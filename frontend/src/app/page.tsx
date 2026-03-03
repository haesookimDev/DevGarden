"use client";

import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import { api, Post } from "@/lib/api";
import { cn, formatDate, getCategoryColor, getCategoryLabel, truncate } from "@/lib/utils";
import { ArrowRight, Code2, FileText, GitBranch, Sparkles } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

export default function HomePage() {
  const [recentPosts, setRecentPosts] = useState<Post[]>([]);

  useEffect(() => {
    api.getPosts({ per_page: 3 }).then((res) => setRecentPosts(res.posts)).catch(() => {});
  }, []);

  return (
    <div>
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-[var(--color-bg-secondary)]">
        <div className="mx-auto max-w-6xl px-4 py-24 md:py-32">
          <div className="flex flex-col items-center text-center">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-[var(--color-accent-light)] px-4 py-1.5 text-sm font-medium text-[var(--color-accent)]">
              <Code2 size={16} />
              Developer Portfolio & Blog
            </div>
            <h1 className="mb-6 text-4xl font-bold tracking-tight md:text-6xl">
              Build. Learn.{" "}
              <span className="text-[var(--color-accent)]">Share.</span>
            </h1>
            <p className="mb-8 max-w-2xl text-lg text-[var(--color-text-secondary)]">
              기술 블로그와 포트폴리오를 한곳에서 관리하세요.
              AI가 문서와 코드를 분석하여 기술 블로그를 자동으로 작성합니다.
            </p>
            <div className="flex gap-4">
              <Link href="/blog">
                <Button size="lg">
                  블로그 보기
                  <ArrowRight size={18} className="ml-2" />
                </Button>
              </Link>
              <Link href="/generate">
                <Button variant="secondary" size="lg">AI 블로그 생성</Button>
              </Link>
            </div>
          </div>
        </div>
        <div className="absolute -top-40 right-0 h-80 w-80 rounded-full bg-[var(--color-accent)]/5 blur-3xl" />
        <div className="absolute -bottom-40 left-0 h-80 w-80 rounded-full bg-[var(--color-accent)]/5 blur-3xl" />
      </section>

      {/* Features */}
      <section className="mx-auto max-w-6xl px-4 py-20">
        <h2 className="mb-12 text-center text-2xl font-bold md:text-3xl">
          AI-Powered Blog Generation
        </h2>
        <div className="grid gap-6 md:grid-cols-3">
          <Card className="text-center">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-blue-50">
              <FileText size={24} className="text-blue-600" />
            </div>
            <h3 className="mb-2 font-bold">Document Upload</h3>
            <p className="text-sm text-[var(--color-text-secondary)]">
              PDF, DOCX, PPTX 파일을 업로드하면 AI가 분석하여 기술 블로그를 자동으로 작성합니다.
            </p>
          </Card>
          <Card className="text-center">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-50">
              <GitBranch size={24} className="text-emerald-600" />
            </div>
            <h3 className="mb-2 font-bold">Git Analysis</h3>
            <p className="text-sm text-[var(--color-text-secondary)]">
              GitHub/GitLab 레포지토리를 분석하여 프로젝트의 기술 스택과 아키텍처를 정리합니다.
            </p>
          </Card>
          <Card className="text-center">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-violet-50">
              <Sparkles size={24} className="text-violet-600" />
            </div>
            <h3 className="mb-2 font-bold">Multi AI Support</h3>
            <p className="text-sm text-[var(--color-text-secondary)]">
              Claude, GPT, Gemini 등 다양한 AI 모델을 선택하여 사용할 수 있습니다.
            </p>
          </Card>
        </div>
      </section>

      {/* Recent Posts */}
      {recentPosts.length > 0 && (
        <section className="bg-[var(--color-bg-secondary)] py-20">
          <div className="mx-auto max-w-6xl px-4">
            <div className="mb-8 flex items-center justify-between">
              <h2 className="text-2xl font-bold">Recent Posts</h2>
              <Link
                href="/blog"
                className="flex items-center gap-1 text-sm font-medium text-[var(--color-accent)] hover:underline"
              >
                View All <ArrowRight size={16} />
              </Link>
            </div>
            <div className="grid gap-6 md:grid-cols-3">
              {recentPosts.map((post) => (
                <Link key={post.id} href={`/blog/${post.slug}`}>
                  <Card>
                    {post.cover_image_url && (
                      <img
                        src={post.cover_image_url}
                        alt={post.title}
                        className="mb-4 h-40 w-full rounded-lg object-cover"
                      />
                    )}
                    <div className="mb-2 flex items-center gap-2">
                      <span className={cn("rounded-full px-2.5 py-0.5 text-xs font-medium", getCategoryColor(post.category))}>
                        {getCategoryLabel(post.category)}
                      </span>
                      <span className="text-xs text-[var(--color-text-tertiary)]">
                        {formatDate(post.created_at)}
                      </span>
                    </div>
                    <h3 className="mb-2 font-bold leading-snug">{post.title}</h3>
                    <p className="text-sm text-[var(--color-text-secondary)]">
                      {truncate(post.excerpt || "", 120)}
                    </p>
                  </Card>
                </Link>
              ))}
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
