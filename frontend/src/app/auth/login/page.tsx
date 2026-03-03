"use client";

import Card from "@/components/ui/Card";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/authStore";
import { Code2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function LoginPage() {
  const router = useRouter();
  const { user, setAuth } = useAuthStore();

  useEffect(() => {
    if (user) router.push("/");
  }, [user, router]);

  useEffect(() => {
    // Load Google Sign-In script
    const script = document.createElement("script");
    script.src = "https://accounts.google.com/gsi/client";
    script.async = true;
    document.body.appendChild(script);

    script.onload = () => {
      if (window.google) {
        window.google.accounts.id.initialize({
          client_id: process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "",
          callback: handleGoogleCallback,
        });
        window.google.accounts.id.renderButton(
          document.getElementById("google-signin-btn")!,
          {
            theme: "outline",
            size: "large",
            width: "320",
            text: "signin_with",
          }
        );
      }
    };

    return () => {
      document.body.removeChild(script);
    };
  }, []);

  const handleGoogleCallback = async (response: { credential: string }) => {
    try {
      const result = await api.googleAuth(response.credential);
      setAuth(result.access_token, result.user);
      if (result.is_new_user) {
        router.push("/auth/register");
      } else {
        router.push("/");
      }
    } catch (err) {
      alert("Login failed. Please try again.");
    }
  };

  return (
    <div className="flex min-h-[70vh] items-center justify-center px-4">
      <Card hover={false} className="w-full max-w-md text-center">
        <div className="mb-6 flex justify-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-[var(--color-accent-light)]">
            <Code2 size={32} className="text-[var(--color-accent)]" />
          </div>
        </div>
        <h1 className="mb-2 text-2xl font-bold">Welcome to DevLog</h1>
        <p className="mb-8 text-sm text-[var(--color-text-secondary)]">
          Sign in with your Google account to start creating.
        </p>
        <div className="flex justify-center">
          <div id="google-signin-btn" />
        </div>
        <p className="mt-6 text-xs text-[var(--color-text-tertiary)]">
          By signing in, you agree to our Terms of Service and Privacy Policy.
        </p>
      </Card>
    </div>
  );
}

// Type declaration for Google Sign-In
declare global {
  interface Window {
    google: {
      accounts: {
        id: {
          initialize: (config: { client_id: string; callback: (response: { credential: string }) => void }) => void;
          renderButton: (element: HTMLElement, config: object) => void;
        };
      };
    };
  }
}
