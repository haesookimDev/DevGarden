"use client";

import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import Input from "@/components/ui/Input";
import { api, AIConfig } from "@/lib/api";
import { useAuthStore } from "@/stores/authStore";
import { Bot, Key, Plus, Trash2, User } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

const providers = [
  { value: "claude", label: "Claude (Anthropic)", defaultModel: "claude-sonnet-4-20250514" },
  { value: "openai", label: "OpenAI", defaultModel: "gpt-4o" },
  { value: "google", label: "Google Gemini", defaultModel: "gemini-2.0-flash" },
  { value: "private", label: "Private Model", defaultModel: "" },
];

export default function SettingsPage() {
  const { user } = useAuthStore();
  const [aiConfigs, setAIConfigs] = useState<AIConfig[]>([]);
  const [showAddForm, setShowAddForm] = useState(false);

  // Profile form
  const [name, setName] = useState(user?.name || "");
  const [bio, setBio] = useState(user?.bio || "");
  const [githubUrl, setGithubUrl] = useState(user?.github_url || "");

  // AI form
  const [newProvider, setNewProvider] = useState("claude");
  const [newApiKey, setNewApiKey] = useState("");
  const [newModelName, setNewModelName] = useState("claude-sonnet-4-20250514");
  const [newBaseUrl, setNewBaseUrl] = useState("");
  const [newIsDefault, setNewIsDefault] = useState(false);

  useEffect(() => {
    if (user) {
      api.getAIConfigs().then(setAIConfigs).catch(() => {});
    }
  }, [user]);

  if (!user) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-20 text-center">
        <p className="mb-4 text-[var(--color-text-secondary)]">Please sign in to access settings.</p>
        <Link href="/auth/login"><Button>Sign In</Button></Link>
      </div>
    );
  }

  const handleProfileUpdate = async () => {
    try {
      await api.updateProfile({ name, bio, github_url: githubUrl });
      alert("Profile updated!");
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to update");
    }
  };

  const handleAddAIConfig = async () => {
    try {
      const config = await api.createAIConfig({
        provider: newProvider,
        api_key: newApiKey,
        model_name: newModelName || undefined,
        base_url: newProvider === "private" ? newBaseUrl : undefined,
        is_default: newIsDefault,
      });
      setAIConfigs([...aiConfigs, config]);
      setShowAddForm(false);
      setNewApiKey("");
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to add");
    }
  };

  const handleDeleteAIConfig = async (id: string) => {
    if (!confirm("Delete this AI configuration?")) return;
    try {
      await api.deleteAIConfig(id);
      setAIConfigs(aiConfigs.filter((c) => c.id !== id));
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to delete");
    }
  };

  return (
    <div className="mx-auto max-w-3xl px-4 py-12">
      <h1 className="mb-8 text-3xl font-bold">Settings</h1>

      {/* Profile Section */}
      <Card hover={false} className="mb-6">
        <div className="mb-4 flex items-center gap-2">
          <User size={20} />
          <h2 className="text-lg font-bold">Profile</h2>
        </div>
        <div className="space-y-3">
          <div>
            <label className="mb-1 block text-sm font-medium">Name</label>
            <Input value={name} onChange={(e) => setName(e.target.value)} />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Bio</label>
            <textarea
              value={bio}
              onChange={(e) => setBio(e.target.value)}
              className="w-full rounded-lg border border-gray-200 px-4 py-2.5 text-sm focus:border-[var(--color-accent)] focus:outline-none"
              rows={3}
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">GitHub URL</label>
            <Input value={githubUrl} onChange={(e) => setGithubUrl(e.target.value)} placeholder="https://github.com/username" />
          </div>
          <Button onClick={handleProfileUpdate}>Save Profile</Button>
        </div>
      </Card>

      {/* AI Configuration */}
      <Card hover={false}>
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bot size={20} />
            <h2 className="text-lg font-bold">AI Models</h2>
          </div>
          <Button size="sm" variant="secondary" onClick={() => setShowAddForm(!showAddForm)}>
            <Plus size={16} className="mr-1" /> Add Provider
          </Button>
        </div>

        <p className="mb-4 text-sm text-[var(--color-text-secondary)]">
          Register your AI provider API keys to enable blog auto-generation.
        </p>

        {/* Existing configs */}
        {aiConfigs.length > 0 && (
          <div className="mb-4 space-y-2">
            {aiConfigs.map((config) => (
              <div key={config.id} className="flex items-center justify-between rounded-lg bg-[var(--color-bg-secondary)] p-3">
                <div className="flex items-center gap-3">
                  <Key size={16} className="text-[var(--color-text-secondary)]" />
                  <div>
                    <span className="text-sm font-medium">
                      {providers.find((p) => p.value === config.provider)?.label || config.provider}
                    </span>
                    {config.model_name && (
                      <span className="ml-2 text-xs text-[var(--color-text-tertiary)]">{config.model_name}</span>
                    )}
                    {config.is_default && (
                      <span className="ml-2 rounded-full bg-[var(--color-accent-light)] px-2 py-0.5 text-xs text-[var(--color-accent)]">
                        Default
                      </span>
                    )}
                  </div>
                </div>
                <button
                  onClick={() => handleDeleteAIConfig(config.id)}
                  className="rounded-lg p-1.5 text-[var(--color-text-tertiary)] hover:bg-red-50 hover:text-red-500"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Add form */}
        {showAddForm && (
          <div className="space-y-3 rounded-lg border border-gray-200 p-4">
            <select
              value={newProvider}
              onChange={(e) => {
                setNewProvider(e.target.value);
                const p = providers.find((p) => p.value === e.target.value);
                setNewModelName(p?.defaultModel || "");
              }}
              className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm"
            >
              {providers.map((p) => (
                <option key={p.value} value={p.value}>{p.label}</option>
              ))}
            </select>
            <Input
              placeholder="API Key *"
              type="password"
              value={newApiKey}
              onChange={(e) => setNewApiKey(e.target.value)}
            />
            <Input
              placeholder="Model Name"
              value={newModelName}
              onChange={(e) => setNewModelName(e.target.value)}
            />
            {newProvider === "private" && (
              <Input
                placeholder="Base URL (required for private models)"
                value={newBaseUrl}
                onChange={(e) => setNewBaseUrl(e.target.value)}
              />
            )}
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={newIsDefault}
                onChange={(e) => setNewIsDefault(e.target.checked)}
              />
              Set as default provider
            </label>
            <div className="flex justify-end gap-2">
              <Button variant="secondary" onClick={() => setShowAddForm(false)}>Cancel</Button>
              <Button onClick={handleAddAIConfig} disabled={!newApiKey}>Add</Button>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}
