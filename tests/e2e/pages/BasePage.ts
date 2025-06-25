import { Page, Locator } from '@playwright/test';

export class BasePage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  // Common navigation elements
  get navigationMenu(): Locator {
    return this.page.locator('nav[data-testid="main-navigation"]');
  }

  get userMenuToggle(): Locator {
    return this.page.locator('[data-testid="user-menu-toggle"]');
  }

  get loginButton(): Locator {
    return this.page.locator('[data-testid="login-button"]');
  }

  get logoutButton(): Locator {
    return this.page.locator('[data-testid="logout-button"]');
  }

  get cartIcon(): Locator {
    return this.page.locator('[data-testid="cart-icon"]');
  }

  get searchInput(): Locator {
    return this.page.locator('[data-testid="search-input"]');
  }

  get searchButton(): Locator {
    return this.page.locator('[data-testid="search-button"]');
  }

  // Common footer elements
  get footer(): Locator {
    return this.page.locator('footer');
  }

  get newsletterSignupForm(): Locator {
    return this.page.locator('[data-testid="newsletter-signup"]');
  }

  // Common actions
  async navigateTo(path: string): Promise<void> {
    await this.page.goto(path);
  }

  async clickLogin(): Promise<void> {
    await this.loginButton.click();
  }

  async clickLogout(): Promise<void> {
    await this.logoutButton.click();
  }

  async search(query: string): Promise<void> {
    await this.searchInput.fill(query);
    await this.searchButton.click();
  }

  async openCart(): Promise<void> {
    await this.cartIcon.click();
  }

  async waitForPageLoad(): Promise<void> {
    await this.page.waitForLoadState('networkidle');
  }

  // Utility methods
  async getPageTitle(): Promise<string> {
    return await this.page.title();
  }

  async getCurrentUrl(): Promise<string> {
    return this.page.url();
  }

  async takeScreenshot(name: string): Promise<void> {
    await this.page.screenshot({ path: `screenshots/${name}.png` });
  }
}