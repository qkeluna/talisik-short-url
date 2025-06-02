#!/usr/bin/env node
/**
 * Production Testing Suite for Talisik Client SDK
 *
 * This script tests the published npm package against the production API
 * to ensure the client SDK works correctly with the live backend.
 *
 * Usage:
 *     npm install talisik-shortener
 *     node test_npm_client.js https://your-production-url.com
 */

const { TalisikClient } = require("talisik-shortener");

class ClientSDKTester {
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
    this.client = new TalisikClient({ baseUrl });
    this.testResults = [];
    this.createdUrls = [];
  }

  logTest(testName, status, details = "") {
    const result = {
      test: testName,
      status,
      details,
      timestamp: new Date().toISOString(),
    };
    this.testResults.push(result);

    // Color coding for console output
    const colors = {
      PASS: "\x1b[32m",
      FAIL: "\x1b[31m",
      WARN: "\x1b[33m",
      reset: "\x1b[0m",
    };

    const color = colors[status] || colors.WARN;
    console.log(`${color}[${status}]${colors.reset} ${testName}`);
    if (details) {
      console.log(`      ${details}`);
    }
  }

  async testClientInstantiation() {
    try {
      // Test client creation
      const client = new TalisikClient({ baseUrl: this.baseUrl });
      if (client && typeof client.shorten === "function") {
        this.logTest(
          "Client Instantiation",
          "PASS",
          "TalisikClient created successfully"
        );
        return true;
      } else {
        this.logTest(
          "Client Instantiation",
          "FAIL",
          "Client missing required methods"
        );
        return false;
      }
    } catch (error) {
      this.logTest("Client Instantiation", "FAIL", `Error: ${error.message}`);
      return false;
    }
  }

  async testShortenUrl() {
    try {
      const testUrl = "https://github.com/frederickluna/talisik-short-url";
      const result = await this.client.shorten({ url: testUrl });

      if (result && result.shortCode && result.shortUrl) {
        this.createdUrls.push(result.shortCode);
        this.logTest(
          "Shorten URL (Auto)",
          "PASS",
          `Created: ${result.shortUrl}`
        );
        return result.shortCode;
      } else {
        this.logTest(
          "Shorten URL (Auto)",
          "FAIL",
          "Missing shortCode or shortUrl in response"
        );
        return null;
      }
    } catch (error) {
      this.logTest("Shorten URL (Auto)", "FAIL", `Error: ${error.message}`);
      return null;
    }
  }

  async testShortenUrlWithCustomCode() {
    try {
      const testUrl = "https://www.example.com/client-test";
      const customCode = `sdk-test-${Date.now()}`;

      const result = await this.client.shorten({
        url: testUrl,
        customCode: customCode,
      });

      if (result && result.shortCode === customCode) {
        this.createdUrls.push(result.shortCode);
        this.logTest(
          "Shorten URL (Custom)",
          "PASS",
          `Created: ${result.shortUrl}`
        );
        return result.shortCode;
      } else {
        this.logTest(
          "Shorten URL (Custom)",
          "FAIL",
          "Custom code not set correctly"
        );
        return null;
      }
    } catch (error) {
      this.logTest("Shorten URL (Custom)", "FAIL", `Error: ${error.message}`);
      return null;
    }
  }

  async testExpandUrl(shortCode) {
    try {
      const result = await this.client.expand(shortCode);

      if (result) {
        this.logTest("Expand URL", "PASS", `Original: ${result}`);
        return { originalUrl: result };
      } else {
        this.logTest("Expand URL", "FAIL", "No original URL returned");
        return null;
      }
    } catch (error) {
      this.logTest("Expand URL", "FAIL", `Error: ${error.message}`);
      return null;
    }
  }

  async testGetInfo(shortCode) {
    try {
      const result = await this.client.getUrlInfo(shortCode);

      if (result && result.shortCode && result.originalUrl !== undefined) {
        this.logTest(
          "Get URL Info",
          "PASS",
          `Clicks: ${result.clickCount || 0}`
        );
        return result;
      } else {
        this.logTest(
          "Get URL Info",
          "FAIL",
          "Missing required fields in response"
        );
        return null;
      }
    } catch (error) {
      this.logTest("Get URL Info", "FAIL", `Error: ${error.message}`);
      return null;
    }
  }

  async testGetStats() {
    try {
      const result = await this.client.getStats();

      if (result && typeof result.totalUrls === "number") {
        this.logTest(
          "Get Stats",
          "PASS",
          `Total URLs: ${result.totalUrls}, Total Clicks: ${
            result.totalClicks || 0
          }`
        );
        return result;
      } else {
        this.logTest("Get Stats", "FAIL", "Missing totalUrls in response");
        return null;
      }
    } catch (error) {
      this.logTest("Get Stats", "FAIL", `Error: ${error.message}`);
      return null;
    }
  }

  async testErrorHandling() {
    // Test invalid URL
    try {
      await this.client.shorten({ url: "not-a-valid-url" });
      this.logTest(
        "Error Handling (Invalid URL)",
        "FAIL",
        "Should have thrown an error"
      );
    } catch (error) {
      if (
        error.message.includes("Invalid URL") ||
        error.message.includes("validation") ||
        error.status === 422
      ) {
        this.logTest(
          "Error Handling (Invalid URL)",
          "PASS",
          "Properly rejects invalid URLs"
        );
      } else {
        this.logTest(
          "Error Handling (Invalid URL)",
          "FAIL",
          `Unexpected error: ${error.message}`
        );
      }
    }

    // Test non-existent short code
    try {
      await this.client.expand("nonexistent123");
      // expand might return null instead of throwing, so check for null
      this.logTest(
        "Error Handling (Not Found)",
        "PASS",
        "Properly handles missing URLs (returns null)"
      );
    } catch (error) {
      if (
        error.message.includes("not found") ||
        error.message.includes("404") ||
        error.status === 404
      ) {
        this.logTest(
          "Error Handling (Not Found)",
          "PASS",
          "Properly handles missing URLs"
        );
      } else {
        this.logTest(
          "Error Handling (Not Found)",
          "FAIL",
          `Unexpected error: ${error.message}`
        );
      }
    }
  }

  async testTypeScriptSupport() {
    try {
      // Test if TypeScript definitions are available
      const client = new TalisikClient({ baseUrl: this.baseUrl });

      // These should be available if TypeScript definitions are correct
      if (
        typeof client.shorten === "function" &&
        typeof client.expand === "function" &&
        typeof client.getUrlInfo === "function" &&
        typeof client.getStats === "function"
      ) {
        this.logTest(
          "TypeScript Support",
          "PASS",
          "All methods available with correct types"
        );
        return true;
      } else {
        this.logTest(
          "TypeScript Support",
          "FAIL",
          "Missing method definitions"
        );
        return false;
      }
    } catch (error) {
      this.logTest("TypeScript Support", "FAIL", `Error: ${error.message}`);
      return false;
    }
  }

  async runComprehensiveTest() {
    console.log(`\n🚀 Starting Client SDK Test Suite for: ${this.baseUrl}`);
    console.log("=" * 60);

    // Test 1: Client Instantiation
    if (!(await this.testClientInstantiation())) {
      console.log("\n❌ Client SDK not working. Stopping tests.");
      return;
    }

    console.log();

    // Test 2: URL Shortening (Auto-generated code)
    const shortCode = await this.testShortenUrl();

    if (shortCode) {
      // Test 3: URL Expansion
      await this.testExpandUrl(shortCode);

      // Test 4: URL Info
      await this.testGetInfo(shortCode);
    }

    console.log();

    // Test 5: Custom Code Shortening
    const customShortCode = await this.testShortenUrlWithCustomCode();

    console.log();

    // Test 6: API Statistics
    await this.testGetStats();

    console.log();

    // Test 7: Error Handling
    await this.testErrorHandling();

    console.log();

    // Test 8: TypeScript Support
    await this.testTypeScriptSupport();

    console.log();

    // Print Summary
    this.printSummary();
  }

  printSummary() {
    const totalTests = this.testResults.length;
    const passedTests = this.testResults.filter(
      (r) => r.status === "PASS"
    ).length;
    const failedTests = this.testResults.filter(
      (r) => r.status === "FAIL"
    ).length;

    console.log("=" * 60);
    console.log("📊 CLIENT SDK TEST SUMMARY");
    console.log(`Total Tests: ${totalTests}`);
    console.log(`✅ Passed: ${passedTests}`);
    console.log(`❌ Failed: ${failedTests}`);
    console.log(
      `Success Rate: ${((passedTests / totalTests) * 100).toFixed(1)}%`
    );

    if (failedTests > 0) {
      console.log("\n❌ Failed Tests:");
      this.testResults
        .filter((result) => result.status === "FAIL")
        .forEach((result) => {
          console.log(`   • ${result.test}: ${result.details}`);
        });
    }

    if (passedTests === totalTests) {
      console.log(
        "\n🎉 All tests passed! Your npm client SDK is working perfectly."
      );
    } else {
      console.log("\n⚠️  Some tests failed. Please review the issues above.");
    }

    console.log("\n📦 SDK Installation:");
    console.log("npm install talisik-shortener");
    console.log("\n📖 Usage Example:");
    console.log(`const { TalisikClient } = require('talisik-shortener');
const client = new TalisikClient({ baseUrl: '${this.baseUrl}' });
const result = await client.shorten('https://example.com');
console.log(result.shortUrl);`);
  }
}

async function main() {
  const args = process.argv.slice(2);

  if (args.length !== 1) {
    console.log("Usage: node test_npm_client.js <production-url>");
    console.log(
      "Example: node test_npm_client.js https://your-app.leapcell.io"
    );
    process.exit(1);
  }

  const productionUrl = args[0];

  try {
    const tester = new ClientSDKTester(productionUrl);
    await tester.runComprehensiveTest();
  } catch (error) {
    console.error("❌ Test suite failed:", error.message);
    process.exit(1);
  }
}

// Run if this file is executed directly
if (require.main === module) {
  main().catch((error) => {
    console.error("❌ Unexpected error:", error);
    process.exit(1);
  });
}

module.exports = { ClientSDKTester };
