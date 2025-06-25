import { Page, Locator } from '@playwright/test';
import { BasePage } from './BasePage';

export class ShopPage extends BasePage {
  constructor(page: Page) {
    super(page);
  }

  // Filter and sort elements
  get filterSidebar(): Locator {
    return this.page.locator('[data-testid="filter-sidebar"]');
  }

  get categoryFilters(): Locator {
    return this.page.locator('[data-testid="category-filter"]');
  }

  get priceRangeFilter(): Locator {
    return this.page.locator('[data-testid="price-range-filter"]');
  }

  get sortDropdown(): Locator {
    return this.page.locator('[data-testid="sort-dropdown"]');
  }

  get clearFiltersButton(): Locator {
    return this.page.locator('[data-testid="clear-filters"]');
  }

  // Product grid elements
  get productGrid(): Locator {
    return this.page.locator('[data-testid="product-grid"]');
  }

  get productCards(): Locator {
    return this.page.locator('[data-testid="product-card"]');
  }

  get productTitles(): Locator {
    return this.page.locator('[data-testid="product-title"]');
  }

  get productPrices(): Locator {
    return this.page.locator('[data-testid="product-price"]');
  }

  get productImages(): Locator {
    return this.page.locator('[data-testid="product-image"]');
  }

  get addToCartButtons(): Locator {
    return this.page.locator('[data-testid="add-to-cart-button"]');
  }

  get quickViewButtons(): Locator {
    return this.page.locator('[data-testid="quick-view-button"]');
  }

  get wishlistButtons(): Locator {
    return this.page.locator('[data-testid="wishlist-button"]');
  }

  // Pagination elements
  get pagination(): Locator {
    return this.page.locator('[data-testid="pagination"]');
  }

  get paginationPrevious(): Locator {
    return this.page.locator('[data-testid="pagination-previous"]');
  }

  get paginationNext(): Locator {
    return this.page.locator('[data-testid="pagination-next"]');
  }

  get paginationNumbers(): Locator {
    return this.page.locator('[data-testid="pagination-number"]');
  }

  // Results and loading states
  get resultsCount(): Locator {
    return this.page.locator('[data-testid="results-count"]');
  }

  get noResultsMessage(): Locator {
    return this.page.locator('[data-testid="no-results"]');
  }

  get loadingSpinner(): Locator {
    return this.page.locator('[data-testid="loading-spinner"]');
  }

  // Quick view modal
  get quickViewModal(): Locator {
    return this.page.locator('[data-testid="quick-view-modal"]');
  }

  get quickViewCloseButton(): Locator {
    return this.page.locator('[data-testid="quick-view-close"]');
  }

  // Actions
  async visit(): Promise<void> {
    await this.navigateTo('/shop');
    await this.waitForPageLoad();
  }

  async filterByCategory(category: string): Promise<void> {
    const categoryFilter = this.categoryFilters.filter({ hasText: category });
    await categoryFilter.click();
    await this.waitForProductsToLoad();
  }

  async setPriceRange(min: number, max: number): Promise<void> {
    const minInput = this.priceRangeFilter.locator('[data-testid="price-min"]');
    const maxInput = this.priceRangeFilter.locator('[data-testid="price-max"]');
    
    await minInput.fill(min.toString());
    await maxInput.fill(max.toString());
    await maxInput.press('Enter');
    await this.waitForProductsToLoad();
  }

  async sortBy(option: string): Promise<void> {
    await this.sortDropdown.selectOption(option);
    await this.waitForProductsToLoad();
  }

  async clearAllFilters(): Promise<void> {
    await this.clearFiltersButton.click();
    await this.waitForProductsToLoad();
  }

  async clickProduct(index: number = 0): Promise<void> {
    await this.productCards.nth(index).click();
  }

  async addProductToCart(index: number = 0): Promise<void> {
    await this.addToCartButtons.nth(index).click();
  }

  async addProductToWishlist(index: number = 0): Promise<void> {
    await this.wishlistButtons.nth(index).click();
  }

  async openQuickView(index: number = 0): Promise<void> {
    await this.quickViewButtons.nth(index).click();
    await this.quickViewModal.waitFor({ state: 'visible' });
  }

  async closeQuickView(): Promise<void> {
    await this.quickViewCloseButton.click();
    await this.quickViewModal.waitFor({ state: 'hidden' });
  }

  async goToPage(pageNumber: number): Promise<void> {
    const pageButton = this.paginationNumbers.filter({ hasText: pageNumber.toString() });
    await pageButton.click();
    await this.waitForProductsToLoad();
  }

  async goToNextPage(): Promise<void> {
    if (await this.paginationNext.isEnabled()) {
      await this.paginationNext.click();
      await this.waitForProductsToLoad();
    }
  }

  async goToPreviousPage(): Promise<void> {
    if (await this.paginationPrevious.isEnabled()) {
      await this.paginationPrevious.click();
      await this.waitForProductsToLoad();
    }
  }

  private async waitForProductsToLoad(): Promise<void> {
    // Wait for loading spinner to disappear
    await this.loadingSpinner.waitFor({ state: 'hidden', timeout: 10000 });
    // Wait for products to be visible
    await this.productGrid.waitFor({ state: 'visible' });
  }

  // Assertion helpers
  async getProductsCount(): Promise<number> {
    return await this.productCards.count();
  }

  async getResultsCountText(): Promise<string> {
    return await this.resultsCount.textContent() || '';
  }

  async hasNoResults(): Promise<boolean> {
    return await this.noResultsMessage.isVisible();
  }

  async isQuickViewOpen(): Promise<boolean> {
    return await this.quickViewModal.isVisible();
  }

  async getProductTitle(index: number = 0): Promise<string> {
    return await this.productTitles.nth(index).textContent() || '';
  }

  async getProductPrice(index: number = 0): Promise<string> {
    return await this.productPrices.nth(index).textContent() || '';
  }

  async isProductInWishlist(index: number = 0): Promise<boolean> {
    const wishlistButton = this.wishlistButtons.nth(index);
    return await wishlistButton.getAttribute('aria-pressed') === 'true';
  }

  async isPaginationVisible(): Promise<boolean> {
    return await this.pagination.isVisible();
  }

  async canGoToNextPage(): Promise<boolean> {
    return await this.paginationNext.isEnabled();
  }

  async canGoToPreviousPage(): Promise<boolean> {
    return await this.paginationPrevious.isEnabled();
  }
}