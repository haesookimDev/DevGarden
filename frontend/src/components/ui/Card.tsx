"use client";

import { cn } from "@/lib/utils";
import { HTMLAttributes } from "react";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  hover?: boolean;
}

export default function Card({ className, hover = true, children, ...props }: CardProps) {
  return (
    <div
      className={cn(
        "rounded-xl border border-gray-100 bg-white p-6",
        hover && "transition-all hover:shadow-md hover:border-gray-200",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}
