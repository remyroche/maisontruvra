import { Page, expect } from '@playwright/test';

export class TestHelpers {
  static async waitForApiResponse(page: Page, urlPattern: string | RegExp, timeout = 10000): Promise<void> {
    await page.waitForResponse(urlPattern, { timeout });
  }

  static async clearBrowserData(page: Page): Promise<void> {
    await page.context().clearCookies();
    await page.context().clearPermissions();
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
  }

  static async mockApiResponse(page: Page, url: string | RegExp, response: any): Promise<void> {
    await page.route(url, async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(response)
      });
    });
  }

  static async interceptApiCall(page: Page, url: string | RegExp): Promise<any> {
    return new Promise((resolve) => {
      page.route(url, async route => {
        const response = await route.fetch();
        const body = await response.json();
        await route.continue();
        resolve(body);
      });
    });
  }

  static generateRandomEmail(): string {
    const timestamp = Date.now();
    const random = Math.random().toString(36).substring(2, 8);
    return `test.${timestamp}.${random}@example.com`;
  }

  static generateRandomString(length: number = 8): string {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
  }

  static generateRandomPhone(): string {
    const prefix = '+33';
    const number = Math.floor(Math.random() * 900000000) + 100000000;
    return `${prefix}${number}`;
  }

  static generateRandomSiret(): string {
    // Generate a 14-digit SIRET number (simplified for testing)
    return Math.floor(Math.random() * 90000000000000) + 10000000000000;
  }

  static async takeScreenshotOnFailure(page: Page, testName: string): Promise<void> {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `${testName}-${timestamp}.png`;
    await page.screenshot({ path: `test-results/screenshots/${filename}` });
  }

  static async waitForPageStable(page: Page, timeout = 5000): Promise<void> {
    // Wait for network to be idle and no loading indicators
    await Promise.all([
      page.waitForLoadState('networkidle', { timeout }),
      page.waitForSelector('[data-testid="loading-spinner"]', { 
        state: 'hidden', 
        timeout: timeout / 2 
      }).catch(() => {
        // Loading spinner might not exist, which is fine
      })
    ]);
  }

  static async scrollToElement(page: Page, selector: string): Promise<void> {
    await page.locator(selector).scrollIntoViewIfNeeded();
  }

  static async waitForElementToBeStable(page: Page, selector: string, timeout = 5000): Promise<void> {
    const element = page.locator(selector);
    await element.waitFor({ state: 'visible', timeout });
    
    // Wait for any animations to complete
    await page.waitForTimeout(300);
  }

  static async fillFormField(page: Page, selector: string, value: string, options?: {
    clear?: boolean;
    delay?: number;
  }): Promise<void> {
    const element = page.locator(selector);
    await element.waitFor({ state: 'visible' });
    
    if (options?.clear !== false) {
      await element.clear();
    }
    
    await element.fill(value);
    
    if (options?.delay) {
      await page.waitForTimeout(options.delay);
    }
  }

  static async selectDropdownOption(page: Page, selector: string, value: string): Promise<void> {
    const dropdown = page.locator(selector);
    await dropdown.waitFor({ state: 'visible' });
    await dropdown.selectOption(value);
  }

  static async checkCheckbox(page: Page, selector: string, checked = true): Promise<void> {
    const checkbox = page.locator(selector);
    await checkbox.waitFor({ state: 'visible' });
    
    const isChecked = await checkbox.isChecked();
    if (isChecked !== checked) {
      await checkbox.click();
    }
  }

  static async verifyToast(page: Page, expectedMessage: string, type: 'success' | 'error' | 'info' = 'success'): Promise<void> {
    const toast = page.locator(`[data-testid="${type}-toast"]`);
    await expect(toast).toBeVisible();
    await expect(toast).toContainText(expectedMessage);
    
    // Wait for toast to disappear
    await expect(toast).toBeHidden({ timeout: 10000 });
  }

  static async verifyPageTitle(page: Page, expectedTitle: string): Promise<void> {
    await expect(page).toHaveTitle(expectedTitle);
  }

  static async verifyUrl(page: Page, expectedPath: string | RegExp): Promise<void> {
    if (typeof expectedPath === 'string') {
      await expect(page).toHaveURL(new RegExp(expectedPath));
    } else {
      await expect(page).toHaveURL(expectedPath);
    }
  }

  static async verifyElementText(page: Page, selector: string, expectedText: string | RegExp): Promise<void> {
    const element = page.locator(selector);
    await expect(element).toHaveText(expectedText);
  }

  static async verifyElementCount(page: Page, selector: string, expectedCount: number): Promise<void> {
    const elements = page.locator(selector);
    await expect(elements).toHaveCount(expectedCount);
  }

  static async verifyElementVisible(page: Page, selector: string): Promise<void> {
    const element = page.locator(selector);
    await expect(element).toBeVisible();
  }

  static async verifyElementHidden(page: Page, selector: string): Promise<void> {
    const element = page.locator(selector);
    await expect(element).toBeHidden();
  }

  static async clickWithRetry(page: Page, selector: string, maxRetries = 3): Promise<void> {
    let retries = 0;
    while (retries < maxRetries) {
      try {
        await page.locator(selector).click();
        return;
      } catch (error) {
        retries++;
        if (retries === maxRetries) {
          throw error;
        }
        await page.waitForTimeout(1000);
      }
    }
  }

  static async typeWithDelay(page: Page, selector: string, text: string, delay = 100): Promise<void> {
    const element = page.locator(selector);
    await element.waitFor({ state: 'visible' });
    await element.type(text, { delay });
  }

  static parsePrice(priceText: string): number {
    return parseFloat(priceText.replace(/[€$£,\s]/g, '')) || 0;
  }

  static formatPrice(amount: number, currency = '€'): string {
    return `${amount.toFixed(2)}${currency}`;
  }

  static async verifyFormValidation(page: Page, fieldSelector: string, expectedMessage: string): Promise<void> {
    const validationMessage = page.locator(`${fieldSelector} + .error-message, ${fieldSelector} ~ .error-message`);
    await expect(validationMessage).toBeVisible();
    await expect(validationMessage).toContainText(expectedMessage);
  }

  static async uploadFile(page: Page, fileInputSelector: string, filePath: string): Promise<void> {
    const fileInput = page.locator(fileInputSelector);
    await fileInput.setInputFiles(filePath);
  }

  static async downloadFile(page: Page, downloadTriggerSelector: string): Promise<string> {
    const [download] = await Promise.all([
      page.waitForEvent('download'),
      page.locator(downloadTriggerSelector).click()
    ]);
    
    const path = await download.path();
    return path || '';
  }

  static async handleDialog(page: Page, action: 'accept' | 'dismiss', message?: string): Promise<void> {
    page.on('dialog', async dialog => {
      if (message) {
        expect(dialog.message()).toContain(message);
      }
      if (action === 'accept') {
        await dialog.accept();
      } else {
        await dialog.dismiss();
      }
    });
  }

  static async dragAndDrop(page: Page, sourceSelector: string, targetSelector: string): Promise<void> {
    const source = page.locator(sourceSelector);
    const target = page.locator(targetSelector);
    
    await source.dragTo(target);
  }

  static async executeWithRetry<T>(
    operation: () => Promise<T>,
    maxRetries = 3,
    delay = 1000
  ): Promise<T> {
    let lastError: Error;
    
    for (let i = 0; i < maxRetries; i++) {
      try {
        return await operation();
      } catch (error) {
        lastError = error as Error;
        if (i < maxRetries - 1) {
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      }
    }
    
    throw lastError!;
  }

  static async waitForCondition(
    condition: () => Promise<boolean>,
    timeout = 10000,
    interval = 500
  ): Promise<void> {
    const startTime = Date.now();
    
    while (Date.now() - startTime < timeout) {
      if (await condition()) {
        return;
      }
      await new Promise(resolve => setTimeout(resolve, interval));
    }
    
    throw new Error(`Condition not met within ${timeout}ms`);
  }
}