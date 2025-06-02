import {
  TalisikConfig,
  ShortenRequest,
  ShortenResponse,
  UrlInfo,
  Stats,
  RequestOptions,
  TalisikMethod,
} from "./types";
import { TalisikError } from "./errors";

/**
 * Main client class for interacting with Talisik URL Shortener API
 *
 * @example
 * ```typescript
 * const client = new TalisikClient({
 *   baseUrl: 'https://api.talisik.com'
 * });
 *
 * // Shorten a URL
 * const result = await client.shorten({
 *   url: 'https://example.com',
 *   customCode: 'my-link'
 * });
 *
 * // Get URL info
 * const info = await client.getUrlInfo('my-link');
 * ```
 */
export class TalisikClient {
  private config: Required<TalisikConfig>;

  constructor(config: TalisikConfig) {
    this.config = {
      timeout: 10000,
      headers: {},
      apiKey: "",
      ...config,
    };

    // Add default headers
    this.config.headers = {
      "Content-Type": "application/json",
      ...this.config.headers,
    };

    // Add API key header if provided
    if (this.config.apiKey) {
      this.config.headers["Authorization"] = `Bearer ${this.config.apiKey}`;
    }
  }

  /**
   * Shorten a URL
   *
   * @param request - The URL shortening request
   * @param options - Additional request options
   * @returns Promise that resolves to the shortened URL information
   *
   * @example
   * ```typescript
   * const result = await client.shorten({
   *   url: 'https://example.com',
   *   customCode: 'my-custom-code',
   *   expiresHours: 24
   * });
   * ```
   */
  async shorten(
    request: ShortenRequest,
    options?: RequestOptions
  ): Promise<ShortenResponse> {
    const response = await this.request<any>(
      "POST",
      "/shorten",
      {
        url: request.url,
        custom_code: request.customCode,
        expires_hours: request.expiresHours,
      },
      options
    );

    return {
      shortUrl: response.short_url,
      originalUrl: response.original_url,
      shortCode: response.short_code,
      expiresAt: response.expires_at,
    };
  }

  /**
   * Get information about a shortened URL
   *
   * @param shortCode - The short code to look up
   * @param options - Additional request options
   * @returns Promise that resolves to URL info or null if not found
   *
   * @example
   * ```typescript
   * const info = await client.getUrlInfo('abc123');
   * if (info) {
   *   console.log(`URL has been clicked ${info.clickCount} times`);
   * }
   * ```
   */
  async getUrlInfo(
    shortCode: string,
    options?: RequestOptions
  ): Promise<UrlInfo | null> {
    try {
      const response = await this.request<any>(
        "GET",
        `/info/${shortCode}`,
        undefined,
        options
      );

      return {
        shortCode: response.short_code,
        originalUrl: response.original_url,
        createdAt: response.created_at,
        expiresAt: response.expires_at,
        clickCount: response.click_count,
        isActive: response.is_active,
        isExpired: response.is_expired,
      };
    } catch (error) {
      if (error instanceof TalisikError && error.status === 404) {
        return null;
      }
      throw error;
    }
  }

  /**
   * Get overall statistics
   *
   * @param options - Additional request options
   * @returns Promise that resolves to usage statistics
   *
   * @example
   * ```typescript
   * const stats = await client.getStats();
   * console.log(`Total URLs: ${stats.totalUrls}`);
   * ```
   */
  async getStats(options?: RequestOptions): Promise<Stats> {
    const response = await this.request<any>(
      "GET",
      "/api/stats",
      undefined,
      options
    );

    return {
      totalUrls: response.total_urls,
      activeUrls: response.active_urls,
      totalClicks: response.total_clicks,
    };
  }

  /**
   * Get the redirect URL for a short code (without following the redirect)
   *
   * @param shortCode - The short code
   * @returns The full redirect URL
   *
   * @example
   * ```typescript
   * const redirectUrl = client.getRedirectUrl('abc123');
   * // Returns: https://api.talisik.com/abc123
   * ```
   */
  getRedirectUrl(shortCode: string): string {
    return `${this.config.baseUrl}/${shortCode}`;
  }

  /**
   * Expand a short code to get the original URL (follows redirect)
   *
   * @param shortCode - The short code to expand
   * @param options - Additional request options
   * @returns Promise that resolves to the original URL or null if not found
   *
   * @example
   * ```typescript
   * const originalUrl = await client.expand('abc123');
   * // Returns: https://example.com
   * ```
   */
  async expand(
    shortCode: string,
    options?: RequestOptions
  ): Promise<string | null> {
    try {
      // First try HEAD request to get redirect without following it
      const response = await fetch(`${this.config.baseUrl}/${shortCode}`, {
        method: "HEAD",
        headers: this.config.headers,
        signal: options?.signal,
        redirect: "manual",
      });

      if (response.status === 301 || response.status === 302) {
        return response.headers.get("location");
      }

      // If HEAD is not supported (405) or doesn't return redirect, fall back to info endpoint
      if (response.status === 405 || response.status === 404) {
        const info = await this.getUrlInfo(shortCode, options);
        return info ? info.originalUrl : null;
      }

      return null;
    } catch (error) {
      // If HEAD request fails, try using the info endpoint as fallback
      try {
        const info = await this.getUrlInfo(shortCode, options);
        return info ? info.originalUrl : null;
      } catch (infoError) {
        throw new TalisikError(`Failed to expand URL: ${error}`);
      }
    }
  }

  /**
   * Low-level request method
   */
  private async request<T>(
    method: TalisikMethod,
    endpoint: string,
    body?: any,
    options?: RequestOptions
  ): Promise<T> {
    const url = `${this.config.baseUrl}${endpoint}`;
    const timeout = options?.timeout || this.config.timeout;

    const headers = {
      ...this.config.headers,
      ...options?.headers,
    };

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    // Use the provided signal or our timeout signal
    const signal = options?.signal || controller.signal;

    try {
      const response = await fetch(url, {
        method,
        headers,
        body: body ? JSON.stringify(body) : undefined,
        signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new TalisikError(
          errorData.detail || `HTTP ${response.status}: ${response.statusText}`,
          response.status,
          errorData.code,
          errorData
        );
      }

      return await response.json();
    } catch (error) {
      clearTimeout(timeoutId);

      if (error instanceof TalisikError) {
        throw error;
      }

      if ((error as any).name === "AbortError") {
        throw new TalisikError("Request timeout", 408);
      }

      throw new TalisikError(`Network error: ${(error as Error).message}`);
    }
  }
}
