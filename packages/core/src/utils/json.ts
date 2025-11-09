/**
 * JSON utility functions
 */

/**
 * Safely parse JSON string
 */
export function safeJsonParse<T = unknown>(json: string): T | null {
  try {
    return JSON.parse(json) as T;
  } catch {
    return null;
  }
}

/**
 * Safely stringify object to JSON
 */
export function safeJsonStringify(obj: unknown, pretty = false): string {
  try {
    return JSON.stringify(obj, null, pretty ? 2 : 0);
  } catch {
    return '';
  }
}

/**
 * Deep clone an object using JSON
 */
export function deepClone<T>(obj: T): T {
  try {
    return JSON.parse(JSON.stringify(obj)) as T;
  } catch {
    return obj;
  }
}

/**
 * Check if a value is a valid JSON string
 */
export function isValidJson(str: string): boolean {
  try {
    JSON.parse(str);
    return true;
  } catch {
    return false;
  }
}

