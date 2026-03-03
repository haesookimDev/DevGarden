"use client";

import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import Input from "@/components/ui/Input";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/authStore";
import { FileText, GitBranch, Loader2, Upload } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

type TabType = "document" | "git";

export default function GeneratePage() {
  const router = useRouter();
  const { user } = useAuthStore();
  const [activeTab, setActiveTab] = useState<TabType>("document");
  const [generating, setGenerating] = useState(false);
  const [streamContent, setStreamContent] = useState("");
  const [error, setError] = useState("");

  // Document tab
  const [file, setFile] = useState<File | null>(null);
  const [language, setLanguage] = useState("ko");

  // Git tab
  const [repoUrl, setRepoUrl] = useState("");
  const [accessToken, setAccessToken] = useState("");

  if (!user) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-20 text-center">
        <p className="mb-4 text-[var(--color-text-secondary)]">Please sign in to use AI generation.</p>
        <Link href="/auth/login"><Button>Sign In</Button></Link>
      </div>
    );
  }

  const handleDocumentGenerate = async () => {
    if (!file) return;
    setGenerating(true);
    setStreamContent("");
    setError("");

    try {
      const uploadResult = await api.uploadDocument(file);
      const task = await api.generateFromDocument(uploadResult.path, language);

      api.streamGeneration(
        task.id,
        (chunk) => setStreamContent((prev) => prev + chunk),
        (postId) => {
          setGenerating(false);
          if (postId) router.push(`/blog/editor?id=${postId}`);
        },
        (msg) => {
          setError(msg);
          setGenerating(false);
        }
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Generation failed");
      setGenerating(false);
    }
  };

  const handleGitGenerate = async () => {
    if (!repoUrl) return;
    setGenerating(true);
    setStreamContent("");
    setError("");

    try {
      const task = await api.generateFromGit(repoUrl, accessToken || undefined, language);

      api.streamGeneration(
        task.id,
        (chunk) => setStreamContent((prev) => prev + chunk),
        (postId) => {
          setGenerating(false);
          if (postId) router.push(`/blog/editor?id=${postId}`);
        },
        (msg) => {
          setError(msg);
          setGenerating(false);
        }
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Generation failed");
      setGenerating(false);
    }
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) setFile(droppedFile);
  }, []);

  return (
    <div className="mx-auto max-w-4xl px-4 py-12">
      <h1 className="mb-2 text-3xl font-bold">AI Blog Generator</h1>
      <p className="mb-8 text-[var(--color-text-secondary)]">
        Upload documents or provide a Git repository URL to auto-generate blog posts.
      </p>

      {/* Tabs */}
      <div className="mb-6 flex gap-1">
        <button
          onClick={() => setActiveTab("document")}
          className={cn(
            "flex items-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium transition-colors",
            activeTab === "document" ? "bg-[var(--color-accent)] text-white" : "text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-tertiary)]"
          )}
        >
          <FileText size={16} /> Document Upload
        </button>
        <button
          onClick={() => setActiveTab("git")}
          className={cn(
            "flex items-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium transition-colors",
            activeTab === "git" ? "bg-[var(--color-accent)] text-white" : "text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-tertiary)]"
          )}
        >
          <GitBranch size={16} /> Git Repository
        </button>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Input Panel */}
        <Card hover={false}>
          {activeTab === "document" ? (
            <div className="space-y-4">
              <h3 className="font-bold">Upload Document</h3>
              <div
                onDrop={handleDrop}
                onDragOver={(e) => e.preventDefault()}
                className="flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-gray-200 p-8 text-center hover:border-[var(--color-accent)]"
              >
                <Upload size={32} className="mb-3 text-[var(--color-text-tertiary)]" />
                <p className="mb-1 text-sm font-medium">Drag & drop or click to upload</p>
                <p className="text-xs text-[var(--color-text-tertiary)]">PDF, DOCX, PPTX (max 100MB)</p>
                <input
                  type="file"
                  accept=".pdf,.docx,.pptx"
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                  className="absolute inset-0 cursor-pointer opacity-0"
                  style={{ position: "relative" }}
                />
              </div>
              {file && (
                <p className="text-sm text-[var(--color-accent)]">{file.name}</p>
              )}
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm"
              >
                <option value="ko">Korean</option>
                <option value="en">English</option>
              </select>
              <Button
                className="w-full"
                onClick={handleDocumentGenerate}
                disabled={!file || generating}
              >
                {generating ? <Loader2 size={16} className="mr-2 animate-spin" /> : null}
                Generate Blog Post
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              <h3 className="font-bold">Git Repository</h3>
              <Input
                placeholder="https://github.com/username/repo"
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
              />
              <Input
                placeholder="Access Token (optional, for private repos)"
                type="password"
                value={accessToken}
                onChange={(e) => setAccessToken(e.target.value)}
              />
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm"
              >
                <option value="ko">Korean</option>
                <option value="en">English</option>
              </select>
              <Button
                className="w-full"
                onClick={handleGitGenerate}
                disabled={!repoUrl || generating}
              >
                {generating ? <Loader2 size={16} className="mr-2 animate-spin" /> : null}
                Analyze & Generate
              </Button>
            </div>
          )}

          {error && (
            <div className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-600">{error}</div>
          )}
        </Card>

        {/* Preview Panel */}
        <Card hover={false} className="max-h-[600px] overflow-y-auto">
          <h3 className="mb-4 font-bold">Preview</h3>
          {streamContent ? (
            <div className="prose max-w-none text-sm">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{streamContent}</ReactMarkdown>
            </div>
          ) : (
            <div className="flex h-64 items-center justify-center text-sm text-[var(--color-text-tertiary)]">
              {generating ? (
                <div className="flex items-center gap-2">
                  <Loader2 size={16} className="animate-spin" />
                  Generating...
                </div>
              ) : (
                "Generated content will appear here"
              )}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
