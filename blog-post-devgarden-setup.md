# DevGarden: AI 기반 기술 블로그 플랫폼 구축기

## Overview

개인 기술 블로그와 포트폴리오를 통합 관리하면서, AI를 활용해 문서/코드 분석 기반 블로그 자동 생성까지 지원하는 풀스택 플랫폼 "DevGarden"을 구축했다. 핵심 차별점은 PDF/DOCX/PPTX 업로드 또는 GitHub/GitLab URL 입력만으로 기술 블로그 초안을 자동으로 생성하는 에이전틱 AI 기능이다.

## Technical Implementation

### 아키텍처 설계

7개의 Docker Compose 서비스로 구성된 마이크로서비스 아키텍처를 채택했다:

```
Nginx (Reverse Proxy) → Frontend (Next.js) + Backend (FastAPI)
                          ↓
        PostgreSQL / MinIO / Redis / Celery Worker
```

**프론트엔드-백엔드 분리 이유**: SEO를 위한 SSR/SSG가 필요한 블로그 특성상 Next.js App Router를 사용하고, AI 처리와 비동기 작업이 많은 백엔드는 Python FastAPI로 분리했다. 이 구조는 추후 멀티 유저 플랫폼으로 확장 시에도 각각 독립적으로 스케일링이 가능하다.

### AI Provider 추상화 레이어

여러 AI 모델을 통합 지원하기 위해 Strategy 패턴 기반의 추상화 계층을 설계했다:

```python
class AIProvider(ABC):
    @abstractmethod
    async def generate(self, system_prompt, user_prompt, max_tokens) -> AIMessage: ...

    @abstractmethod
    async def generate_stream(self, system_prompt, user_prompt, max_tokens) -> AsyncIterator[str]: ...
```

`AIProviderFactory`가 사용자 설정에 따라 Claude, OpenAI, Google Gemini, 또는 OpenAI-compatible 커스텀 모델 인스턴스를 생성한다. Private 모델은 OpenAI provider를 상속받아 `base_url`만 변경하는 방식으로 구현했다.

### 문서 파싱 파이프라인

3가지 문서 타입 각각에 최적화된 파서를 구현했다:

- **PDF**: PyMuPDF (fitz) - 텍스트와 이미지를 페이지 단위로 추출
- **DOCX**: python-docx - 본문, 테이블, 임베디드 이미지 추출
- **PPTX**: python-pptx - 슬라이드 텍스트, 스피커 노트, 이미지 추출

모든 파서는 `DocumentParser` 추상 클래스를 구현하며 `ParsedDocument` 데이터클래스를 반환한다.

### Git 레포지토리 분석

Git 분석 파이프라인은 보안과 효율성을 모두 고려했다:

1. **Shallow Clone** (depth=1): 전체 히스토리 없이 최신 스냅샷만 클론
2. **핵심 파일 자동 감지**: README, package.json, pyproject.toml 등 프로젝트 정의 파일 우선 분석
3. **언어 감지**: 파일 확장자 기반 프로그래밍 언어 통계
4. **총 콘텐츠 제한**: AI 프롬프트 크기를 200KB 이내로 제한
5. **자동 정리**: 분석 완료 후 클론 디렉토리 삭제

### 실시간 스트리밍 (SSE)

AI 생성 결과를 실시간으로 프론트엔드에 전달하기 위해 Server-Sent Events를 구현했다. Celery 워커가 AI API의 스트리밍 응답을 받으면 Redis Pub/Sub을 통해 FastAPI의 SSE 엔드포인트로 전달하고, 프론트엔드의 EventSource가 이를 수신하여 실시간으로 렌더링한다.

```
Celery Worker → Redis Pub/Sub → FastAPI SSE → Frontend EventSource
```

### 데이터베이스 설계

PostgreSQL의 `ARRAY` 타입을 활용해 tags, tech_stack 같은 다중 값 필드를 별도 조인 테이블 없이 처리했다. `generation_tasks` 테이블의 `JSONB` 타입으로 각 생성 타입별 입력 데이터를 유연하게 저장한다.

### 프론트엔드 UI/UX

- **디자인 시스템**: 흰색 배경 기반, 파란색 악센트, Inter + JetBrains Mono 폰트
- **하이브리드 에디터**: Markdown 직접 입력 모드와 실시간 미리보기 모드 전환
- **반응형**: 모바일 햄버거 메뉴, 태블릿 2열, 데스크톱 3열 그리드
- **상태 관리**: Zustand로 최소한의 전역 상태 (인증 정보)만 관리

## Challenges & Solutions

### 문제 1: npm 캐시 권한 오류

root 소유의 npm 캐시 파일로 인해 패키지 설치가 불가능했다. Docker 빌드 환경에서는 문제가 없으므로, package.json에 의존성을 직접 명시하고 Docker 빌드 시 자동 설치되도록 처리했다.

### 문제 2: AI 프롬프트 크기 관리

대용량 문서나 대규모 레포지토리 분석 시 AI 프롬프트가 컨텍스트 윈도우를 초과할 수 있다. 문서는 100KB, Git 레포는 총 200KB로 콘텐츠를 제한하고, 핵심 파일을 우선 선택하는 휴리스틱을 적용했다.

### 문제 3: 멀티 프로바이더 API 호환성

각 AI 프로바이더마다 API 인터페이스가 다르다. 추상 클래스로 통합 인터페이스를 정의하고, 특히 Private 모델은 OpenAI-compatible API를 가정하여 OpenAI provider를 상속받는 방식으로 해결했다.

## Key Takeaways

1. **MVP 우선 접근이 효과적**: 인프라 → CRUD → 포트폴리오 → AI 기능 순서로 단계적 구현이 복잡한 시스템에서 리스크를 줄인다
2. **Docker Compose는 개발 생산성의 핵심**: 7개 서비스를 단일 명령으로 관리할 수 있어 개발 환경 셋업이 간단하다
3. **AI 추상화 레이어의 가치**: 새로운 AI 프로바이더 추가 시 하나의 클래스만 구현하면 되므로 확장성이 뛰어나다
4. **SSE > WebSocket for AI streaming**: 단방향 실시간 통신에는 SSE가 WebSocket보다 구현이 간단하고 인프라 호환성이 높다
5. **PostgreSQL ARRAY/JSONB 활용**: NoSQL 수준의 유연성을 관계형 DB에서 달성할 수 있어 스키마 설계가 단순해진다

---

# DevGarden: Building an AI-Powered Technical Blog Platform

## Overview

Built "DevGarden," a full-stack platform that integrates a personal technical blog and portfolio with AI-powered automatic blog generation from document/code analysis. The core differentiator is the agentic AI capability that auto-generates technical blog drafts from PDF/DOCX/PPTX uploads or GitHub/GitLab repository URLs.

## Technical Implementation

### Architecture Design

Adopted a microservice architecture with 7 Docker Compose services:

```
Nginx (Reverse Proxy) → Frontend (Next.js) + Backend (FastAPI)
                          ↓
        PostgreSQL / MinIO / Redis / Celery Worker
```

**Why separate frontend and backend**: Blog content needs SSR/SSG for SEO (Next.js App Router), while the backend requires Python's rich AI/ML ecosystem for heavy async processing (FastAPI). This structure also enables independent scaling when expanding to a multi-user platform.

### AI Provider Abstraction Layer

Designed a Strategy pattern-based abstraction layer for unified multi-model support:

```python
class AIProvider(ABC):
    @abstractmethod
    async def generate(self, system_prompt, user_prompt, max_tokens) -> AIMessage: ...

    @abstractmethod
    async def generate_stream(self, system_prompt, user_prompt, max_tokens) -> AsyncIterator[str]: ...
```

`AIProviderFactory` creates Claude, OpenAI, Google Gemini, or custom OpenAI-compatible model instances based on user settings. Private models inherit from the OpenAI provider, only changing the `base_url`.

### Document Parsing Pipeline

Implemented optimized parsers for each document type:

- **PDF**: PyMuPDF (fitz) - page-by-page text and image extraction
- **DOCX**: python-docx - body text, tables, and embedded images
- **PPTX**: python-pptx - slide text, speaker notes, and images

All parsers implement the `DocumentParser` abstract class and return a `ParsedDocument` dataclass.

### Git Repository Analysis

The Git analysis pipeline balances security and efficiency:

1. **Shallow Clone** (depth=1): Only the latest snapshot, no full history
2. **Key File Auto-Detection**: Priority analysis of README, package.json, pyproject.toml, etc.
3. **Language Detection**: File extension-based programming language statistics
4. **Content Size Limits**: Total AI prompt content capped at 200KB
5. **Auto-Cleanup**: Clone directory deleted after analysis

### Real-time Streaming (SSE)

Implemented Server-Sent Events for real-time AI generation feedback. Celery workers receive streaming responses from AI APIs, publish via Redis Pub/Sub to FastAPI SSE endpoints, and the frontend's EventSource renders content in real-time.

### Database Design

Leveraged PostgreSQL's `ARRAY` type for multi-value fields like tags and tech_stack without separate join tables. `JSONB` type in `generation_tasks` flexibly stores input data for each generation type.

### Frontend UI/UX

- **Design System**: White background, blue accent, Inter + JetBrains Mono fonts
- **Hybrid Editor**: Toggle between raw Markdown input and live preview modes
- **Responsive**: Mobile hamburger menu, tablet 2-column, desktop 3-column grid
- **State Management**: Zustand for minimal global state (auth only)

## Challenges & Solutions

### Problem 1: npm Cache Permission Errors
Root-owned npm cache files prevented package installation. Since Docker builds don't have this issue, dependencies were directly specified in package.json for automatic installation during Docker build.

### Problem 2: AI Prompt Size Management
Large documents or repositories could exceed AI context windows. Applied content limits (100KB for documents, 200KB for repos) with heuristics for prioritizing key files.

### Problem 3: Multi-Provider API Compatibility
Each AI provider has different API interfaces. Unified through an abstract class, with Private models inheriting the OpenAI provider (assuming OpenAI-compatible APIs).

## Key Takeaways

1. **MVP-first approach works**: Infrastructure → CRUD → Portfolio → AI features reduces risk in complex systems
2. **Docker Compose is a productivity multiplier**: Managing 7 services with a single command simplifies dev environment setup
3. **AI abstraction layer pays off**: Adding a new AI provider requires implementing just one class
4. **SSE > WebSocket for AI streaming**: SSE is simpler and more infrastructure-compatible for unidirectional real-time communication
5. **PostgreSQL ARRAY/JSONB**: Achieves NoSQL-level flexibility within a relational database, simplifying schema design
