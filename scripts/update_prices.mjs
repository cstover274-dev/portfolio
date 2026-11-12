// Daily update: pulls closing prices, then rebuilds the performance history.
//
//   ALPHAVANTAGE_KEY=... node scripts/update_prices.mjs
//
// Free Alpha Vantage keys allow 25 requests a day. This uses one per ticker for prices,
// plus one per ticker for dividends on Mondays only.
//
// Returns are total return. A dividend counts as cash from its ex-dividend date, for the
// holdings and the benchmark funds alike.
//
// Not handled yet: trades and deposits. Units are assumed unchanged since `unitsFrom`
// (or the launch date). When a trade happens, update portfolio.json and set `unitsFrom`.
import fs from 'node:fs/promises';

const DATA = new URL('../src/data/', import.meta.url);
const read = async (name) => JSON.parse(await fs.readFile(new URL(name, DATA), 'utf8'));
const write = (name, value) => fs.writeFile(new URL(name, DATA), JSON.stringify(value, null, 2) + '\n');
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const round = (n, digits = 4) => Number(n.toFixed(digits));

async function alphaVantage(params) {
  const query = new URLSearchParams({ ...params, apikey: process.env.ALPHAVANTAGE_KEY });
  const response = await fetch(`https://www.alphavantage.co/query?${query}`);
  const json = await response.json();
  // Never print Alpha Vantage's own message: it can echo the key back.
  if (!response.ok || json.Information || json.Note || json['Error Message']) {
    throw new Error(`no data for ${params.symbol} (${params.function}); probably the daily request limit`);
  }
  return json;
}

export function tickersIn(portfolio) {
  return [...new Set([
    ...portfolio.holdings.map((h) => h.ticker),
    portfolio.cash.heldIn,
    ...portfolio.benchmark.blend.map((b) => b.ticker),
    portfolio.benchmark.market,
  ])];
}

// series: { TICKER: { 'YYYY-MM-DD': close } }, dividends: { TICKER: [{ exDate, amount }] }
export function buildHistory({ portfolio, series, dividends, previous = [] }) {
  const launch = portfolio.launchDate;
  const unitsFrom = portfolio.unitsFrom ?? launch;
  const start = portfolio.benchmark.start.prices;
  const tickers = tickersIn(portfolio);

  // Only days on or after launch where every ticker has a close.
  const dates = Object.keys(series[tickers[0]])
    .filter((d) => d >= launch && tickers.every((t) => series[t][d] !== undefined))
    .sort();

  const paid = (ticker, date) =>
    (dividends[ticker] ?? []).filter((d) => d.exDate > launch && d.exDate <= date).reduce((sum, d) => sum + d.amount, 0);
  const worth = (ticker, date) => series[ticker][date] + paid(ticker, date);

  const byDate = new Map(previous.map((point) => [point.date, point]));
  for (const date of dates) {
    const old = byDate.get(date);
    const value =
      portfolio.holdings.reduce((sum, h) => sum + h.units * worth(h.ticker, date), 0) +
      portfolio.cash.units * worth(portfolio.cash.heldIn, date);
    const blend = portfolio.benchmark.blend.reduce((sum, b) => sum + b.weight * (worth(b.ticker, date) / start[b.ticker]), 0);
    const market = (worth(portfolio.benchmark.market, date) / start[portfolio.benchmark.market]) * 100;
    byDate.set(date, {
      date,
      portfolio: date >= unitsFrom || !old ? round(value) : old.portfolio,
      blend: round(blend),
      market: round(market),
    });
  }
  const history = [...byDate.values()].sort((a, b) => a.date.localeCompare(b.date));
  const last = dates.at(-1);
  const closes = last ? Object.fromEntries(tickers.map((t) => [t, series[t][last]])) : null;
  return { history, asOf: last, closes };
}

async function main() {
  if (!process.env.ALPHAVANTAGE_KEY) throw new Error('ALPHAVANTAGE_KEY is not set');
  const portfolio = await read('portfolio.json');
  const tickers = tickersIn(portfolio);

  const series = {};
  for (const symbol of tickers) {
    const json = await alphaVantage({ function: 'TIME_SERIES_DAILY', symbol, outputsize: 'compact' });
    series[symbol] = Object.fromEntries(
      Object.entries(json['Time Series (Daily)']).map(([date, bar]) => [date, Number(bar['4. close'])]),
    );
    await sleep(1500);
  }

  let dividends = await read('dividends.json');
  const monday = new Date().getUTCDay() === 1;
  if (monday || process.env.FETCH_DIVIDENDS === '1') {
    try {
      const fresh = {};
      for (const symbol of tickers) {
        const json = await alphaVantage({ function: 'DIVIDENDS', symbol });
        fresh[symbol] = (json.data ?? [])
          .filter((d) => d.ex_dividend_date > portfolio.launchDate)
          .map((d) => ({ exDate: d.ex_dividend_date, amount: Number(d.amount) }))
          .sort((a, b) => a.exDate.localeCompare(b.exDate));
        await sleep(1500);
      }
      dividends = fresh;
      await write('dividends.json', dividends);
    } catch (error) {
      console.warn(`Dividends not refreshed: ${error.message}. Keeping the saved ones.`);
    }
  }

  const { history, asOf, closes } = buildHistory({ portfolio, series, dividends, previous: await read('history.json') });
  if (!asOf) throw new Error('no trading days found on or after the launch date');
  await write('history.json', history);
  await write('prices.json', { asOf, note: 'Closing prices.', closes });
  console.log(`Prices as of ${asOf}. History has ${history.length} day(s).`);
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((error) => {
    // Leave the saved data untouched and let the site rebuild with what it has.
    console.warn(`Update skipped: ${error.message}`);
  });
}
