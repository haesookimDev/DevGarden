import os
import shutil
import tempfile
from pathlib import Path

from git import Repo

# Files to prioritize during analysis
KEY_FILES = [
    "README.md", "readme.md", "README.rst",
    "package.json", "pyproject.toml", "Cargo.toml", "go.mod", "pom.xml", "build.gradle",
    "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
    "Makefile", "CMakeLists.txt",
    ".env.example",
]

# File extensions to analyze
CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".kt",
    ".c", ".cpp", ".h", ".hpp", ".cs", ".rb", ".php", ".swift", ".scala",
}

IGNORE_DIRS = {
    "node_modules", ".git", "__pycache__", ".next", "dist", "build",
    "target", ".venv", "venv", "vendor", ".idea", ".vscode",
}

MAX_FILE_SIZE = 50_000  # 50KB per file
MAX_TOTAL_CONTENT = 200_000  # 200KB total for AI prompt


def clone_repo(repo_url: str, access_token: str | None = None) -> str:
    """Clone a repository and return the path."""
    clone_dir = tempfile.mkdtemp(prefix="devgarden_git_")

    if access_token and "github.com" in repo_url:
        repo_url = repo_url.replace("https://", f"https://{access_token}@")
    elif access_token and "gitlab.com" in repo_url:
        repo_url = repo_url.replace("https://", f"https://oauth2:{access_token}@")

    Repo.clone_from(repo_url, clone_dir, depth=1)
    return clone_dir


def get_directory_tree(repo_path: str, max_depth: int = 3) -> str:
    """Generate a directory tree string."""
    lines = []
    root = Path(repo_path)

    def _walk(path: Path, prefix: str, depth: int):
        if depth > max_depth:
            return
        entries = sorted(path.iterdir(), key=lambda e: (not e.is_dir(), e.name))
        entries = [e for e in entries if e.name not in IGNORE_DIRS and not e.name.startswith(".")]

        for i, entry in enumerate(entries[:30]):  # Limit entries
            connector = "└── " if i == len(entries) - 1 else "├── "
            lines.append(f"{prefix}{connector}{entry.name}")
            if entry.is_dir():
                extension = "    " if i == len(entries) - 1 else "│   "
                _walk(entry, prefix + extension, depth + 1)

    _walk(root, "", 0)
    return "\n".join(lines)


def find_key_files(repo_path: str) -> dict[str, str]:
    """Find and read key project files."""
    result = {}
    root = Path(repo_path)

    # Read known key files
    for filename in KEY_FILES:
        filepath = root / filename
        if filepath.exists() and filepath.stat().st_size < MAX_FILE_SIZE:
            result[filename] = filepath.read_text(errors="ignore")

    return result


def analyze_code_files(repo_path: str) -> dict[str, str]:
    """Analyze source code files and return interesting ones."""
    result = {}
    total_size = 0
    root = Path(repo_path)

    # Collect all code files
    code_files = []
    for ext in CODE_EXTENSIONS:
        code_files.extend(root.rglob(f"*{ext}"))

    # Filter and sort by size (prefer smaller, more focused files)
    code_files = [
        f for f in code_files
        if not any(part in IGNORE_DIRS for part in f.parts)
        and f.stat().st_size < MAX_FILE_SIZE
    ]
    code_files.sort(key=lambda f: f.stat().st_size)

    for filepath in code_files[:20]:  # Limit to 20 files
        content = filepath.read_text(errors="ignore")
        if total_size + len(content) > MAX_TOTAL_CONTENT:
            break
        relative = str(filepath.relative_to(root))
        result[relative] = content
        total_size += len(content)

    return result


def detect_languages(repo_path: str) -> dict[str, int]:
    """Detect programming languages by file count."""
    lang_map = {
        ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript", ".tsx": "TypeScript",
        ".jsx": "JavaScript", ".go": "Go", ".rs": "Rust", ".java": "Java",
        ".kt": "Kotlin", ".rb": "Ruby", ".php": "PHP", ".swift": "Swift",
        ".c": "C", ".cpp": "C++", ".cs": "C#", ".scala": "Scala",
    }
    counts: dict[str, int] = {}
    root = Path(repo_path)

    for ext, lang in lang_map.items():
        files = [f for f in root.rglob(f"*{ext}") if not any(p in IGNORE_DIRS for p in f.parts)]
        if files:
            counts[lang] = counts.get(lang, 0) + len(files)

    return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))


def get_dependencies(key_files: dict[str, str]) -> str:
    """Extract dependency information from key files."""
    parts = []
    if "package.json" in key_files:
        parts.append(f"package.json:\n{key_files['package.json']}")
    if "pyproject.toml" in key_files:
        parts.append(f"pyproject.toml:\n{key_files['pyproject.toml']}")
    if "Cargo.toml" in key_files:
        parts.append(f"Cargo.toml:\n{key_files['Cargo.toml']}")
    if "go.mod" in key_files:
        parts.append(f"go.mod:\n{key_files['go.mod']}")
    return "\n---\n".join(parts) if parts else "No dependency files found"


def cleanup_clone(clone_dir: str):
    """Remove cloned repository."""
    shutil.rmtree(clone_dir, ignore_errors=True)


def analyze_repository(repo_url: str, access_token: str | None = None) -> dict:
    """Full repository analysis pipeline."""
    clone_dir = clone_repo(repo_url, access_token)
    try:
        key_files = find_key_files(clone_dir)
        code_files = analyze_code_files(clone_dir)
        languages = detect_languages(clone_dir)
        tree = get_directory_tree(clone_dir)
        dependencies = get_dependencies(key_files)
        total_files = sum(1 for _ in Path(clone_dir).rglob("*") if _.is_file())

        return {
            "repo_url": repo_url,
            "readme": key_files.get("README.md", key_files.get("readme.md", "No README found")),
            "tree": tree,
            "key_files": "\n---\n".join(f"### {k}\n```\n{v}\n```" for k, v in list(code_files.items())[:10]),
            "dependencies": dependencies,
            "total_files": total_files,
            "languages": ", ".join(f"{lang} ({count})" for lang, count in languages.items()),
        }
    finally:
        cleanup_clone(clone_dir)
