"use client";

import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import Input from "@/components/ui/Input";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/authStore";
import { Code2, Github, User as UserIcon } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function RegisterPage() {
  const router = useRouter();
  const { user, setAuth, token } = useAuthStore();

  const [name, setName] = useState("");
  const [bio, setBio] = useState("");
  const [githubUrl, setGithubUrl] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!token) {
      router.replace("/auth/login");
      return;
    }
    if (user) {
      setName(user.name || "");
    }
  }, [user, token, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setSaving(true);
    try {
      const updatedUser = await api.updateProfile({
        name: name.trim(),
        bio: bio.trim() || undefined,
        github_url: githubUrl.trim() || undefined,
      });
      setAuth(token!, updatedUser);
      router.push("/dashboard");
    } catch {
      alert("Failed to save profile. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  if (!token) return null;

  return (
    <div className="flex min-h-[70vh] items-center justify-center px-4">
      <Card hover={false} className="w-full max-w-lg">
        <div className="mb-6 flex justify-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-[var(--color-accent-light)]">
            <Code2 size={32} className="text-[var(--color-accent)]" />
          </div>
        </div>
        <h1 className="mb-2 text-center text-2xl font-bold">Welcome to DevLog!</h1>
        <p className="mb-8 text-center text-sm text-[var(--color-text-secondary)]">
          Set up your profile to get started.
        </p>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="mb-1.5 flex items-center gap-1.5 text-sm font-medium">
              <UserIcon size={14} />
              Name <span className="text-[var(--color-error)]">*</span>
            </label>
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Your display name"
              required
            />
          </div>

          <div>
            <label className="mb-1.5 block text-sm font-medium">Bio</label>
            <textarea
              value={bio}
              onChange={(e) => setBio(e.target.value)}
              placeholder="Tell us about yourself (e.g., Full-stack developer passionate about AI)"
              rows={3}
              className="w-full rounded-lg border border-gray-200 bg-white px-4 py-2.5 text-sm transition-colors placeholder:text-[var(--color-text-tertiary)] focus:border-[var(--color-accent)] focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)]/20"
            />
          </div>

          <div>
            <label className="mb-1.5 flex items-center gap-1.5 text-sm font-medium">
              <Github size={14} />
              GitHub URL
            </label>
            <Input
              value={githubUrl}
              onChange={(e) => setGithubUrl(e.target.value)}
              placeholder="https://github.com/username"
              type="url"
            />
          </div>

          <div className="flex gap-3 pt-2">
            <Button
              type="button"
              variant="secondary"
              className="flex-1"
              onClick={() => router.push("/dashboard")}
            >
              Skip for now
            </Button>
            <Button type="submit" className="flex-1" disabled={saving || !name.trim()}>
              {saving ? "Saving..." : "Complete Setup"}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
