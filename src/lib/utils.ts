import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { DefaultFilters, CustomFilter } from "@/types";

/**
 * Merge Tailwind CSS classes with proper precedence
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

/**
 * Format Date to readable string
 */
export function formatDate(date: Date): string {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

/**
 * Generate unique ID
 */
export function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Truncate text with ellipsis
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength).trim() + "...";
}

/**
 * Fetch with timeout support
 */
export async function fetchWithTimeout(
  url: string,
  options: RequestInit = {},
  timeout: number = 30000
): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    if (error instanceof Error && error.name === "AbortError") {
      throw new Error(`Request timeout after ${timeout}ms`);
    }
    throw error;
  }
}

/**
 * Parse custom filter value based on type
 */
export function parseCustomFilterValue(
  filter: CustomFilter,
  value: string | boolean | number
): string | boolean | number {
  switch (filter.type) {
    case "checkbox":
      return Boolean(value);
    case "text_input":
      return String(value);
    case "radio":
    case "selectbox":
      return String(value);
    default:
      return value;
  }
}

/**
 * Build filters text for AI prompt
 */
export function buildFiltersText(
  defaultFilters: DefaultFilters,
  customFilters: Record<string, string | boolean | number>
): string {
  const parts: string[] = [];

  parts.push(`Answer Format: ${defaultFilters.answerFormat}`);
  parts.push(`Tone: ${defaultFilters.toneOfResponse}`);
  parts.push(`Detail Level: ${defaultFilters.outputDetail}/5`);
  parts.push(`Audience: ${defaultFilters.audienceLevel}`);
  parts.push(`Purpose: ${defaultFilters.purpose}`);
  parts.push(`Include Visuals: ${defaultFilters.includeVisuals ? "Yes" : "No"}`);
  parts.push(`Structure: ${defaultFilters.responseStructure}`);

  if (Object.keys(customFilters).length > 0) {
    parts.push("\nCustom Preferences:");
    Object.entries(customFilters).forEach(([key, value]) => {
      parts.push(`- ${key}: ${value}`);
    });
  }

  return parts.join("\n");
}
