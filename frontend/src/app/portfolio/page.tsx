"use client";

import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import Modal from "@/components/ui/Modal";
import Input from "@/components/ui/Input";
import { api, PortfolioItem } from "@/lib/api";
import { cn, formatDate } from "@/lib/utils";
import { useAuthStore } from "@/stores/authStore";
import { Award, Briefcase, Code2, ExternalLink, Plus, Sparkles } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

const tabs = [
  { value: "", label: "All", icon: Code2 },
  { value: "project", label: "Projects", icon: Code2 },
  { value: "award", label: "Awards", icon: Award },
  { value: "career", label: "Career", icon: Briefcase },
];

export default function PortfolioPage() {
  const { user } = useAuthStore();
  const [items, setItems] = useState<PortfolioItem[]>([]);
  const [activeTab, setActiveTab] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);

  // Form state
  const [formData, setFormData] = useState({
    type: "project",
    title: "",
    description: "",
    tech_stack: "",
    organization: "",
    role: "",
    source_url: "",
    start_date: "",
    end_date: "",
  });

  const loadItems = () => {
    setLoading(true);
    api
      .getPortfolioItems(activeTab || undefined)
      .then(setItems)
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadItems();
  }, [activeTab]);

  const handleSubmit = async () => {
    try {
      await api.createPortfolioItem({
        type: formData.type,
        title: formData.title,
        description: formData.description || undefined,
        tech_stack: formData.tech_stack ? formData.tech_stack.split(",").map((t) => t.trim()) : undefined,
        organization: formData.organization || undefined,
        role: formData.role || undefined,
        source_url: formData.source_url || undefined,
        start_date: formData.start_date || undefined,
        end_date: formData.end_date || undefined,
      });
      setShowForm(false);
      setFormData({ type: "project", title: "", description: "", tech_stack: "", organization: "", role: "", source_url: "", start_date: "", end_date: "" });
      loadItems();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to create");
    }
  };

  return (
    <div className="mx-auto max-w-6xl px-4 py-12">
      <div className="mb-8 flex items-center justify-between">
        <h1 className="text-3xl font-bold">Portfolio</h1>
        {user && (
          <div className="flex gap-2">
            <Button variant="secondary" onClick={() => setShowForm(true)}>
              <Plus size={16} className="mr-1" /> Add Item
            </Button>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="mb-8 flex gap-1">
        {tabs.map((tab) => (
          <button
            key={tab.value}
            onClick={() => setActiveTab(tab.value)}
            className={cn(
              "flex items-center gap-1.5 rounded-lg px-4 py-2 text-sm font-medium transition-colors",
              activeTab === tab.value
                ? "bg-[var(--color-accent)] text-white"
                : "text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-tertiary)]"
            )}
          >
            <tab.icon size={16} />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Items */}
      {loading ? (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-48 animate-pulse rounded-xl bg-[var(--color-bg-tertiary)]" />
          ))}
        </div>
      ) : items.length === 0 ? (
        <div className="py-20 text-center text-[var(--color-text-secondary)]">
          No portfolio items yet.
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {items.map((item) => (
            <Card key={item.id}>
              <div className="mb-3 flex items-center justify-between">
                <span className={cn(
                  "rounded-full px-2.5 py-0.5 text-xs font-medium",
                  item.type === "project" && "bg-blue-100 text-blue-700",
                  item.type === "award" && "bg-amber-100 text-amber-700",
                  item.type === "career" && "bg-emerald-100 text-emerald-700",
                )}>
                  {item.type}
                </span>
                {item.source_url && (
                  <a href={item.source_url} target="_blank" rel="noopener noreferrer" className="text-[var(--color-text-secondary)] hover:text-[var(--color-accent)]">
                    <ExternalLink size={16} />
                  </a>
                )}
              </div>
              <h3 className="mb-1 font-bold">{item.title}</h3>
              {item.organization && (
                <p className="mb-2 text-sm text-[var(--color-text-secondary)]">{item.organization}</p>
              )}
              {item.description && (
                <p className="mb-3 text-sm text-[var(--color-text-secondary)] line-clamp-3">{item.description}</p>
              )}
              {item.tech_stack && item.tech_stack.length > 0 && (
                <div className="mb-3 flex flex-wrap gap-1">
                  {item.tech_stack.map((tech) => (
                    <span key={tech} className="rounded-md bg-[var(--color-bg-tertiary)] px-2 py-0.5 text-xs">{tech}</span>
                  ))}
                </div>
              )}
              <div className="flex items-center justify-between text-xs text-[var(--color-text-tertiary)]">
                <span>
                  {item.start_date && formatDate(item.start_date)}
                  {item.end_date && ` ~ ${formatDate(item.end_date)}`}
                </span>
                {user && (
                  <button
                    onClick={() => {
                      api.generateFromPortfolio(item.id).then((task) => {
                        window.location.href = `/generate?task=${task.id}`;
                      });
                    }}
                    className="flex items-center gap-1 text-[var(--color-accent)] hover:underline"
                  >
                    <Sparkles size={12} /> Generate Blog
                  </button>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Add Item Modal */}
      <Modal isOpen={showForm} onClose={() => setShowForm(false)} title="Add Portfolio Item" className="max-w-md">
        <div className="space-y-3">
          <select
            value={formData.type}
            onChange={(e) => setFormData({ ...formData, type: e.target.value })}
            className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm"
          >
            <option value="project">Project</option>
            <option value="award">Award</option>
            <option value="career">Career</option>
          </select>
          <Input placeholder="Title *" value={formData.title} onChange={(e) => setFormData({ ...formData, title: e.target.value })} />
          <textarea
            placeholder="Description"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            className="w-full rounded-lg border border-gray-200 px-4 py-2.5 text-sm focus:border-[var(--color-accent)] focus:outline-none"
            rows={3}
          />
          <Input placeholder="Tech Stack (comma separated)" value={formData.tech_stack} onChange={(e) => setFormData({ ...formData, tech_stack: e.target.value })} />
          <Input placeholder="Organization" value={formData.organization} onChange={(e) => setFormData({ ...formData, organization: e.target.value })} />
          <Input placeholder="Role" value={formData.role} onChange={(e) => setFormData({ ...formData, role: e.target.value })} />
          <Input placeholder="Source URL" value={formData.source_url} onChange={(e) => setFormData({ ...formData, source_url: e.target.value })} />
          <div className="flex gap-3">
            <Input type="date" placeholder="Start Date" value={formData.start_date} onChange={(e) => setFormData({ ...formData, start_date: e.target.value })} />
            <Input type="date" placeholder="End Date" value={formData.end_date} onChange={(e) => setFormData({ ...formData, end_date: e.target.value })} />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="secondary" onClick={() => setShowForm(false)}>Cancel</Button>
            <Button onClick={handleSubmit} disabled={!formData.title}>Create</Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
