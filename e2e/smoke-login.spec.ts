import { expect, test } from "@playwright/test";

test("login shows Log out", async ({ page }) => {
  await page.goto("/practice-test-login/");
  await page.locator("#username").fill("student");
  await page.locator("#password").fill("Password123");
  await page.getByRole("button", { name: "Submit" }).click();
  await expect(page.getByRole("link", { name: "Log out" })).toBeVisible();
});
