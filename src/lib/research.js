// Every holding's write-up is a Markdown file in src/content/holdings.
// The settings at the top of each file (between the --- lines) fill in the page.
const files = import.meta.glob('../content/holdings/*.md', { eager: true });

export const writeups = Object.values(files).map((f) => ({ ...f.frontmatter, Content: f.Content }));
export const writeupFor = (ticker) => writeups.find((w) => w.ticker === ticker);
