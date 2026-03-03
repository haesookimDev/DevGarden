"use client";

import { Code2, Github } from "lucide-react";
import Link from "next/link";

export default function Footer() {
  return (
    <footer className="border-t border-gray-100 bg-[var(--color-bg-secondary)]">
      <div className="mx-auto max-w-6xl px-4 py-12">
        <div className="flex flex-col items-center gap-4 md:flex-row md:justify-between">
          <div className="flex items-center gap-2">
            <Code2 size={20} className="text-[var(--color-accent)]" />
            <span className="font-bold">DevLog</span>
          </div>
          <nav className="flex gap-6 text-sm text-[var(--color-text-secondary)]">
            <Link href="/blog" className="hover:text-[var(--color-text-primary)]">Blog</Link>
            <Link href="/portfolio" className="hover:text-[var(--color-text-primary)]">Portfolio</Link>
          </nav>
          <p className="text-sm text-[var(--color-text-tertiary)]">
            &copy; {new Date().getFullYear()} DevLog. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
