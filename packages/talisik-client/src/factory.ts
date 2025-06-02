import { TalisikClient } from "./client";
import { TalisikConfig } from "./types";

/**
 * Factory function to create a new Talisik client instance
 *
 * @param config - Client configuration
 * @returns A new TalisikClient instance
 *
 * @example
 * ```typescript
 * import { createTalisikClient } from 'talisik-shortener';
 *
 * const client = createTalisikClient({
 *   baseUrl: 'https://api.talisik.com'
 * });
 * ```
 */
export function createTalisikClient(config: TalisikConfig): TalisikClient {
  return new TalisikClient(config);
}

/**
 * Create a Talisik client with common defaults for development
 *
 * @param overrides - Configuration overrides
 * @returns A new TalisikClient instance configured for development
 *
 * @example
 * ```typescript
 * const client = createDevClient(); // Uses localhost:8000
 * ```
 */
export function createDevClient(
  overrides: Partial<TalisikConfig> = {}
): TalisikClient {
  return new TalisikClient({
    baseUrl: "http://localhost:8000",
    timeout: 5000,
    ...overrides,
  });
}

/**
 * Create a Talisik client with common defaults for production
 *
 * @param baseUrl - Production API URL
 * @param overrides - Configuration overrides
 * @returns A new TalisikClient instance configured for production
 *
 * @example
 * ```typescript
 * const client = createProdClient('https://api.yourdomain.com');
 * ```
 */
export function createProdClient(
  baseUrl: string,
  overrides: Partial<TalisikConfig> = {}
): TalisikClient {
  return new TalisikClient({
    baseUrl,
    timeout: 10000,
    ...overrides,
  });
}
