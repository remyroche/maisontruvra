import { Page, Locator } from '@playwright/test';
import { BasePage } from './BasePage';

export class CartPage extends BasePage {
  constructor(page: Page) {
    super(page);
  }

  // Cart container elements
  get cartContainer(): Locator {
    return this.page.locator('[data-testid="cart-container"]');
  }

  get emptyCartMessage(): Locator {
    return this.page.locator('[data-testid="empty-cart-message"]');
  }

  // Cart items
  get cartItems(): Locator {
    return this.page.locator('[data-testid="cart-item"]');
  }

  get itemNames(): Locator {
    return this.page.locator('[data-testid="item-name"]');
  }

  get itemPrices(): Locator {
    return this.page.locator('[data-testid="item-price"]');
  }

  get itemQuantities(): Locator {
    return this.page.locator('[data-testid="item-quantity"]');
  }

  get itemTotals(): Locator {
    return this.page.locator('[data-testid="item-total"]');
  }

  get removeItemButtons(): Locator {
    return this.page.locator('[data-testid="remove-item-button"]');
  }

  get quantityIncreaseButtons(): Locator {
    return this.page.locator('[data-testid="quantity-increase"]');
  }

  get quantityDecreaseButtons(): Locator {
    return this.page.locator('[data-testid="quantity-decrease"]');
  }

  // Cart summary
  get cartSummary(): Locator {
    return this.page.locator('[data-testid="cart-summary"]');
  }

  get subtotalAmount(): Locator {
    return this.page.locator('[data-testid="subtotal-amount"]');
  }

  get shippingAmount(): Locator {
    return this.page.locator('[data-testid="shipping-amount"]');
  }

  get taxAmount(): Locator {
    return this.page.locator('[data-testid="tax-amount"]');
  }

  get totalAmount(): Locator {
    return this.page.locator('[data-testid="total-amount"]');
  }

  get discountAmount(): Locator {
    return this.page.locator('[data-testid="discount-amount"]');
  }

  // Promotional code
  get promoCodeInput(): Locator {
    return this.page.locator('[data-testid="promo-code-input"]');
  }

  get applyPromoButton(): Locator {
    return this.page.locator('[data-testid="apply-promo-button"]');
  }

  get removePromoButton(): Locator {
    return this.page.locator('[data-testid="remove-promo-button"]');
  }

  get promoCodeMessage(): Locator {
    return this.page.locator('[data-testid="promo-code-message"]');
  }

  // Shipping calculator
  get shippingCalculator(): Locator {
    return this.page.locator('[data-testid="shipping-calculator"]');
  }

  get countrySelect(): Locator {
    return this.page.locator('[data-testid="shipping-country"]');
  }

  get postalCodeInput(): Locator {
    return this.page.locator('[data-testid="shipping-postal-code"]');
  }

  get calculateShippingButton(): Locator {
    return this.page.locator('[data-testid="calculate-shipping"]');
  }

  // Action buttons
  get continueShoppingButton(): Locator {
    return this.page.locator('[data-testid="continue-shopping"]');
  }

  get clearCartButton(): Locator {
    return this.page.locator('[data-testid="clear-cart"]');
  }

  get checkoutButton(): Locator {
    return this.page.locator('[data-testid="checkout-button"]');
  }

  get saveForLaterButtons(): Locator {
    return this.page.locator('[data-testid="save-for-later"]');
  }

  // Notifications and messages
  get updateMessage(): Locator {
    return this.page.locator('[data-testid="update-message"]');
  }

  get errorMessage(): Locator {
    return this.page.locator('[data-testid="error-message"]');
  }

  // Actions
  async visit(): Promise<void> {
    await this.navigateTo('/cart');
    await this.waitForPageLoad();
  }

  async removeItem(index: number = 0): Promise<void> {
    await this.removeItemButtons.nth(index).click();
    // Wait for item to be removed from DOM
    await this.page.waitForTimeout(500);
  }

  async updateItemQuantity(index: number, quantity: number): Promise<void> {
    const currentQuantity = await this.getItemQuantity(index);
    const difference = quantity - currentQuantity;
    
    if (difference > 0) {
      for (let i = 0; i < difference; i++) {
        await this.quantityIncreaseButtons.nth(index).click();
        await this.page.waitForTimeout(200);
      }
    } else if (difference < 0) {
      for (let i = 0; i < Math.abs(difference); i++) {
        await this.quantityDecreaseButtons.nth(index).click();
        await this.page.waitForTimeout(200);
      }
    }
  }

  async increaseItemQuantity(index: number = 0): Promise<void> {
    await this.quantityIncreaseButtons.nth(index).click();
  }

  async decreaseItemQuantity(index: number = 0): Promise<void> {
    await this.quantityDecreaseButtons.nth(index).click();
  }

  async applyPromoCode(code: string): Promise<void> {
    await this.promoCodeInput.fill(code);
    await this.applyPromoButton.click();
    await this.page.waitForTimeout(1000); // Wait for response
  }

  async removePromoCode(): Promise<void> {
    await this.removePromoButton.click();
  }

  async calculateShipping(country: string, postalCode: string): Promise<void> {
    await this.countrySelect.selectOption(country);
    await this.postalCodeInput.fill(postalCode);
    await this.calculateShippingButton.click();
    await this.page.waitForTimeout(1000); // Wait for calculation
  }

  async continueShopping(): Promise<void> {
    await this.continueShoppingButton.click();
  }

  async clearCart(): Promise<void> {
    await this.clearCartButton.click();
    // Handle confirmation dialog if present
    if (await this.page.locator('[data-testid="confirm-clear-cart"]').isVisible()) {
      await this.page.locator('[data-testid="confirm-clear-cart"]').click();
    }
  }

  async proceedToCheckout(): Promise<void> {
    await this.checkoutButton.click();
  }

  async saveItemForLater(index: number = 0): Promise<void> {
    await this.saveForLaterButtons.nth(index).click();
  }

  // Assertion helpers
  async isCartEmpty(): Promise<boolean> {
    return await this.emptyCartMessage.isVisible();
  }

  async getItemsCount(): Promise<number> {
    return await this.cartItems.count();
  }

  async getItemName(index: number = 0): Promise<string> {
    return await this.itemNames.nth(index).textContent() || '';
  }

  async getItemPrice(index: number = 0): Promise<string> {
    return await this.itemPrices.nth(index).textContent() || '';
  }

  async getItemQuantity(index: number = 0): Promise<number> {
    const quantityInput = this.itemQuantities.nth(index);
    const value = await quantityInput.inputValue();
    return parseInt(value) || 1;
  }

  async getItemTotal(index: number = 0): Promise<string> {
    return await this.itemTotals.nth(index).textContent() || '';
  }

  async getSubtotal(): Promise<string> {
    return await this.subtotalAmount.textContent() || '';
  }

  async getShippingCost(): Promise<string> {
    return await this.shippingAmount.textContent() || '';
  }

  async getTaxes(): Promise<string> {
    return await this.taxAmount.textContent() || '';
  }

  async getTotal(): Promise<string> {
    return await this.totalAmount.textContent() || '';
  }

  async getDiscountAmount(): Promise<string> {
    return await this.discountAmount.textContent() || '';
  }

  async isPromoCodeApplied(): Promise<boolean> {
    return await this.removePromoButton.isVisible();
  }

  async getPromoCodeMessage(): Promise<string> {
    return await this.promoCodeMessage.textContent() || '';
  }

  async isCheckoutEnabled(): Promise<boolean> {
    return await this.checkoutButton.isEnabled();
  }

  async hasUpdateMessage(): Promise<boolean> {
    return await this.updateMessage.isVisible();
  }

  async hasErrorMessage(): Promise<boolean> {
    return await this.errorMessage.isVisible();
  }

  async getErrorMessage(): Promise<string> {
    return await this.errorMessage.textContent() || '';
  }

  // Helper methods for price calculations
  private parsePrice(priceText: string): number {
    return parseFloat(priceText.replace(/[€$£,\s]/g, '')) || 0;
  }

  async calculateExpectedSubtotal(): Promise<number> {
    let total = 0;
    const itemCount = await this.getItemsCount();
    
    for (let i = 0; i < itemCount; i++) {
      const price = this.parsePrice(await this.getItemPrice(i));
      const quantity = await this.getItemQuantity(i);
      total += price * quantity;
    }
    
    return total;
  }

  async verifyCartTotals(): Promise<boolean> {
    const expectedSubtotal = await this.calculateExpectedSubtotal();
    const actualSubtotal = this.parsePrice(await this.getSubtotal());
    
    return Math.abs(expectedSubtotal - actualSubtotal) < 0.01; // Allow for small rounding differences
  }
}