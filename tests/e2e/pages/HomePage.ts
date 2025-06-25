import { Page, Locator } from '@playwright/test';
import { BasePage } from './BasePage';

export class HomePage extends BasePage {
  constructor(page: Page) {
    super(page);
  }

  // Home page specific elements
  get heroSection(): Locator {
    return this.page.locator('[data-testid="hero-section"]');
  }

  get heroTitle(): Locator {
    return this.page.locator('[data-testid="hero-title"]');
  }

  get heroSubtitle(): Locator {
    return this.page.locator('[data-testid="hero-subtitle"]');
  }

  get ctaButton(): Locator {
    return this.page.locator('[data-testid="cta-button"]');
  }

  get featuredProducts(): Locator {
    return this.page.locator('[data-testid="featured-products"]');
  }

  get productCards(): Locator {
    return this.page.locator('[data-testid="product-card"]');
  }

  get newsletterSection(): Locator {
    return this.page.locator('[data-testid="newsletter-section"]');
  }

  get testimonialsSection(): Locator {
    return this.page.locator('[data-testid="testimonials-section"]');
  }

  // Navigation menu items
  get shopLink(): Locator {
    return this.page.locator('[data-testid="nav-shop"]');
  }

  get notreMaisonLink(): Locator {
    return this.page.locator('[data-testid="nav-notre-maison"]');
  }

  get journalLink(): Locator {
    return this.page.locator('[data-testid="nav-journal"]');
  }

  get professionnelsLink(): Locator {
    return this.page.locator('[data-testid="nav-professionnels"]');
  }

  // Actions
  async visit(): Promise<void> {
    await this.navigateTo('/');
    await this.waitForPageLoad();
  }

  async clickShop(): Promise<void> {
    await this.shopLink.click();
  }

  async clickNotreMaison(): Promise<void> {
    await this.notreMaisonLink.click();
  }

  async clickJournal(): Promise<void> {
    await this.journalLink.click();
  }

  async clickProfessionnels(): Promise<void> {
    await this.professionnelsLink.click();
  }

  async clickCTA(): Promise<void> {
    await this.ctaButton.click();
  }

  async clickFeaturedProduct(index: number = 0): Promise<void> {
    await this.productCards.nth(index).click();
  }

  async signupForNewsletter(email: string): Promise<void> {
    const emailInput = this.newsletterSection.locator('input[type="email"]');
    const submitButton = this.newsletterSection.locator('button[type="submit"]');
    
    await emailInput.fill(email);
    await submitButton.click();
  }

  // Assertions helpers
  async isHeroVisible(): Promise<boolean> {
    return await this.heroSection.isVisible();
  }

  async getFeaturedProductsCount(): Promise<number> {
    return await this.productCards.count();
  }

  async isNewsletterSectionVisible(): Promise<boolean> {
    return await this.newsletterSection.isVisible();
  }
}