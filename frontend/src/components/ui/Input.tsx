"use client";

import { cn } from "@/lib/utils";
import { InputHTMLAttributes, forwardRef } from "react";

const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement>>(
  ({ className, ...props }, ref) => {
    return (
      <input
        ref={ref}
        className={cn(
          "w-full rounded-lg border border-gray-200 bg-white px-4 py-2.5 text-sm transition-colors",
          "placeholder:text-[var(--color-text-tertiary)]",
          "focus:border-[var(--color-accent)] focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)]/20",
          className
        )}
        {...props}
      />
    );
  }
);

Input.displayName = "Input";
export default Input;
