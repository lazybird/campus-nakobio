import { defineConfig } from 'astro/config';
import node from '@astrojs/node';
import gitCms from '@malihub/git-headless-cms-astro';

// https://astro.build/config
export default defineConfig({
  output: 'hybrid',
  adapter: node({
    mode: 'standalone'
  }),
  integrations: [gitCms()],
  server: {
    port: 3000,
    host: true
  }
});
