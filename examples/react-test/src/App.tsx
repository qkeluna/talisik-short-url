import React, { useState, useEffect } from "react";
import { TalisikClient } from "talisik-shortener";
import "./App.css";

// Replace with your production URL
const API_URL =
  process.env.REACT_APP_API_URL || "https://your-production-url.com";

interface ShortenedUrl {
  shortCode: string;
  shortUrl: string;
  originalUrl: string;
  clicks?: number;
  createdAt?: string;
}

interface TestResult {
  test: string;
  status: "PASS" | "FAIL" | "RUNNING";
  details: string;
}

function App() {
  const [client] = useState(() => new TalisikClient({ baseUrl: API_URL }));
  const [url, setUrl] = useState(
    "https://github.com/frederickluna/talisik-short-url"
  );
  const [customCode, setCustomCode] = useState("");
  const [shortenedUrls, setShortenedUrls] = useState<ShortenedUrl[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<{
    totalUrls: number;
    totalClicks: number;
  } | null>(null);
  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [runningTests, setRunningTests] = useState(false);

  // Load stats on component mount
  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const statsData = await client.getStats();
      setStats(statsData);
    } catch (err) {
      console.error("Failed to load stats:", err);
    }
  };

  const handleShorten = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const options = customCode ? { customCode } : undefined;
      const result = await client.shorten(url, options);

      const newUrl: ShortenedUrl = {
        shortCode: result.shortCode,
        shortUrl: result.shortUrl,
        originalUrl: url,
      };

      setShortenedUrls((prev) => [newUrl, ...prev]);
      setUrl("");
      setCustomCode("");
      await loadStats(); // Refresh stats
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to shorten URL");
    } finally {
      setLoading(false);
    }
  };

  const handleExpand = async (shortCode: string) => {
    try {
      const info = await client.getInfo(shortCode);
      setShortenedUrls((prev) =>
        prev.map((url) =>
          url.shortCode === shortCode
            ? { ...url, clicks: info.clicks, createdAt: info.createdAt }
            : url
        )
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to get URL info");
    }
  };

  const runTests = async () => {
    setRunningTests(true);
    setTestResults([]);

    const addTestResult = (
      test: string,
      status: TestResult["status"],
      details: string
    ) => {
      setTestResults((prev) => [...prev, { test, status, details }]);
    };

    // Test 1: Basic Shortening
    addTestResult("Basic URL Shortening", "RUNNING", "Testing...");
    try {
      const result = await client.shorten("https://example.com/test");
      addTestResult(
        "Basic URL Shortening",
        "PASS",
        `Created: ${result.shortUrl}`
      );
    } catch (err) {
      addTestResult(
        "Basic URL Shortening",
        "FAIL",
        err instanceof Error ? err.message : "Unknown error"
      );
    }

    // Test 2: Custom Code
    addTestResult("Custom Code Shortening", "RUNNING", "Testing...");
    try {
      const customTestCode = `test-${Date.now()}`;
      const result = await client.shorten("https://example.com/custom", {
        customCode: customTestCode,
      });
      if (result.shortCode === customTestCode) {
        addTestResult(
          "Custom Code Shortening",
          "PASS",
          `Custom code: ${customTestCode}`
        );
      } else {
        addTestResult(
          "Custom Code Shortening",
          "FAIL",
          "Custom code not set correctly"
        );
      }
    } catch (err) {
      addTestResult(
        "Custom Code Shortening",
        "FAIL",
        err instanceof Error ? err.message : "Unknown error"
      );
    }

    // Test 3: URL Expansion
    addTestResult("URL Expansion", "RUNNING", "Testing...");
    try {
      // Use first shortened URL if available
      if (shortenedUrls.length > 0) {
        const result = await client.expand(shortenedUrls[0].shortCode);
        addTestResult(
          "URL Expansion",
          "PASS",
          `Original: ${result.originalUrl}`
        );
      } else {
        addTestResult("URL Expansion", "FAIL", "No URLs available to test");
      }
    } catch (err) {
      addTestResult(
        "URL Expansion",
        "FAIL",
        err instanceof Error ? err.message : "Unknown error"
      );
    }

    // Test 4: Stats
    addTestResult("Statistics API", "RUNNING", "Testing...");
    try {
      const statsData = await client.getStats();
      addTestResult(
        "Statistics API",
        "PASS",
        `URLs: ${statsData.totalUrls}, Clicks: ${statsData.totalClicks}`
      );
    } catch (err) {
      addTestResult(
        "Statistics API",
        "FAIL",
        err instanceof Error ? err.message : "Unknown error"
      );
    }

    // Test 5: Error Handling
    addTestResult("Error Handling", "RUNNING", "Testing...");
    try {
      await client.shorten("invalid-url");
      addTestResult("Error Handling", "FAIL", "Should have thrown an error");
    } catch (err) {
      addTestResult("Error Handling", "PASS", "Properly rejects invalid URLs");
    }

    setRunningTests(false);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🔗 Talisik URL Shortener</h1>
        <p>React SDK Integration Test</p>
        <p className="api-url">API: {API_URL}</p>
      </header>

      <main className="App-main">
        {/* URL Shortening Form */}
        <section className="shorten-section">
          <h2>Shorten URL</h2>
          <form onSubmit={handleShorten} className="shorten-form">
            <div className="input-group">
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="Enter URL to shorten..."
                required
                disabled={loading}
              />
              <input
                type="text"
                value={customCode}
                onChange={(e) => setCustomCode(e.target.value)}
                placeholder="Custom code (optional)"
                disabled={loading}
              />
              <button type="submit" disabled={loading || !url}>
                {loading ? "Shortening..." : "Shorten"}
              </button>
            </div>
          </form>
          {error && <div className="error">{error}</div>}
        </section>

        {/* Statistics */}
        {stats && (
          <section className="stats-section">
            <h3>📊 Statistics</h3>
            <div className="stats">
              <div className="stat">
                <span className="stat-value">{stats.totalUrls}</span>
                <span className="stat-label">Total URLs</span>
              </div>
              <div className="stat">
                <span className="stat-value">{stats.totalClicks}</span>
                <span className="stat-label">Total Clicks</span>
              </div>
            </div>
          </section>
        )}

        {/* Shortened URLs */}
        {shortenedUrls.length > 0 && (
          <section className="urls-section">
            <h3>📋 Shortened URLs</h3>
            <div className="urls-list">
              {shortenedUrls.map((item, index) => (
                <div key={index} className="url-item">
                  <div className="url-info">
                    <a
                      href={item.shortUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="short-url"
                    >
                      {item.shortUrl}
                    </a>
                    <div className="original-url">{item.originalUrl}</div>
                    {item.clicks !== undefined && (
                      <div className="clicks">👆 {item.clicks} clicks</div>
                    )}
                  </div>
                  <button
                    onClick={() => handleExpand(item.shortCode)}
                    className="info-btn"
                    title="Get URL info"
                  >
                    ℹ️
                  </button>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* SDK Testing */}
        <section className="test-section">
          <h3>🧪 SDK Integration Tests</h3>
          <button
            onClick={runTests}
            disabled={runningTests}
            className="test-btn"
          >
            {runningTests ? "Running Tests..." : "Run Tests"}
          </button>

          {testResults.length > 0 && (
            <div className="test-results">
              {testResults.map((result, index) => (
                <div
                  key={index}
                  className={`test-result ${result.status.toLowerCase()}`}
                >
                  <span className="test-status">
                    {result.status === "PASS"
                      ? "✅"
                      : result.status === "FAIL"
                      ? "❌"
                      : "⏳"}
                  </span>
                  <span className="test-name">{result.test}</span>
                  <span className="test-details">{result.details}</span>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Integration Instructions */}
        <section className="instructions-section">
          <h3>📖 Integration Guide</h3>
          <div className="code-block">
            <pre>{`// Install the SDK
npm install talisik-shortener

// Import and use
import { TalisikClient } from 'talisik-shortener';

const client = new TalisikClient({
  baseUrl: '${API_URL}'
});

// Shorten a URL
const result = await client.shorten('https://example.com');
console.log(result.shortUrl);

// Expand a URL
const info = await client.expand('abc123');
console.log(info.originalUrl);`}</pre>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
