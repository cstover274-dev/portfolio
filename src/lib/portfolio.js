// Turns the holdings file and the latest closing prices into weights.
import data from '../data/portfolio.json';
import prices from '../data/prices.json';

const COLORS = ['#1F3A5F', '#4F7DB3', '#2E7D6F', '#C1892C', '#8C4A2F', '#6B5B95', '#3E8E9E', '#A65E7A'];
const CASH_COLOR = '#B9C0C8';

export function getPortfolio() {
  const rows = data.holdings.map((h) => {
    const price = prices.closes[h.ticker];
    return { ...h, price, value: h.units * price };
  });
  const cashValue = data.cash.units * (prices.closes[data.cash.heldIn] ?? data.cash.unitPrice);
  const total = rows.reduce((sum, r) => sum + r.value, 0) + cashValue;

  rows.sort((a, b) => b.value - a.value);
  rows.forEach((r, i) => {
    r.weight = (r.value / total) * 100;
    r.color = COLORS[i % COLORS.length];
    // Price return only for now. Dividends get added once the dividend log exists.
    r.sinceTracked = r.tracked.price ? (r.price / r.tracked.price - 1) * 100 : null;
  });

  const cash = { ...data.cash, value: cashValue, weight: (cashValue / total) * 100, color: CASH_COLOR };

  const legs = data.legs.map((leg) => {
    const members = rows.filter((r) => r.leg === leg.id);
    const weight = leg.id === 'cash' ? cash.weight : members.reduce((s, r) => s + r.weight, 0);
    const status = weight < leg.band[0] ? 'under' : weight > leg.band[1] ? 'over' : 'in';
    return { ...leg, weight, status, tickers: members.map((m) => m.ticker) };
  });

  const defense = legs.filter((l) => data.defenseLegs.includes(l.id)).reduce((s, l) => s + l.weight, 0);

  return {
    rows, cash, legs, defense,
    defenseCap: data.defenseCap,
    largest: rows[0],
    launchDate: data.launchDate,
    asOf: prices.asOf,
    benchmark: data.benchmark,
    legName: (id) => data.legs.find((l) => l.id === id)?.name ?? id,
  };
}
