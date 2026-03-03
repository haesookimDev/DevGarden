"use client";

import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/authStore";
import { ArrowLeft, Eye, Save, Send } from "lucide-react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function BlogEditorPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const postId = searchParams.get("id");
  const { user } = useAuthStore();

  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [excerpt, setExcerpt] = useState("");
  const [category, setCategory] = useState("tech");
  const [tags, setTags] = useState("");
  const [mode, setMode] = useState<"edit" | "preview">("edit");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (postId) {
      api.getPost(postId).then((post) => {
        setTitle(post.title);
        setContent(post.content);
        setExcerpt(post.excerpt || "");
        setCategory(post.category || "tech");
        setTags(post.tags?.join(", ") || "");
      });
    }
  }, [postId]);

  if (!user) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-20 text-center">
        <p className="mb-4 text-[var(--color-text-secondary)]">Please sign in to write posts.</p>
        <Link href="/auth/login"><Button>Sign In</Button></Link>
      </div>
    );
  }

  const handleSave = async (publish = false) => {
    setSaving(true);
    try {
      const data = {
        title,
        content,
        excerpt: excerpt || undefined,
        category,
        tags: tags.split(",").map((t) => t.trim()).filter(Boolean),
      };

      let post;
      if (postId) {
        post = await api.updatePost(postId, data);
      } else {
        post = await api.createPost(data);
      }

      if (publish) {
        await api.publishPost(post.id);
      }

      router.push(`/blog/${post.slug}`);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to save");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      {/* Toolbar */}
      <div className="mb-6 flex items-center justify-between">
        <Link
          href="/blog"
          className="flex items-center gap-1 text-sm text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
        >
          <ArrowLeft size={16} /> Back
        </Link>
        <div className="flex items-center gap-2">
          <div className="flex rounded-lg border border-gray-200">
            <button
              onClick={() => setMode("edit")}
              className={`px-3 py-1.5 text-sm ${mode === "edit" ? "bg-[var(--color-bg-tertiary)] font-medium" : ""}`}
            >
              Edit
            </button>
            <button
              onClick={() => setMode("preview")}
              className={`flex items-center gap-1 px-3 py-1.5 text-sm ${mode === "preview" ? "bg-[var(--color-bg-tertiary)] font-medium" : ""}`}
            >
              <Eye size={14} /> Preview
            </button>
          </div>
          <Button variant="secondary" onClick={() => handleSave(false)} disabled={saving}>
            <Save size={16} className="mr-1" />
            Save Draft
          </Button>
          <Button onClick={() => handleSave(true)} disabled={saving}>
            <Send size={16} className="mr-1" />
            Publish
          </Button>
        </div>
      </div>

      {/* Meta fields */}
      <div className="mb-6 space-y-3">
        <Input
          placeholder="Post title..."
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="text-2xl font-bold border-none px-0 focus:ring-0"
        />
        <Input
          placeholder="Brief excerpt..."
          value={excerpt}
          onChange={(e) => setExcerpt(e.target.value)}
        />
        <div className="flex gap-3">
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="rounded-lg border border-gray-200 px-3 py-2 text-sm"
          >
            <option value="tech">Tech</option>
            <option value="troubleshooting">Troubleshooting</option>
            <option value="project">Project</option>
          </select>
          <Input
            placeholder="Tags (comma separated)"
            value={tags}
            onChange={(e) => setTags(e.target.value)}
            className="flex-1"
          />
        </div>
      </div>

      {/* Editor / Preview */}
      <div className="min-h-[500px] rounded-xl border border-gray-200">
        {mode === "edit" ? (
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Write your post in Markdown..."
            className="h-full min-h-[500px] w-full resize-none rounded-xl p-6 font-mono text-sm focus:outline-none"
          />
        ) : (
          <div className="prose max-w-none p-6">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
}
