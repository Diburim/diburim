import { defineConfig } from "vite";

export default defineConfig({
  appType: "mpa",
  server: {
    port: 5173,
    open: "/index.html",
    watch: {
      ignored: ["**/_import/**", "**/shulchan_aruch/corpus/**"],
    },
  },
});
