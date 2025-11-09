/**
 * Date utility functions
 */

/**
 * Format a date to ISO 8601 format (YYYY-MM-DD)
 */
export function formatDate(date: string | Date): string {
  if (!date) return '';

  try {
    const dateObj = typeof date === 'string' ? new Date(date) : date;

    if (isNaN(dateObj.getTime())) {
      return '';
    }

    return dateObj.toISOString().split('T')[0];
  } catch {
    return '';
  }
}

/**
 * Format a date to ISO 8601 datetime format (YYYY-MM-DDTHH:mm:ss)
 */
export function formatDateTime(date: string | Date): string {
  if (!date) return '';

  try {
    const dateObj = typeof date === 'string' ? new Date(date) : date;

    if (isNaN(dateObj.getTime())) {
      return '';
    }

    return dateObj.toISOString();
  } catch {
    return '';
  }
}

/**
 * Validate if a string is a valid date
 */
export function isValidDate(date: string): boolean {
  if (!date) return false;

  try {
    const dateObj = new Date(date);
    return !isNaN(dateObj.getTime());
  } catch {
    return false;
  }
}

/**
 * Format duration to ISO 8601 duration format (PT1H30M)
 */
export function formatDuration(minutes: number): string {
  if (!minutes || minutes <= 0) return '';

  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;

  let duration = 'PT';
  if (hours > 0) duration += `${hours}H`;
  if (mins > 0) duration += `${mins}M`;

  return duration;
}

/**
 * Parse ISO 8601 duration to minutes
 */
export function parseDuration(duration: string): number {
  if (!duration) return 0;

  const match = duration.match(/PT(?:(\d+)H)?(?:(\d+)M)?/);
  if (!match) return 0;

  const hours = parseInt(match[1] || '0', 10);
  const minutes = parseInt(match[2] || '0', 10);

  return hours * 60 + minutes;
}

