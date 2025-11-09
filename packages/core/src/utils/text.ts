/**
 * Text utility functions
 */

/**
 * Truncate text to a maximum length
 */
export function truncate(text: string, maxLength: number): string {
  if (!text || text.length <= maxLength) return text;
  return text.substring(0, maxLength - 3) + '...';
}

/**
 * Strip HTML tags from text
 */
export function stripHtml(html: string): string {
  if (!html) return '';
  return html.replace(/<[^>]*>/g, '');
}

/**
 * Escape special characters for JSON
 */
export function escapeJson(text: string): string {
  if (!text) return '';

  return text
    .replace(/\\/g, '\\\\')
    .replace(/"/g, '\\"')
    .replace(/\n/g, '\\n')
    .replace(/\r/g, '\\r')
    .replace(/\t/g, '\\t');
}

/**
 * Capitalize first letter of each word
 */
export function capitalize(text: string): string {
  if (!text) return '';

  return text
    .split(' ')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

/**
 * Clean whitespace from text
 */
export function cleanWhitespace(text: string): string {
  if (!text) return '';

  return text
    .replace(/\s+/g, ' ') // Replace multiple spaces with single space
    .trim();
}

