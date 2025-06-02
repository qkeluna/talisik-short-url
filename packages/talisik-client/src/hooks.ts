/**
 * React hooks for Talisik URL Shortener
 *
 * These hooks are optional and only available if React is installed.
 * They provide an easy way to integrate Talisik with React applications.
 *
 * @example
 * ```typescript
 * import { useTalisik } from 'talisik-shortener';
 *
 * function MyComponent() {
 *   const { shortenUrl, loading, error } = useTalisik({
 *     baseUrl: 'https://api.talisik.com'
 *   });
 *
 *   const handleShorten = async () => {
 *     const result = await shortenUrl({ url: 'https://example.com' });
 *     console.log(result.shortUrl);
 *   };
 *
 *   return (
 *     <button onClick={handleShorten} disabled={loading}>
 *       {loading ? 'Shortening...' : 'Shorten URL'}
 *     </button>
 *   );
 * }
 * ```
 */

import { TalisikClient } from "./client";
import {
  TalisikConfig,
  ShortenRequest,
  ShortenResponse,
  UrlInfo,
  Stats,
  UseTalisikResult,
  UseTalisikOptions,
} from "./types";
import { TalisikError } from "./errors";

// Check if React is available at runtime
function getReact() {
  try {
    // Try to access React through global/window if available
    if (typeof window !== "undefined" && (window as any).React) {
      return (window as any).React;
    }

    // Try dynamic import for Node.js environments
    if (typeof globalThis !== "undefined" && (globalThis as any).require) {
      return (globalThis as any).require("react");
    }

    return null;
  } catch {
    return null;
  }
}

/**
 * React hook for using Talisik URL Shortener
 *
 * @param options - Configuration options
 * @returns Object with shortening functions, loading state, and errors
 */
export function useTalisik(
  options: UseTalisikOptions
): UseTalisikResult | undefined {
  const React = getReact();

  if (!React) {
    console.warn("React is not available. useTalisik hook cannot be used.");
    return undefined;
  }

  const { useState, useCallback, useMemo } = React;

  const [loading, setLoading] = useState(false);
  const errorState = useState(null);
  const error = errorState[0] as TalisikError | null;
  const setError = errorState[1] as (error: TalisikError | null) => void;

  // Create client instance
  const client = useMemo(() => {
    return new TalisikClient({
      baseUrl: options.baseUrl || "http://localhost:8000",
      apiKey: options.apiKey,
      headers: options.headers,
      timeout: options.timeout,
    });
  }, [options.baseUrl, options.apiKey, options.headers, options.timeout]);

  const shortenUrl = useCallback(
    async (request: ShortenRequest): Promise<ShortenResponse> => {
      setLoading(true);
      setError(null);

      try {
        const result = await client.shorten(request);
        return result;
      } catch (err) {
        const talisikError =
          err instanceof TalisikError
            ? err
            : new TalisikError(`Unknown error: ${err}`);
        setError(talisikError);
        throw talisikError;
      } finally {
        setLoading(false);
      }
    },
    [client]
  );

  const getUrlInfo = useCallback(
    async (shortCode: string): Promise<UrlInfo | null> => {
      setLoading(true);
      setError(null);

      try {
        const result = await client.getUrlInfo(shortCode);
        return result;
      } catch (err) {
        const talisikError =
          err instanceof TalisikError
            ? err
            : new TalisikError(`Unknown error: ${err}`);
        setError(talisikError);
        throw talisikError;
      } finally {
        setLoading(false);
      }
    },
    [client]
  );

  const getStats = useCallback(async (): Promise<Stats> => {
    setLoading(true);
    setError(null);

    try {
      const result = await client.getStats();
      return result;
    } catch (err) {
      const talisikError =
        err instanceof TalisikError
          ? err
          : new TalisikError(`Unknown error: ${err}`);
      setError(talisikError);
      throw talisikError;
    } finally {
      setLoading(false);
    }
  }, [client]);

  return {
    shortenUrl,
    getUrlInfo,
    getStats,
    loading,
    error,
  };
}

/**
 * React hook for creating a Talisik client instance
 *
 * @param config - Client configuration
 * @returns Memoized TalisikClient instance
 *
 * @example
 * ```typescript
 * function MyComponent() {
 *   const client = useTalisikClient({
 *     baseUrl: 'https://api.talisik.com'
 *   });
 *
 *   const handleShorten = async () => {
 *     const result = await client.shorten({ url: 'https://example.com' });
 *   };
 *
 *   return <button onClick={handleShorten}>Shorten</button>;
 * }
 * ```
 */
export function useTalisikClient(
  config: TalisikConfig
): TalisikClient | undefined {
  const React = getReact();

  if (!React) {
    console.warn(
      "React is not available. useTalisikClient hook cannot be used."
    );
    return undefined;
  }

  const { useMemo } = React;

  return useMemo(() => {
    return new TalisikClient(config);
  }, [config.baseUrl, config.apiKey, config.headers, config.timeout]);
}

// Export hook utilities
export const hooks = {
  useTalisik,
  useTalisikClient,
};
