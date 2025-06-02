#!/usr/bin/env node

/**
 * Offline Demo: Talisik npm Package Experience
 *
 * This shows what developers would experience when using the npm package
 * Demonstrates the API without requiring a running server
 *
 * Run with: node examples/offline-npm-demo.js
 */

console.log("🚀 Talisik URL Shortener - npm Package Demo");
console.log("============================================\n");

console.log("📦 Installation Experience:");
console.log("npm install talisik-shortener\n");

console.log("💻 Code Example - React Component:");
console.log(`
import React, { useState } from 'react';
import { TalisikClient } from 'talisik-shortener';

function UrlShortener() {
  const [url, setUrl] = useState('');
  const [result, setResult] = useState(null);
  
  const client = new TalisikClient({
    baseUrl: 'https://api.yourdomain.com'
  });

  const handleShorten = async () => {
    const shortened = await client.shorten({ url });
    setResult(shortened);
  };

  return (
    <div>
      <input 
        value={url} 
        onChange={(e) => setUrl(e.target.value)}
        placeholder="Enter URL to shorten" 
      />
      <button onClick={handleShorten}>Shorten URL</button>
      {result && (
        <div>
          <p>✅ Short URL: <a href={result.shortUrl}>{result.shortUrl}</a></p>
          <p>Original: {result.originalUrl}</p>
          <p>Expires: {result.expiresAt || 'Never'}</p>
        </div>
      )}
    </div>
  );
}
`);

console.log("🌐 Multi-Framework Support:");
console.log(`
✅ React:     import { TalisikClient } from 'talisik-shortener';
✅ Vue:       import { TalisikClient } from 'talisik-shortener';
✅ Next.js:   import { TalisikClient } from 'talisik-shortener';
✅ Svelte:    import { TalisikClient } from 'talisik-shortener';
✅ Node.js:   const { TalisikClient } = require('talisik-shortener');
`);

console.log("🎯 API Methods Available:");
console.log(`
• client.shorten({ url, customCode?, expiresHours? })
• client.getUrlInfo(shortCode)
• client.getStats()
• client.expand(shortCode)
• client.getRedirectUrl(shortCode)
`);

console.log("⚡ React Hooks (Optional):");
console.log(`
import { useTalisik } from 'talisik-shortener';

function MyComponent() {
  const { shortenUrl, loading, error } = useTalisik({
    baseUrl: 'https://api.yourdomain.com'
  });

  const handleShorten = async () => {
    const result = await shortenUrl({ url: 'https://example.com' });
    console.log(result.shortUrl);
  };

  return (
    <button onClick={handleShorten} disabled={loading}>
      {loading ? 'Shortening...' : 'Shorten URL'}
    </button>
  );
}
`);

console.log("🔧 Factory Functions:");
console.log(`
import { createDevClient, createProdClient } from 'talisik-shortener';

// Development (localhost:8000)
const devClient = createDevClient();

// Production
const prodClient = createProdClient('https://api.yourdomain.com');
`);

console.log("💡 Error Handling:");
console.log(`
import { TalisikError } from 'talisik-shortener';

try {
  const result = await client.shorten({ url: 'invalid-url' });
} catch (error) {
  if (error instanceof TalisikError) {
    console.log('Status:', error.status);
    console.log('Is client error:', error.isClientError());
    console.log('Is not found:', error.isNotFound());
  }
}
`);

console.log("🚀 **What This Means for Developers:**");
console.log(`
✅ No complex setup required
✅ Works with any JavaScript framework
✅ Full TypeScript support included
✅ Same API across all platforms
✅ Self-hosted option available
✅ No vendor lock-in
✅ Privacy-focused (no tracking)
`);

console.log("📈 **Competitive Advantages:**");
console.log(`
vs. Other URL Shorteners:
• Self-hosted (you own your data)
• Open source (full transparency)
• Developer-first (built for integration)
• No tracking beyond basic analytics

vs. shadcn/ui approach:
• Simpler (just npm install, no copying code)
• Maintained (updates via npm)
• Consistent (same API everywhere)
• Backend included (full solution)
`);

console.log("🎯 **Ready for Launch:**");
console.log(`
1. Complete TypeScript client ✅
2. Multi-framework support ✅
3. Comprehensive documentation ✅
4. Error handling & types ✅
5. React hooks included ✅
6. Factory functions ✅

Next steps:
• Fix minor TypeScript issues
• Publish to npm registry
• Create example repositories
• Developer community outreach
`);

console.log("\n🌟 **Total Addressable Market:**");
console.log("• React Developers: 13.8M+");
console.log("• Vue Developers: 4.2M+");
console.log("• Next.js Developers: 2.8M+");
console.log("• Node.js Developers: 16.9M+");
console.log("**Total: 30M+ JavaScript developers** 🎯\n");

console.log(
  "🎉 **This positions Talisik as the go-to URL shortener for developers!**"
);
console.log(
  "    Making URL shortening as easy as installing any other npm package.\n"
);
