#!/usr/bin/env node

/**
 * Demo: How developers would use talisik-shortener npm package
 *
 * This simulates what the developer experience would be like
 * after installing: npm install talisik-shortener
 *
 * Run with: node examples/npm-package-demo.js
 */

// Simulate importing from the npm package
// In real usage: import { TalisikClient } from 'talisik-shortener';

const API_URL = process.env.API_URL || "http://localhost:8000";

// This is what the TalisikClient would look like in the npm package
class TalisikClient {
  constructor(config) {
    this.baseUrl = config.baseUrl;
    this.timeout = config.timeout || 10000;
    this.headers = {
      "Content-Type": "application/json",
      ...config.headers,
    };
  }

  async shorten(request) {
    const response = await fetch(`${this.baseUrl}/shorten`, {
      method: "POST",
      headers: this.headers,
      body: JSON.stringify({
        url: request.url,
        custom_code: request.customCode,
        expires_hours: request.expiresHours,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to shorten URL");
    }

    const data = await response.json();
    return {
      shortUrl: data.short_url,
      originalUrl: data.original_url,
      shortCode: data.short_code,
      expiresAt: data.expires_at,
    };
  }

  async getUrlInfo(shortCode) {
    const response = await fetch(`${this.baseUrl}/info/${shortCode}`, {
      headers: this.headers,
    });

    if (response.status === 404) {
      return null;
    }

    if (!response.ok) {
      throw new Error("Failed to get URL info");
    }

    const data = await response.json();
    return {
      shortCode: data.short_code,
      originalUrl: data.original_url,
      createdAt: data.created_at,
      expiresAt: data.expires_at,
      clickCount: data.click_count,
      isActive: data.is_active,
      isExpired: data.is_expired,
    };
  }

  async getStats() {
    const response = await fetch(`${this.baseUrl}/api/stats`, {
      headers: this.headers,
    });

    if (!response.ok) {
      throw new Error("Failed to get stats");
    }

    const data = await response.json();
    return {
      totalUrls: data.total_urls,
      activeUrls: data.active_urls,
      totalClicks: data.total_clicks,
    };
  }

  getRedirectUrl(shortCode) {
    return `${this.baseUrl}/${shortCode}`;
  }
}

// Demo: Various developer scenarios
async function demonstrateNpmPackageUsage() {
  console.log("🚀 Talisik npm Package Demo");
  console.log("===========================\n");

  // Initialize client (what developers would do)
  const client = new TalisikClient({
    baseUrl: API_URL,
    timeout: 5000,
  });

  try {
    console.log("📦 Scenario 1: React Developer");
    console.log('import { TalisikClient } from "talisik-shortener";');
    console.log(
      'const client = new TalisikClient({ baseUrl: "https://api.mydomain.com" });\n'
    );

    // Shorten a URL
    const result1 = await client.shorten({
      url: "https://reactjs.org/docs",
      customCode: "react-docs",
    });
    console.log("✅ Shortened URL for React docs:");
    console.log(`   ${result1.shortUrl}\n`);

    console.log("📦 Scenario 2: Vue Developer");
    console.log('import { TalisikClient } from "talisik-shortener";');
    console.log(
      'const client = new TalisikClient({ baseUrl: "https://api.mydomain.com" });\n'
    );

    // Shorten a URL
    const result2 = await client.shorten({
      url: "https://vuejs.org/guide/",
      expiresHours: 48,
    });
    console.log("✅ Shortened URL for Vue guide:");
    console.log(`   ${result2.shortUrl}\n`);

    console.log("📦 Scenario 3: Next.js Developer (API Route)");
    console.log("// pages/api/shorten.js");
    console.log('import { TalisikClient } from "talisik-shortener";\n');

    const result3 = await client.shorten({
      url: "https://nextjs.org/docs",
    });
    console.log("✅ Shortened URL for Next.js docs:");
    console.log(`   ${result3.shortUrl}\n`);

    console.log("📦 Scenario 4: Node.js Backend");
    console.log('const { TalisikClient } = require("talisik-shortener");\n');

    const result4 = await client.shorten({
      url: "https://nodejs.org/en/docs/",
    });
    console.log("✅ Shortened URL for Node.js docs:");
    console.log(`   ${result4.shortUrl}\n`);

    // Show stats
    console.log("📊 Getting Statistics:");
    const stats = await client.getStats();
    console.log(`   Total URLs: ${stats.totalUrls}`);
    console.log(`   Active URLs: ${stats.activeUrls}`);
    console.log(`   Total Clicks: ${stats.totalClicks}\n`);

    // Show URL info
    console.log("🔍 Getting URL Info:");
    const info = await client.getUrlInfo("react-docs");
    if (info) {
      console.log(`   Short Code: ${info.shortCode}`);
      console.log(`   Original: ${info.originalUrl}`);
      console.log(`   Clicks: ${info.clickCount}`);
      console.log(`   Active: ${info.isActive}\n`);
    }

    console.log("🎉 Demo Complete!");
    console.log("\n💡 What developers get:");
    console.log("   ✅ npm install talisik-shortener");
    console.log("   ✅ TypeScript support included");
    console.log("   ✅ Works with React, Vue, Next.js, Node.js");
    console.log("   ✅ Same API across all frameworks");
    console.log("   ✅ Error handling built-in");
    console.log("   ✅ Timeout and cancellation support");

    console.log("\n🔗 Redirect URLs created:");
    console.log(`   React Docs: ${client.getRedirectUrl("react-docs")}`);
    console.log(`   Vue Guide: ${client.getRedirectUrl(result2.shortCode)}`);
    console.log(`   Next.js Docs: ${client.getRedirectUrl(result3.shortCode)}`);
    console.log(`   Node.js Docs: ${client.getRedirectUrl(result4.shortCode)}`);
  } catch (error) {
    console.error("❌ Demo failed:", error.message);
    console.log("\n💡 To run this demo:");
    console.log("   1. Start the API: make api");
    console.log("   2. Run demo: node examples/npm-package-demo.js");
  }
}

// Check Node.js version and run demo
if (typeof fetch === "undefined") {
  console.error("❌ This demo requires Node.js 18+ with fetch support.");
  console.log("   Run with: node --experimental-fetch npm-package-demo.js");
  process.exit(1);
}

demonstrateNpmPackageUsage();
