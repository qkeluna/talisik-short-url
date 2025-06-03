import React, { useState, useEffect } from "react";
import { TalisikClient } from "talisik-shortener";
import "./App.css";

// Replace with your production URL
// const API_URL = "https://talisik-short-url-qkeluna8941-ktpw2srp.leapcell.dev";
const API_URL = "https://go.downlodr.com"; // Custom subdomain (safer than root domain)

// Fallback for testing during domain setup:
// const API_URL = "https://talisik-short-url-qkeluna8941-ktpw2srp.leapcell.dev";

interface ShortenedUrl {
  shortCode: string;
  shortUrl: string;
  customDomainUrl: string;
  originalUrl: string;
  clicks?: number;
  createdAt?: string;
}

interface TestResult {
  test: string;
  status: "PASS" | "FAIL" | "RUNNING";
  details: string;
}

interface UrlTableRow {
  original_url: string;
  short_code: string;
  expires_at: string | null;
  click_count: number;
  is_active: boolean;
  created_at: string;
}

function App() {
  const [client] = useState(() => new TalisikClient({ baseUrl: API_URL }));
  const [url, setUrl] = useState(
    "https://github.com/frederickluna/talisik-short-url"
  );
  const [customCode, setCustomCode] = useState("");
  const [expiresHours, setExpiresHours] = useState("");
  const [shortenedUrls, setShortenedUrls] = useState<ShortenedUrl[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<{
    totalUrls: number;
    totalClicks: number;
  } | null>(null);
  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [runningTests, setRunningTests] = useState(false);
  const [urlTable, setUrlTable] = useState<UrlTableRow[]>([]);
  const [loadingTable, setLoadingTable] = useState(false);

  // Load stats and table data on component mount
  useEffect(() => {
    loadStats();
    loadUrlTable();
  }, []);

  const loadStats = async () => {
    try {
      const statsData = await client.getStats();
      setStats(statsData);
    } catch (err) {
      console.error("Failed to load stats:", err);
    }
  };

  const loadUrlTable = async () => {
    setLoadingTable(true);
    try {
      const urlsData = await client.getAllUrls();
      setUrlTable(urlsData);
    } catch (err) {
      console.error("Failed to load URL table:", err);
    } finally {
      setLoadingTable(false);
    }
  };

  const handleShorten = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const options: any = {};
      if (customCode) options.customCode = customCode;
      if (expiresHours) options.expiresHours = parseInt(expiresHours);

      const result = await client.shorten({ url, ...options });

      // Debug log to check what the API returns
      console.log("API Response:", result);
      console.log("Using API_URL:", API_URL);

      const newUrl: ShortenedUrl = {
        shortCode: result.shortCode,
        shortUrl: `${API_URL}/${result.shortCode}`,
        customDomainUrl: `https://downlodr.com/${result.shortCode}`,
        originalUrl: url,
      };

      setShortenedUrls((prev) => [newUrl, ...prev]);
      setUrl("");
      setCustomCode("");
      setExpiresHours("");
      await loadStats(); // Refresh stats
      await loadUrlTable(); // Refresh table data
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to shorten URL");
    } finally {
      setLoading(false);
    }
  };

  const handleExpand = async (shortCode: string) => {
    try {
      const info = await client.getUrlInfo(shortCode);
      if (info) {
        setShortenedUrls((prev) =>
          prev.map((url) =>
            url.shortCode === shortCode
              ? { ...url, clicks: info.clickCount, createdAt: info.createdAt }
              : url
          )
        );
      }
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
      const result = await client.shorten({ url: "https://example.com/test" });
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
      const result = await client.shorten({
        url: "https://example.com/custom",
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
        if (result) {
          addTestResult("URL Expansion", "PASS", `Original: ${result}`);
        } else {
          addTestResult("URL Expansion", "FAIL", "No URL returned");
        }
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
      await client.shorten({ url: "invalid-url" });
      addTestResult("Error Handling", "FAIL", "Should have thrown an error");
    } catch (err) {
      addTestResult("Error Handling", "PASS", "Properly rejects invalid URLs");
    }

    // Test 6: URL with Expiration
    addTestResult("URL Expiration", "RUNNING", "Testing...");
    try {
      const result = await client.shorten({
        url: "https://example.com/expires",
        expiresHours: 24,
      });

      // Get URL info to check expiration
      const info = await client.getUrlInfo(result.shortCode);
      if (info && info.expiresAt) {
        const expiresAt = new Date(info.expiresAt);
        const now = new Date();
        const hoursUntilExpiry =
          (expiresAt.getTime() - now.getTime()) / (1000 * 60 * 60);

        if (hoursUntilExpiry > 23 && hoursUntilExpiry <= 24) {
          addTestResult(
            "URL Expiration",
            "PASS",
            `Expires in ${Math.round(hoursUntilExpiry)} hours`
          );
        } else {
          addTestResult(
            "URL Expiration",
            "FAIL",
            `Expiration time incorrect: ${Math.round(hoursUntilExpiry)} hours`
          );
        }
      } else {
        addTestResult("URL Expiration", "FAIL", "No expiration info found");
      }
    } catch (err) {
      addTestResult(
        "URL Expiration",
        "FAIL",
        err instanceof Error ? err.message : "Unknown error"
      );
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
              <input
                type="number"
                value={expiresHours}
                onChange={(e) => setExpiresHours(e.target.value)}
                placeholder="Expires in hours (e.g. 24)"
                min="1"
                max="8760"
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

        {/* URL Table */}
        <section className="table-section">
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "1rem",
            }}
          >
            <h3>📋 URL List</h3>
            <button
              onClick={loadUrlTable}
              disabled={loadingTable}
              className="refresh-btn"
              title="Refresh URL list"
            >
              {loadingTable ? "⏳ Refreshing..." : "🔄 Refresh"}
            </button>
          </div>
          {loadingTable ? (
            <div className="loading">Loading table data...</div>
          ) : (
            <div className="table-container">
              <table className="url-table">
                <thead>
                  <tr>
                    <th>Original URL</th>
                    <th>Short Code</th>
                    <th>Expires At</th>
                    <th>Clicks</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {urlTable.map((row, index) => (
                    <tr key={index}>
                      <td className="url-cell" title={row.original_url}>
                        {row.original_url.length > 50
                          ? `${row.original_url.substring(0, 50)}...`
                          : row.original_url}
                      </td>
                      <td className="code-cell">
                        <span className="short-code">{row.short_code}</span>
                      </td>
                      <td className="expires-cell">
                        {row.expires_at ? (
                          new Date(row.expires_at).toLocaleDateString()
                        ) : (
                          <span className="no-expiry">No expiry</span>
                        )}
                      </td>
                      <td className="clicks-cell">
                        <span className="click-count">{row.click_count}</span>
                      </td>
                      <td className="status-cell">
                        <span
                          className={`status ${
                            row.is_active ? "active" : "inactive"
                          }`}
                        >
                          {row.is_active ? "✅ Active" : "❌ Inactive"}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {urlTable.length === 0 && (
                <div className="empty-table">No URLs found</div>
              )}
            </div>
          )}
        </section>

        {/* Demo URLs Section */}
        <section className="urls-section">
          <h3>🔗 Demo URLs (Production Examples)</h3>
          <p
            style={{ marginBottom: "1rem", color: "#666", fontSize: "0.9rem" }}
          >
            These are example URLs from your production environment. Click the
            info button to test the expand functionality.
          </p>
          <div className="urls-list">
            {/* First Demo - NDPOBoE */}
            <div className="url-item">
              <div className="url-info">
                {/* Custom Domain URL */}
                <div style={{ marginBottom: "0.75rem" }}>
                  <span
                    className="short-url"
                    style={{ color: "#f39c12", fontSize: "1.1rem" }}
                    title="Custom domain (available after CNAME setup)"
                  >
                    https://downlodr.com/NDPOBoE
                  </span>
                  <div
                    style={{
                      fontSize: "0.8rem",
                      color: "#f39c12",
                      marginTop: "0.25rem",
                    }}
                  >
                    🎯 Custom domain format
                  </div>
                </div>

                {/* Production URL */}
                <div style={{ marginBottom: "0.5rem" }}>
                  <a
                    href={`${API_URL}/NDPOBoE`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="short-url"
                    style={{ fontSize: "1.1rem" }}
                  >
                    {API_URL}/NDPOBoE
                  </a>
                  <div
                    style={{
                      fontSize: "0.8rem",
                      color: "#27ae60",
                      marginTop: "0.25rem",
                    }}
                  >
                    ✅ Production URL (working now) - 1 click
                  </div>
                </div>

                {/* Original URL */}
                <div className="original-url" style={{ marginTop: "0.75rem" }}>
                  https://docs.google.com/spreadsheets/d/1nmt7x6_z6TcOkJpzVbmPAz6Bh2teS3F5a628Ug6HEHM/edit?usp=sharing
                </div>
              </div>
              <button
                onClick={async () => {
                  try {
                    const result = await client.expand("NDPOBoE");
                    if (result) {
                      alert(`✅ Expand successful!\nOriginal URL: ${result}`);
                    } else {
                      alert("❌ No URL found");
                    }
                  } catch (err) {
                    alert(
                      `❌ Error: ${
                        err instanceof Error ? err.message : "Unknown error"
                      }`
                    );
                  }
                }}
                className="info-btn"
                title="Test expand functionality"
              >
                🔄
              </button>
            </div>

            {/* Second Demo - X3qhq1a */}
            <div className="url-item">
              <div className="url-info">
                {/* Custom Domain URL */}
                <div style={{ marginBottom: "0.75rem" }}>
                  <span
                    className="short-url"
                    style={{ color: "#f39c12", fontSize: "1.1rem" }}
                    title="Custom domain (available after CNAME setup)"
                  >
                    https://downlodr.com/X3qhq1a
                  </span>
                  <div
                    style={{
                      fontSize: "0.8rem",
                      color: "#f39c12",
                      marginTop: "0.25rem",
                    }}
                  >
                    🎯 Custom domain format
                  </div>
                </div>

                {/* Production URL */}
                <div style={{ marginBottom: "0.5rem" }}>
                  <a
                    href={`${API_URL}/X3qhq1a`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="short-url"
                    style={{ fontSize: "1.1rem" }}
                  >
                    {API_URL}/X3qhq1a
                  </a>
                  <div
                    style={{
                      fontSize: "0.8rem",
                      color: "#27ae60",
                      marginTop: "0.25rem",
                    }}
                  >
                    ✅ Production URL (working now) - 2 clicks
                  </div>
                </div>

                {/* Original URL */}
                <div className="original-url" style={{ marginTop: "0.75rem" }}>
                  https://github.com/frederickluna/talisik-short-url
                </div>
              </div>
              <button
                onClick={async () => {
                  try {
                    const result = await client.expand("X3qhq1a");
                    if (result) {
                      alert(`✅ Expand successful!\nOriginal URL: ${result}`);
                    } else {
                      alert("❌ No URL found");
                    }
                  } catch (err) {
                    alert(
                      `❌ Error: ${
                        err instanceof Error ? err.message : "Unknown error"
                      }`
                    );
                  }
                }}
                className="info-btn"
                title="Test expand functionality"
              >
                🔄
              </button>
            </div>
          </div>
        </section>

        {/* Shortened URLs */}
        {shortenedUrls.length > 0 && (
          <section className="urls-section">
            <h3>📋 Shortened URLs</h3>
            <div className="urls-list">
              {shortenedUrls.map((item, index) => (
                <div key={index} className="url-item">
                  <div className="url-info">
                    {/* Custom Domain URL */}
                    <div style={{ marginBottom: "0.75rem" }}>
                      <span
                        className="short-url"
                        style={{ color: "#f39c12", fontSize: "1.1rem" }}
                        title="Custom domain (available after CNAME setup)"
                      >
                        {item.customDomainUrl}
                      </span>
                      <div
                        style={{
                          fontSize: "0.8rem",
                          color: "#f39c12",
                          marginTop: "0.25rem",
                        }}
                      >
                        🎯 Custom domain format
                      </div>
                    </div>

                    {/* Production URL */}
                    <div style={{ marginBottom: "0.5rem" }}>
                      <a
                        href={item.shortUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="short-url"
                        style={{ fontSize: "1.1rem" }}
                      >
                        {item.shortUrl}
                      </a>
                      <div
                        style={{
                          fontSize: "0.8rem",
                          color: "#27ae60",
                          marginTop: "0.25rem",
                        }}
                      >
                        ✅ Production URL (working now)
                      </div>
                    </div>

                    {/* Original URL */}
                    <div
                      className="original-url"
                      style={{ marginTop: "0.75rem" }}
                    >
                      {item.originalUrl}
                    </div>

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
