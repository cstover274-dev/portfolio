// Small helpers shared by every page.
export const base = import.meta.env.BASE_URL.replace(/\/$/, '');
export const href = (path) => base + path;

export const fmtDate = (iso) =>
  new Date(iso + 'T12:00:00Z').toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric', timeZone: 'UTC',
  });

export const pct = (n, digits = 1) => n.toFixed(digits) + '%';
export const usd = (n) =>
  '$' + n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
