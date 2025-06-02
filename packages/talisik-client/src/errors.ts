/**
 * Error classes for Talisik URL Shortener client
 */

/**
 * Custom error class for Talisik-specific errors
 */
export class TalisikError extends Error {
  public readonly status?: number;
  public readonly code?: string;
  public readonly details?: unknown;

  constructor(
    message: string,
    status?: number,
    code?: string,
    details?: unknown
  ) {
    super(message);
    this.name = "TalisikError";
    this.status = status;
    this.code = code;
    this.details = details;

    // Maintains proper stack trace for where our error was thrown (only available on V8)
    if ((Error as any).captureStackTrace) {
      (Error as any).captureStackTrace(this, TalisikError);
    }
  }

  /**
   * Check if this is a network-related error
   */
  isNetworkError(): boolean {
    return !this.status || this.status === 408;
  }

  /**
   * Check if this is a client error (4xx)
   */
  isClientError(): boolean {
    return !!this.status && this.status >= 400 && this.status < 500;
  }

  /**
   * Check if this is a server error (5xx)
   */
  isServerError(): boolean {
    return !!this.status && this.status >= 500 && this.status < 600;
  }

  /**
   * Check if this error indicates the resource was not found
   */
  isNotFound(): boolean {
    return this.status === 404;
  }

  /**
   * Check if this error indicates a timeout
   */
  isTimeout(): boolean {
    return (
      this.status === 408 || this.message.toLowerCase().includes("timeout")
    );
  }

  /**
   * Convert error to JSON-serializable object
   */
  toJSON() {
    return {
      name: this.name,
      message: this.message,
      status: this.status,
      code: this.code,
      details: this.details,
    };
  }
}

/**
 * Error thrown when the Talisik client is not properly configured
 */
export class TalisikConfigError extends TalisikError {
  constructor(message: string) {
    super(message);
    this.name = "TalisikConfigError";
  }
}

/**
 * Error thrown when a URL validation fails
 */
export class TalisikValidationError extends TalisikError {
  constructor(message: string) {
    super(message);
    this.name = "TalisikValidationError";
  }
}
