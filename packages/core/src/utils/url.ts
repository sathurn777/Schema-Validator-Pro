/**
 * URL utility functions
 */

/**
 * Normalize a URL to ensure it's valid and properly formatted
 */
export function normalizeUrl(url: string): string {
  if (!url) return '';

  // Trim whitespace
  url = url.trim();

  // If it doesn't start with http:// or https://, add https://
  if (!url.match(/^https?:\/\//i)) {
    url = 'https://' + url;
  }

  try {
    const urlObj = new URL(url);
    return urlObj.href;
  } catch {
    // If URL is invalid, return as-is
    return url;
  }
}

/**
 * Validate if a string is a valid URL
 */
export function isValidUrl(url: string): boolean {
  if (!url) return false;

  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

/**
 * Extract domain from URL
 */
export function extractDomain(url: string): string {
  try {
    const urlObj = new URL(url);
    return urlObj.hostname;
  } catch {
    return '';
  }
}

