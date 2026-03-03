"use client";

import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import { api, Post } from "@/lib/api";
import { cn, formatDate, getCategoryColor, getCategoryLabel, truncate } from "@/lib/utils";
import { useAuthStore } from "@/stores/authStore";
import { ArrowRight, Briefcase, Edit3, Eye, FileText, PenSquare, Plus, Sparkles, Trash2 } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function DashboardPage() {
  const router = useRouter();
  const { user } = useAuthStore();
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<"all" | "draft" | "published">("all");

  useEffect(() => {
    if (!user) {
      router.push("/auth/login");
      return;
    }
    loadPosts();
  }, [user, router]);

  const loadPosts = () => {
    setLoading(true);
    api
      .getMyPosts()
      .then(setPosts)
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this post?")) return;
    try {
      await api.deletePost(id);
      loadPosts();
    } catch {
      alert("Failed to delete post");
    }
  };

  if (!user) return null;

  const filteredPosts = filter === "all" ? posts : posts.filter((p) => p.status === filter);
  const draftCount = posts.filter((p) => p.status === "draft").length;
  const publishedCount = posts.filter((p) => p.status === "published").length;

  return (
    <div className="mx-auto max-w-6xl px-4 py-12">
      {/* Welcome */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="mt-1 text-[var(--color-text-secondary)]">
          Welcome back, {user.name}
        </p>
      </div>

      {/* Quick Actions */}
      <div className="mb-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Link href="/blog/editor">
          <Card className="flex items-center gap-3 transition-all hover:border-[var(--color-accent)]">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-50">
              <PenSquare size={20} className="text-blue-600" />
            </div>
            <div>
              <p className="text-sm font-semibold">New Post</p>
              <p className="text-xs text-[var(--color-text-tertiary)]">Write a blog post</p>
            </div>
          </Card>
        </Link>
        <Link href="/generate">
          <Card className="flex items-center gap-3 transition-all hover:border-[var(--color-accent)]">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-violet-50">
              <Sparkles size={20} className="text-violet-600" />
            </div>
            <div>
              <p className="text-sm font-semibold">AI Generate</p>
              <p className="text-xs text-[var(--color-text-tertiary)]">Auto-generate from docs</p>
            </div>
          </Card>
        </Link>
        <Link href="/dashboard/portfolio">
          <Card className="flex items-center gap-3 transition-all hover:border-[var(--color-accent)]">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-50">
              <Briefcase size={20} className="text-emerald-600" />
            </div>
            <div>
              <p className="text-sm font-semibold">Portfolio</p>
              <p className="text-xs text-[var(--color-text-tertiary)]">Manage your portfolio</p>
            </div>
          </Card>
        </Link>
        <Link href="/settings">
          <Card className="flex items-center gap-3 transition-all hover:border-[var(--color-accent)]">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-amber-50">
              <FileText size={20} className="text-amber-600" />
            </div>
            <div>
              <p className="text-sm font-semibold">Settings</p>
              <p className="text-xs text-[var(--color-text-tertiary)]">AI models & profile</p>
            </div>
          </Card>
        </Link>
      </div>

      {/* My Posts */}
      <div className="mb-6 flex items-center justify-between">
        <h2 className="text-xl font-bold">My Posts</h2>
        <Link href="/blog/editor">
          <Button size="sm">
            <Plus size={16} className="mr-1" /> New Post
          </Button>
        </Link>
      </div>

      {/* Filter Tabs */}
      <div className="mb-6 flex gap-1">
        {[
          { value: "all" as const, label: `All (${posts.length})` },
          { value: "draft" as const, label: `Drafts (${draftCount})` },
          { value: "published" as const, label: `Published (${publishedCount})` },
        ].map((tab) => (
          <button
            key={tab.value}
            onClick={() => setFilter(tab.value)}
            className={cn(
              "rounded-lg px-4 py-2 text-sm font-medium transition-colors",
              filter === tab.value
                ? "bg-[var(--color-accent)] text-white"
                : "text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-tertiary)]"
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Posts List */}
      {loading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-24 animate-pulse rounded-xl bg-[var(--color-bg-tertiary)]" />
          ))}
        </div>
      ) : filteredPosts.length === 0 ? (
        <div className="py-20 text-center">
          <p className="text-[var(--color-text-secondary)]">
            {filter === "all" ? "No posts yet. Start writing!" : `No ${filter} posts.`}
          </p>
          <Link href="/blog/editor" className="mt-4 inline-block">
            <Button variant="secondary">
              <PenSquare size={16} className="mr-1" /> Write your first post
            </Button>
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredPosts.map((post) => (
            <div
              key={post.id}
              className="flex items-center justify-between rounded-xl border border-gray-100 bg-white p-4 transition-all hover:border-gray-200 hover:shadow-sm"
            >
              <div className="min-w-0 flex-1">
                <div className="mb-1 flex items-center gap-2">
                  <span
                    className={cn(
                      "rounded-full px-2 py-0.5 text-xs font-medium",
                      post.status === "published"
                        ? "bg-emerald-100 text-emerald-700"
                        : "bg-gray-100 text-gray-600"
                    )}
                  >
                    {post.status}
                  </span>
                  {post.category && (
                    <span className={cn("rounded-full px-2 py-0.5 text-xs font-medium", getCategoryColor(post.category))}>
                      {getCategoryLabel(post.category)}
                    </span>
                  )}
                  <span className="text-xs text-[var(--color-text-tertiary)]">
                    {formatDate(post.updated_at)}
                  </span>
                </div>
                <h3 className="font-semibold truncate">{post.title}</h3>
                {post.excerpt && (
                  <p className="mt-0.5 text-sm text-[var(--color-text-secondary)] truncate">
                    {truncate(post.excerpt, 100)}
                  </p>
                )}
              </div>
              <div className="ml-4 flex items-center gap-1">
                {post.status === "published" && (
                  <Link
                    href={`/blog/${post.slug}`}
                    className="rounded-lg p-2 text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-tertiary)]"
                    title="View"
                  >
                    <Eye size={16} />
                  </Link>
                )}
                <Link
                  href={`/blog/editor?id=${post.id}`}
                  className="rounded-lg p-2 text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-tertiary)]"
                  title="Edit"
                >
                  <Edit3 size={16} />
                </Link>
                <button
                  onClick={() => handleDelete(post.id)}
                  className="rounded-lg p-2 text-[var(--color-text-secondary)] hover:bg-red-50 hover:text-red-500"
                  title="Delete"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
