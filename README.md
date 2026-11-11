# Portfolio

The code and research behind my equity portfolio site: a real-money, long-only portfolio, with a written thesis for every holding.

## How it's organized

- `src/content/holdings/` has one text file per holding. The thesis, the "right when" and "wrong if" signals and the update log all live there.
- `src/data/portfolio.json` lists the holdings, the target allocation and the benchmarks. Positions are stored as scaled units, so the site shows weights and returns but no dollar amounts.
- `src/data/prices.json` holds the latest closing prices.
- `src/pages/` has the page templates.
- `src/charts/` has the figures used in write-ups, drawn by the scripts in `scripts/`.

## Editing a write-up

Open the holding's file in `src/content/holdings/`, change the text between the quotes, and save. Published research isn't rewritten after the fact. Changes go in the `log` list with a date.

## Running it locally

```
npm install
npm run dev
```

Nothing on this site is investment advice.
