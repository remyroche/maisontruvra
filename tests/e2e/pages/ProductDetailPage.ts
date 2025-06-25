import { Page, Locator } from '@playwright/test';
import { BasePage } from './BasePage';

export class ProductDetailPage extends BasePage {
  constructor(page: Page) {
    super(page);
  }

  // Product information elements
  get productTitle(): Locator {
    return this.page.locator('[data-testid="product-title"]');
  }

  get productPrice(): Locator {
    return this.page.locator('[data-testid="product-price"]');
  }

  get productDescription(): Locator {
    return this.page.locator('[data-testid="product-description"]');
  }

  get productImages(): Locator {
    return this.page.locator('[data-testid="product-images"]');
  }

  get mainProductImage(): Locator {
    return this.page.locator('[data-testid="main-product-image"]');
  }

  get thumbnailImages(): Locator {
    return this.page.locator('[data-testid="thumbnail-image"]');
  }

  // Product actions
  get quantityInput(): Locator {
    return this.page.locator('[data-testid="quantity-input"]');
  }

  get quantityDecrease(): Locator {
    return this.page.locator('[data-testid="quantity-decrease"]');
  }

  get quantityIncrease(): Locator {
    return this.page.locator('[data-testid="quantity-increase"]');
  }

  get addToCartButton(): Locator {
    return this.page.locator('[data-testid="add-to-cart-button"]');
  }

  get buyNowButton(): Locator {
    return this.page.locator('[data-testid="buy-now-button"]');
  }

  get addToWishlistButton(): Locator {
    return this.page.locator('[data-testid="add-to-wishlist-button"]');
  }

  get shareButton(): Locator {
    return this.page.locator('[data-testid="share-button"]');
  }

  // Product variants (if applicable)
  get variantSelectors(): Locator {
    return this.page.locator('[data-testid="variant-selector"]');
  }

  get sizeSelector(): Locator {
    return this.page.locator('[data-testid="size-selector"]');
  }

  get colorSelector(): Locator {
    return this.page.locator('[data-testid="color-selector"]');
  }

  // Product details tabs
  get detailsTabs(): Locator {
    return this.page.locator('[data-testid="product-tabs"]');
  }

  get descriptionTab(): Locator {
    return this.page.locator('[data-testid="description-tab"]');
  }

  get specificationsTab(): Locator {
    return this.page.locator('[data-testid="specifications-tab"]');
  }

  get reviewsTab(): Locator {
    return this.page.locator('[data-testid="reviews-tab"]');
  }

  get deliveryTab(): Locator {
    return this.page.locator('[data-testid="delivery-tab"]');
  }

  // Stock and availability
  get stockStatus(): Locator {
    return this.page.locator('[data-testid="stock-status"]');
  }

  get availabilityMessage(): Locator {
    return this.page.locator('[data-testid="availability-message"]');
  }

  // Reviews section
  get reviewsSection(): Locator {
    return this.page.locator('[data-testid="reviews-section"]');
  }

  get reviewsList(): Locator {
    return this.page.locator('[data-testid="reviews-list"]');
  }

  get reviewItems(): Locator {
    return this.page.locator('[data-testid="review-item"]');
  }

  get writeReviewButton(): Locator {
    return this.page.locator('[data-testid="write-review-button"]');
  }

  get averageRating(): Locator {
    return this.page.locator('[data-testid="average-rating"]');
  }

  get totalReviews(): Locator {
    return this.page.locator('[data-testid="total-reviews"]');
  }

  // Related products
  get relatedProductsSection(): Locator {
    return this.page.locator('[data-testid="related-products"]');
  }

  get relatedProductCards(): Locator {
    return this.page.locator('[data-testid="related-product-card"]');
  }

  // Breadcrumb
  get breadcrumb(): Locator {
    return this.page.locator('[data-testid="breadcrumb"]');
  }

  // Notifications
  get successNotification(): Locator {
    return this.page.locator('[data-testid="success-notification"]');
  }

  get errorNotification(): Locator {
    return this.page.locator('[data-testid="error-notification"]');
  }

  // Actions
  async visitProduct(productId: string): Promise<void> {
    await this.navigateTo(`/product/${productId}`);
    await this.waitForPageLoad();
  }

  async setQuantity(quantity: number): Promise<void> {
    await this.quantityInput.fill(quantity.toString());
  }

  async increaseQuantity(): Promise<void> {
    await this.quantityIncrease.click();
  }

  async decreaseQuantity(): Promise<void> {
    await this.quantityDecrease.click();
  }

  async addToCart(): Promise<void> {
    await this.addToCartButton.click();
  }

  async buyNow(): Promise<void> {
    await this.buyNowButton.click();
  }

  async addToWishlist(): Promise<void> {
    await this.addToWishlistButton.click();
  }

  async selectSize(size: string): Promise<void> {
    await this.sizeSelector.selectOption(size);
  }

  async selectColor(color: string): Promise<void> {
    const colorOption = this.colorSelector.locator(`[data-color="${color}"]`);
    await colorOption.click();
  }

  async clickThumbnail(index: number): Promise<void> {
    await this.thumbnailImages.nth(index).click();
  }

  async switchToTab(tabName: string): Promise<void> {
    const tab = this.detailsTabs.locator(`[data-tab="${tabName}"]`);
    await tab.click();
  }

  async writeReview(): Promise<void> {
    await this.writeReviewButton.click();
  }

  async clickRelatedProduct(index: number): Promise<void> {
    await this.relatedProductCards.nth(index).click();
  }

  async shareProduct(): Promise<void> {
    await this.shareButton.click();
  }

  // Assertion helpers
  async getProductTitle(): Promise<string> {
    return await this.productTitle.textContent() || '';
  }

  async getProductPrice(): Promise<string> {
    return await this.productPrice.textContent() || '';
  }

  async getQuantity(): Promise<number> {
    const value = await this.quantityInput.inputValue();
    return parseInt(value) || 1;
  }

  async isInStock(): Promise<boolean> {
    const status = await this.stockStatus.textContent() || '';
    return !status.toLowerCase().includes('rupture') && !status.toLowerCase().includes('indisponible');
  }

  async isAddToCartEnabled(): Promise<boolean> {
    return await this.addToCartButton.isEnabled();
  }

  async isInWishlist(): Promise<boolean> {
    return await this.addToWishlistButton.getAttribute('aria-pressed') === 'true';
  }

  async hasSuccessNotification(): Promise<boolean> {
    return await this.successNotification.isVisible();
  }

  async hasErrorNotification(): Promise<boolean> {
    return await this.errorNotification.isVisible();
  }

  async getAverageRating(): Promise<number> {
    const rating = await this.averageRating.textContent() || '0';
    return parseFloat(rating);
  }

  async getTotalReviews(): Promise<number> {
    const total = await this.totalReviews.textContent() || '0';
    return parseInt(total.replace(/\D/g, '')) || 0;
  }

  async getRelatedProductsCount(): Promise<number> {
    return await this.relatedProductCards.count();
  }

  async getCurrentImageSrc(): Promise<string> {
    return await this.mainProductImage.getAttribute('src') || '';
  }

  async getAvailabilityMessage(): Promise<string> {
    return await this.availabilityMessage.textContent() || '';
  }
}