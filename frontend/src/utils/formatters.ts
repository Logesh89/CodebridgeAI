/**
 * Format ISO datetime string to local system time format.
 * Ensures UTC timestamps are parsed correctly into the user's local system timezone.
 */
export function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return '-';
  let normalized = String(dateStr).trim();
  if (!normalized.endsWith('Z') && !normalized.includes('+') && !normalized.includes('-T')) {
    // If string ends with date/time without offset, append Z for UTC parsing
    if (normalized.includes('T')) {
      normalized += 'Z';
    }
  }
  try {
    const d = new Date(normalized);
    if (isNaN(d.getTime())) return String(dateStr);
    return d.toLocaleString();
  } catch {
    return String(dateStr);
  }
}
