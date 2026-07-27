import { defineConfig, devices } from "@playwright/test";

// Developer workstations can reuse an installed Chrome build. CI always installs
// Playwright's immutable Chromium revision before running this configuration.
const localChannel = process.env.CI ? undefined : "chrome";

export default defineConfig({
  testDir: "./tests",
  use: { baseURL: "http://127.0.0.1:4173/noxus", trace: "retain-on-failure" },
  webServer: { command: "npm run build && npx vite preview --host 127.0.0.1", port: 4173, reuseExistingServer: true },
  projects: [
    { name: "desktop", use: { ...devices["Desktop Chrome"], channel: localChannel } },
    {
      name: "tablet",
      use: {
        ...devices["iPad Pro 11"],
        browserName: "chromium",
        channel: localChannel,
      },
    },
  ],
});
