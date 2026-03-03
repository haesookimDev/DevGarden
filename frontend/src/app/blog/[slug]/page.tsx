"use client";

import Button from "@/components/ui/Button";
import { api, Post } from "@/lib/api";
import { cn, formatDate, getCategoryColor, getCategoryLabel } from "@/lib/utils";
import { ArrowLeft, Clock, Eye } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function BlogPostPage() {
  const { slug } = useParams<{ slug: string }>();
  const [post, setPost] = useState<Post | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (slug) {
      api.getPost(slug).then(setPost).catch(() => {}).finally(() => setLoading(false));
    }
  }, [slug]);

  if (loading) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-12">
        <div className="space-y-4">
          <div className="h-8 w-3/4 animate-pulse rounded bg-[var(--color-bg-tertiary)]" />
          <div className="h-4 w-1/2 animate-pulse rounded bg-[var(--color-bg-tertiary)]" />
          <div className="mt-8 h-64 animate-pulse rounded bg-[var(--color-bg-tertiary)]" />
        </div>
      </div>
    );
  }

  if (!post) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-20 text-center">
        <h1 className="mb-4 text-2xl font-bold">Post not found</h1>
        <Link href="/blog">
          <Button variant="secondary">Back to Blog</Button>
        </Link>
      </div>
    );
  }

  return (
    <article className="mx-auto max-w-3xl px-4 py-12">
      {/* Back link */}
      <Link
        href="/blog"
        className="mb-8 inline-flex items-center gap-1 text-sm text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
      >
        <ArrowLeft size={16} />
        Back to Blog
      </Link>

      {/* Header */}
      <header className="mb-8">
        <div className="mb-4 flex flex-wrap items-center gap-3">
          <span className={cn("rounded-full px-3 py-1 text-xs font-medium", getCategoryColor(post.category))}>
            {getCategoryLabel(post.category)}
          </span>
          <span className="flex items-center gap-1 text-sm text-[var(--color-text-secondary)]">
            <Clock size={14} />
            {post.reading_time_min} min read
          </span>
          <span className="flex items-center gap-1 text-sm text-[var(--color-text-secondary)]">
            <Eye size={14} />
            {post.view_count} views
          </span>
        </div>
        <h1 className="mb-4 text-3xl font-bold leading-tight md:text-4xl">{post.title}</h1>
        {post.excerpt && (
          <p className="text-lg text-[var(--color-text-secondary)]">{post.excerpt}</p>
        )}
        <div className="mt-4 text-sm text-[var(--color-text-tertiary)]">
          {formatDate(post.published_at || post.created_at)}
        </div>
      </header>

      {/* Cover image */}
      {post.cover_image_url && (
        <img
          src={post.cover_image_url}
          alt={post.title}
          className="mb-8 w-full rounded-xl object-cover"
        />
      )}

      {/* Content */}
      <div className="prose max-w-none">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {post.content}
        </ReactMarkdown>
      </div>

      {/* Tags */}
      {post.tags && post.tags.length > 0 && (
        <div className="mt-8 border-t border-gray-100 pt-6">
          <div className="flex flex-wrap gap-2">
            {post.tags.map((tag) => (
              <span
                key={tag}
                className="rounded-lg bg-[var(--color-bg-tertiary)] px-3 py-1 text-sm text-[var(--color-text-secondary)]"
              >
                #{tag}
              </span>
            ))}
          </div>
        </div>
      )}
    </article>
  );
}
