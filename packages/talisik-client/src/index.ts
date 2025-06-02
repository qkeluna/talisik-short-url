/**
 * Talisik URL Shortener - JavaScript/TypeScript Client SDK
 *
 * A privacy-focused URL shortening service client that works in:
 * - React/Next.js applications
 * - Vue/Nuxt applications
 * - Svelte/SvelteKit applications
 * - Node.js backend services
 * - Browser environments
 *
 * @example
 * ```typescript
 * import { TalisikClient } from 'talisik-shortener';
 *
 * const client = new TalisikClient({
 *   baseUrl: 'https://api.talisik.com'
 * });
 *
 * const result = await client.shorten('https://example.com');
 * console.log(result.shortUrl); // https://api.talisik.com/abc123
 * ```
 */

// Export types first
export * from "./types";

// Export main client
export { TalisikClient } from "./client";

// Export utility functions
export { createTalisikClient } from "./factory";

// Export React hooks (if React is available)
export * from "./hooks";

// Export error classes
export * from "./errors";

// Default export for convenience
export { TalisikClient as default } from "./client";
