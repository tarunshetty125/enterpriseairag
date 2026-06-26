export function formatPercent(value: number | null | undefined) {
  if (value === null || value === undefined) {
    return "Unavailable";
  }
  return `${(value * 100).toFixed(1)}%`;
}

export function formatNumber(value: number | null | undefined, digits = 2) {
  if (value === null || value === undefined) {
    return "Unavailable";
  }
  return value.toLocaleString("en-US", {
    maximumFractionDigits: digits,
  });
}

export function formatMs(value: number | null | undefined) {
  if (value === null || value === undefined) {
    return "Unavailable";
  }
  return `${value.toFixed(1)} ms`;
}

export function getNumberMetric(
  metrics: Record<string, unknown>,
  key: string,
): number | null {
  const value = metrics[key];
  return typeof value === "number" ? value : null;
}

export function getRecordMetric(
  metrics: Record<string, unknown>,
  key: string,
): Record<string, unknown> {
  const value = metrics[key];
  if (value && typeof value === "object" && !Array.isArray(value)) {
    return value as Record<string, unknown>;
  }
  return {};
}
