#!/usr/bin/env node

/**
 * Demo script showing how to integrate Talisik URL Shortener API
 * This demonstrates the same patterns you'd use in React/JavaScript
 *
 * Run with: node examples/react_demo.js
 * (Make sure the API is running: make api)
 */

const API_URL = process.env.API_URL || "http://localhost:8000";

// Talisik Client - same code you'd use in React
class TalisikClient {
  async shortenUrl({ url, customCode = null, expiresHours = null }) {
    const response = await fetch(`${API_URL}/shorten`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        url,
        custom_code: customCode,
        expires_hours: expiresHours,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to shorten URL");
    }

    return await response.json();
  }

  async getUrlInfo(shortCode) {
    const response = await fetch(`${API_URL}/info/${shortCode}`);
    return response.ok ? await response.json() : null;
  }

  async getStats() {
    const response = await fetch(`${API_URL}/api/stats`);
    return response.ok ? await response.json() : null;
  }

  getRedirectUrl(shortCode) {
    return `${API_URL}/${shortCode}`;
  }
}

// Demo usage
async function demonstrateIntegration() {
  console.log("🔗 Talisik URL Shortener - JavaScript Integration Demo\n");

  const client = new TalisikClient();

  try {
    // 1. Shorten a URL
    console.log("1. Shortening URL...");
    const result = await client.shortenUrl({
      url: "https://github.com/features",
      customCode: null,
      expiresHours: 24,
    });

    console.log("✅ URL shortened successfully!");
    console.log(`   Short URL: ${result.short_url}`);
    console.log(`   Original: ${result.original_url}`);
    console.log(`   Code: ${result.short_code}`);
    console.log(`   Expires: ${result.expires_at || "Never"}\n`);

    // 2. Get URL info
    console.log("2. Getting URL info...");
    const info = await client.getUrlInfo(result.short_code);

    if (info) {
      console.log("✅ URL info retrieved:");
      console.log(`   Clicks: ${info.click_count}`);
      console.log(`   Active: ${info.is_active}`);
      console.log(
        `   Created: ${new Date(info.created_at).toLocaleString()}\n`
      );
    }

    // 3. Create a custom code URL
    console.log("3. Creating URL with custom code...");
    const customResult = await client.shortenUrl({
      url: "https://docs.python.org/3/",
      customCode: "python-docs",
    });

    console.log("✅ Custom URL created:");
    console.log(`   Short URL: ${customResult.short_url}`);
    console.log(`   Custom Code: ${customResult.short_code}\n`);

    // 4. Get overall stats
    console.log("4. Getting overall statistics...");
    const stats = await client.getStats();

    if (stats) {
      console.log("✅ Statistics:");
      console.log(`   Total URLs: ${stats.total_urls}`);
      console.log(`   Active URLs: ${stats.active_urls}`);
      console.log(`   Total Clicks: ${stats.total_clicks}\n`);
    }

    // 5. Show how redirects work
    console.log("5. Redirect URLs (click to test):");
    console.log(`   ${client.getRedirectUrl(result.short_code)}`);
    console.log(`   ${client.getRedirectUrl("python-docs")}\n`);

    console.log(
      "🎉 Demo complete! You can now integrate these patterns into React."
    );
    console.log("\nNext steps:");
    console.log("- Copy TalisikClient to your React project");
    console.log("- Use in components with useState/useEffect");
    console.log("- Add error handling and loading states");
    console.log("- See docs/REACT_QUICKSTART.md for full setup");
  } catch (error) {
    console.error("❌ Demo failed:", error.message);
    console.log("\nMake sure the API is running:");
    console.log("  cd talisik-short-url");
    console.log("  make api");
  }
}

// Check if fetch is available (Node 18+)
if (typeof fetch === "undefined") {
  console.error("❌ This demo requires Node.js 18+ with fetch support.");
  console.log("Run with: node --experimental-fetch react_demo.js");
  process.exit(1);
}

// Run the demo
demonstrateIntegration();
