import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

test("English and Arabic builder navigation is responsive", async ({ page }) => {
  await page.route("**/api/method/frappe.auth.get_logged_user", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ message: "Administrator" }) });
  });
  await page.route("**/api/v2/method/noxus_core.api.v1.catalog", async (route) => {
    await route.fulfill({ status: 503, contentType: "application/json", body: JSON.stringify({ exception: "offline test catalog" }) });
  });
  await page.goto("/noxus/builder");
  await expect(page.getByRole("heading", { name: "Solution Builder" })).toBeVisible();
  const englishAccessibility = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21aa", "wcag22aa"])
    .analyze();
  expect(englishAccessibility.violations).toEqual([]);
  await page.getByRole("button", { name: "2. Modules" }).click();
  await expect(page.getByText("NOXUS Core", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "العربية" }).click();
  await expect(page.locator("html")).toHaveAttribute("dir", "rtl");
  await expect(page.getByRole("heading", { name: "منشئ الحلول" })).toBeVisible();
  const arabicAccessibility = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21aa", "wcag22aa"])
    .analyze();
  expect(arabicAccessibility.violations).toEqual([]);
});
