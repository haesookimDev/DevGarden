const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiClient {
  private token: string | null = null;

  setToken(token: string | null) {
    this.token = token;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...((options.headers as Record<string, string>) || {}),
    };

    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }

    const res = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(error.detail || "API request failed");
    }

    if (res.status === 204) return undefined as T;
    return res.json();
  }

  // Auth
  async googleAuth(credential: string) {
    return this.request<{
      access_token: string;
      refresh_token: string;
      user: User;
    }>("/api/v1/auth/google", {
      method: "POST",
      body: JSON.stringify({ credential }),
    });
  }

  async getMe() {
    return this.request<User>("/api/v1/auth/me");
  }

  // Posts
  async getPosts(params?: {
    category?: string;
    search?: string;
    page?: number;
    per_page?: number;
  }) {
    const query = new URLSearchParams();
    if (params?.category) query.set("category", params.category);
    if (params?.search) query.set("search", params.search);
    if (params?.page) query.set("page", String(params.page));
    if (params?.per_page) query.set("per_page", String(params.per_page));
    return this.request<PostListResponse>(
      `/api/v1/posts?${query.toString()}`
    );
  }

  async getPost(slug: string) {
    return this.request<Post>(`/api/v1/posts/${slug}`);
  }

  async createPost(data: PostCreate) {
    return this.request<Post>("/api/v1/posts", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async updatePost(id: string, data: Partial<PostCreate>) {
    return this.request<Post>(`/api/v1/posts/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async deletePost(id: string) {
    return this.request<void>(`/api/v1/posts/${id}`, { method: "DELETE" });
  }

  async publishPost(id: string) {
    return this.request<Post>(`/api/v1/posts/${id}/publish`, {
      method: "POST",
    });
  }

  // Portfolio
  async getPortfolioItems(type?: string) {
    const query = type ? `?type=${type}` : "";
    return this.request<PortfolioItem[]>(`/api/v1/portfolio${query}`);
  }

  async createPortfolioItem(data: PortfolioItemCreate) {
    return this.request<PortfolioItem>("/api/v1/portfolio", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async updatePortfolioItem(id: string, data: Partial<PortfolioItemCreate>) {
    return this.request<PortfolioItem>(`/api/v1/portfolio/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async deletePortfolioItem(id: string) {
    return this.request<void>(`/api/v1/portfolio/${id}`, { method: "DELETE" });
  }

  // Upload
  async uploadImage(file: File) {
    const formData = new FormData();
    formData.append("file", file);
    const headers: Record<string, string> = {};
    if (this.token) headers["Authorization"] = `Bearer ${this.token}`;

    const res = await fetch(`${API_BASE}/api/v1/upload/image`, {
      method: "POST",
      headers,
      body: formData,
    });
    return res.json();
  }

  async uploadDocument(file: File) {
    const formData = new FormData();
    formData.append("file", file);
    const headers: Record<string, string> = {};
    if (this.token) headers["Authorization"] = `Bearer ${this.token}`;

    const res = await fetch(`${API_BASE}/api/v1/upload/document`, {
      method: "POST",
      headers,
      body: formData,
    });
    return res.json();
  }

  // AI Generation
  async generateFromDocument(fileUrl: string, language = "ko") {
    return this.request<GenerationTask>("/api/v1/generate/from-document", {
      method: "POST",
      body: JSON.stringify({ file_url: fileUrl, language }),
    });
  }

  async generateFromGit(
    repoUrl: string,
    accessToken?: string,
    language = "ko"
  ) {
    return this.request<GenerationTask>("/api/v1/generate/from-git", {
      method: "POST",
      body: JSON.stringify({
        repo_url: repoUrl,
        access_token: accessToken,
        language,
      }),
    });
  }

  async generateFromPortfolio(portfolioItemId: string, language = "ko") {
    return this.request<GenerationTask>("/api/v1/generate/from-portfolio", {
      method: "POST",
      body: JSON.stringify({ portfolio_item_id: portfolioItemId, language }),
    });
  }

  async getTaskStatus(taskId: string) {
    return this.request<GenerationTask>(
      `/api/v1/generate/status/${taskId}`
    );
  }

  streamGeneration(taskId: string, onChunk: (text: string) => void, onDone: (postId?: string) => void, onError: (msg: string) => void) {
    const url = `${API_BASE}/api/v1/generate/stream/${taskId}`;
    const eventSource = new EventSource(url);

    eventSource.addEventListener("chunk", (e) => onChunk(e.data));
    eventSource.addEventListener("done", (e) => {
      const data = JSON.parse(e.data);
      onDone(data.post_id);
      eventSource.close();
    });
    eventSource.addEventListener("error", (e) => {
      onError((e as MessageEvent).data || "Stream error");
      eventSource.close();
    });
    eventSource.onerror = () => {
      eventSource.close();
    };

    return eventSource;
  }

  // Settings
  async getAIConfigs() {
    return this.request<AIConfig[]>("/api/v1/settings/ai");
  }

  async createAIConfig(data: AIConfigCreate) {
    return this.request<AIConfig>("/api/v1/settings/ai", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async updateAIConfig(id: string, data: Partial<AIConfigCreate>) {
    return this.request<AIConfig>(`/api/v1/settings/ai/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async deleteAIConfig(id: string) {
    return this.request<void>(`/api/v1/settings/ai/${id}`, {
      method: "DELETE",
    });
  }

  async updateProfile(data: { name?: string; bio?: string; github_url?: string }) {
    return this.request<User>("/api/v1/settings/profile", {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }
}

export const api = new ApiClient();

// Types
export interface User {
  id: string;
  email: string;
  name: string;
  avatar_url: string | null;
  bio: string | null;
  github_url: string | null;
  is_admin: boolean;
  created_at: string;
}

export interface Post {
  id: string;
  user_id: string;
  title: string;
  slug: string;
  content: string;
  excerpt: string | null;
  cover_image_url: string | null;
  category: string | null;
  tags: string[] | null;
  status: string;
  source_type: string | null;
  reading_time_min: number | null;
  view_count: number;
  created_at: string;
  updated_at: string;
  published_at: string | null;
}

export interface PostCreate {
  title: string;
  content: string;
  excerpt?: string;
  cover_image_url?: string;
  category?: string;
  tags?: string[];
}

export interface PostListResponse {
  posts: Post[];
  total: number;
  page: number;
  per_page: number;
}

export interface PortfolioItem {
  id: string;
  user_id: string;
  type: string;
  title: string;
  description: string | null;
  tech_stack: string[] | null;
  start_date: string | null;
  end_date: string | null;
  organization: string | null;
  role: string | null;
  source_url: string | null;
  image_urls: string[] | null;
  sort_order: number;
  created_at: string;
  updated_at: string;
}

export interface PortfolioItemCreate {
  type: string;
  title: string;
  description?: string;
  tech_stack?: string[];
  start_date?: string;
  end_date?: string;
  organization?: string;
  role?: string;
  source_url?: string;
  image_urls?: string[];
  sort_order?: number;
}

export interface GenerationTask {
  id: string;
  task_type: string;
  status: string;
  error_message: string | null;
  result_post_id: string | null;
  created_at: string;
  completed_at: string | null;
}

export interface AIConfig {
  id: string;
  provider: string;
  model_name: string | null;
  base_url: string | null;
  is_active: boolean;
  is_default: boolean;
  created_at: string;
}

export interface AIConfigCreate {
  provider: string;
  api_key: string;
  model_name?: string;
  base_url?: string;
  is_default?: boolean;
}
