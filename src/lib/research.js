// Every holding's write-up is a Markdown file in src/content/holdings.
// The settings at the top of each file (between the --- lines) fill in the page.
const files = import.meta.glob('../content/holdings/*.md', { eager: true });

// Figures are SVG files in src/charts. A line like [[chart:aar-selloff]] in a write-up places one.
const charts = import.meta.glob('../charts/*.svg', { query: '?raw', import: 'default', eager: true });
const chart = (name) => charts[`../charts/${name}.svg`] ?? '';

export const writeups = Object.values(files).map((f) => ({
  ...f.frontmatter,
  body: async () =>
    (await f.compiledContent()).replace(/<p>\[\[chart:([\w-]+)\]\]<\/p>/g, (_, name) => `<figure>${chart(name)}</figure>`),
}));
export const writeupFor = (ticker) => writeups.find((w) => w.ticker === ticker);
