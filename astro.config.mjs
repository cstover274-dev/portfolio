import { defineConfig } from 'astro/config';

// While the site lives at cstover274-dev.github.io/portfolio, pages sit under /portfolio.
// When a custom domain is attached, set `site` to that domain and `base` to '/'.
export default defineConfig({
  site: 'https://cstover274-dev.github.io',
  base: '/portfolio',
});
