"use client";

import Button from "@/components/ui/Button";
import { useAuthStore } from "@/stores/authStore";
import { Briefcase, LogIn } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function PortfolioRedirectPage() {
  const router = useRouter();
  const { user, isLoading } = useAuthStore();

  useEffect(() => {
    if (!isLoading && user) {
      router.replace("/dashboard/portfolio");
    }
  }, [user, isLoading, router]);

  if (isLoading || user) return null;

  return (
    <div className="flex min-h-[60vh] items-center justify-center px-4">
      <div className="text-center">
        <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-[var(--color-bg-tertiary)]">
          <Briefcase size={32} className="text-[var(--color-text-secondary)]" />
        </div>
        <h1 className="mb-2 text-2xl font-bold">Portfolio</h1>
        <p className="mb-6 text-[var(--color-text-secondary)]">
          Sign in to manage your portfolio items.
        </p>
        <Link href="/auth/login">
          <Button>
            <LogIn size={16} className="mr-2" /> Sign In
          </Button>
        </Link>
      </div>
    </div>
  );
}
