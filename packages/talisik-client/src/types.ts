/**
 * TypeScript type definitions for Talisik URL Shortener
 */

import { TalisikError } from "./errors";

// Configuration types
export interface TalisikConfig {
  /** Base URL of the Talisik API server */
  baseUrl: string;
  /** API key for authentication (if required) */
  apiKey?: string;
  /** Custom headers to include with requests */
  headers?: Record<string, string>;
  /** Request timeout in milliseconds (default: 10000) */
  timeout?: number;
}

// Request types
export interface ShortenRequest {
  /** The URL to shorten */
  url: string;
  /** Custom short code (optional) */
  customCode?: string | null;
  /** Expiration time in hours (optional) */
  expiresHours?: number | null;
}

// Response types
export interface ShortenResponse {
  /** The generated short URL */
  shortUrl: string;
  /** The original URL that was shortened */
  originalUrl: string;
  /** The short code used */
  shortCode: string;
  /** Expiration date in ISO format (if set) */
  expiresAt?: string | null;
}

export interface UrlInfo {
  /** The short code */
  shortCode: string;
  /** The original URL */
  originalUrl: string;
  /** Creation timestamp in ISO format */
  createdAt: string;
  /** Expiration timestamp in ISO format (if set) */
  expiresAt?: string | null;
  /** Number of times this URL has been clicked */
  clickCount: number;
  /** Whether the URL is active */
  isActive: boolean;
  /** Whether the URL has expired */
  isExpired: boolean;
}

export interface Stats {
  /** Total number of URLs created */
  totalUrls: number;
  /** Number of active URLs */
  activeUrls: number;
  /** Total number of clicks across all URLs */
  totalClicks: number;
}

// Client method options
export interface RequestOptions {
  /** Override the default timeout for this request */
  timeout?: number;
  /** Additional headers for this request */
  headers?: Record<string, string>;
  /** AbortController signal for request cancellation */
  signal?: AbortSignal;
}

// Utility types
export type TalisikMethod = "GET" | "POST" | "PUT" | "DELETE";

export interface APIResponse<T = unknown> {
  data: T;
  success: boolean;
  error?: TalisikError;
}

// React hook types (optional, only used if React is available)
export interface UseTalisikResult {
  shortenUrl: (request: ShortenRequest) => Promise<ShortenResponse>;
  getUrlInfo: (shortCode: string) => Promise<UrlInfo | null>;
  getStats: () => Promise<Stats>;
  loading: boolean;
  error: TalisikError | null;
}

export interface UseTalisikOptions extends Partial<TalisikConfig> {
  /** Whether to automatically retry failed requests */
  retry?: boolean;
  /** Number of retry attempts (default: 3) */
  retryAttempts?: number;
}
