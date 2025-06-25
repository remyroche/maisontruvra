import { Page, Locator } from '@playwright/test';
import { BasePage } from './BasePage';

export class AccountPage extends BasePage {
  constructor(page: Page) {
    super(page);
  }

  // Account navigation
  get accountSidebar(): Locator {
    return this.page.locator('[data-testid="account-sidebar"]');
  }

  get dashboardLink(): Locator {
    return this.page.locator('[data-testid="nav-dashboard"]');
  }

  get profileLink(): Locator {
    return this.page.locator('[data-testid="nav-profile"]');
  }

  get ordersLink(): Locator {
    return this.page.locator('[data-testid="nav-orders"]');
  }

  get addressesLink(): Locator {
    return this.page.locator('[data-testid="nav-addresses"]');
  }

  get wishlistLink(): Locator {
    return this.page.locator('[data-testid="nav-wishlist"]');
  }

  get securityLink(): Locator {
    return this.page.locator('[data-testid="nav-security"]');
  }

  get loyaltyLink(): Locator {
    return this.page.locator('[data-testid="nav-loyalty"]');
  }

  // Dashboard elements
  get welcomeMessage(): Locator {
    return this.page.locator('[data-testid="welcome-message"]');
  }

  get accountStats(): Locator {
    return this.page.locator('[data-testid="account-stats"]');
  }

  get recentOrders(): Locator {
    return this.page.locator('[data-testid="recent-orders"]');
  }

  get quickActions(): Locator {
    return this.page.locator('[data-testid="quick-actions"]');
  }

  // Profile form elements
  get profileForm(): Locator {
    return this.page.locator('[data-testid="profile-form"]');
  }

  get firstNameInput(): Locator {
    return this.page.locator('[data-testid="first-name-input"]');
  }

  get lastNameInput(): Locator {
    return this.page.locator('[data-testid="last-name-input"]');
  }

  get emailInput(): Locator {
    return this.page.locator('[data-testid="email-input"]');
  }

  get phoneInput(): Locator {
    return this.page.locator('[data-testid="phone-input"]');
  }

  get updateProfileButton(): Locator {
    return this.page.locator('[data-testid="update-profile-button"]');
  }

  // Orders section
  get ordersTable(): Locator {
    return this.page.locator('[data-testid="orders-table"]');
  }

  get orderRows(): Locator {
    return this.page.locator('[data-testid="order-row"]');
  }

  get orderNumbers(): Locator {
    return this.page.locator('[data-testid="order-number"]');
  }

  get orderDates(): Locator {
    return this.page.locator('[data-testid="order-date"]');
  }

  get orderStatuses(): Locator {
    return this.page.locator('[data-testid="order-status"]');
  }

  get orderTotals(): Locator {
    return this.page.locator('[data-testid="order-total"]');
  }

  get viewOrderButtons(): Locator {
    return this.page.locator('[data-testid="view-order-button"]');
  }

  get trackOrderButtons(): Locator {
    return this.page.locator('[data-testid="track-order-button"]');
  }

  // Address management
  get addressesList(): Locator {
    return this.page.locator('[data-testid="addresses-list"]');
  }

  get addAddressButton(): Locator {
    return this.page.locator('[data-testid="add-address-button"]');
  }

  get addressCards(): Locator {
    return this.page.locator('[data-testid="address-card"]');
  }

  get editAddressButtons(): Locator {
    return this.page.locator('[data-testid="edit-address-button"]');
  }

  get deleteAddressButtons(): Locator {
    return this.page.locator('[data-testid="delete-address-button"]');
  }

  get setDefaultButtons(): Locator {
    return this.page.locator('[data-testid="set-default-address"]');
  }

  // Address form
  get addressForm(): Locator {
    return this.page.locator('[data-testid="address-form"]');
  }

  get addressLine1Input(): Locator {
    return this.page.locator('[data-testid="address-line1-input"]');
  }

  get addressLine2Input(): Locator {
    return this.page.locator('[data-testid="address-line2-input"]');
  }

  get cityInput(): Locator {
    return this.page.locator('[data-testid="city-input"]');
  }

  get stateInput(): Locator {
    return this.page.locator('[data-testid="state-input"]');
  }

  get postalCodeInput(): Locator {
    return this.page.locator('[data-testid="postal-code-input"]');
  }

  get countrySelect(): Locator {
    return this.page.locator('[data-testid="country-select"]');
  }

  get saveAddressButton(): Locator {
    return this.page.locator('[data-testid="save-address-button"]');
  }

  // Wishlist elements
  get wishlistItems(): Locator {
    return this.page.locator('[data-testid="wishlist-item"]');
  }

  get removeFromWishlistButtons(): Locator {
    return this.page.locator('[data-testid="remove-from-wishlist"]');
  }

  get moveToCartButtons(): Locator {
    return this.page.locator('[data-testid="move-to-cart"]');
  }

  get emptyWishlistMessage(): Locator {
    return this.page.locator('[data-testid="empty-wishlist"]');
  }

  // Security settings
  get changePasswordForm(): Locator {
    return this.page.locator('[data-testid="change-password-form"]');
  }

  get currentPasswordInput(): Locator {
    return this.page.locator('[data-testid="current-password-input"]');
  }

  get newPasswordInput(): Locator {
    return this.page.locator('[data-testid="new-password-input"]');
  }

  get confirmPasswordInput(): Locator {
    return this.page.locator('[data-testid="confirm-password-input"]');
  }

  get changePasswordButton(): Locator {
    return this.page.locator('[data-testid="change-password-button"]');
  }

  get twoFactorSection(): Locator {
    return this.page.locator('[data-testid="two-factor-section"]');
  }

  get enableTwoFactorButton(): Locator {
    return this.page.locator('[data-testid="enable-two-factor"]');
  }

  get disableTwoFactorButton(): Locator {
    return this.page.locator('[data-testid="disable-two-factor"]');
  }

  // Notifications and messages
  get successMessage(): Locator {
    return this.page.locator('[data-testid="success-message"]');
  }

  get errorMessage(): Locator {
    return this.page.locator('[data-testid="error-message"]');
  }

  // Actions
  async visit(): Promise<void> {
    await this.navigateTo('/account');
    await this.waitForPageLoad();
  }

  async goToDashboard(): Promise<void> {
    await this.dashboardLink.click();
  }

  async goToProfile(): Promise<void> {
    await this.profileLink.click();
  }

  async goToOrders(): Promise<void> {
    await this.ordersLink.click();
  }

  async goToAddresses(): Promise<void> {
    await this.addressesLink.click();
  }

  async goToWishlist(): Promise<void> {
    await this.wishlistLink.click();
  }

  async goToSecurity(): Promise<void> {
    await this.securityLink.click();
  }

  async updateProfile(data: {
    firstName?: string;
    lastName?: string;
    email?: string;
    phone?: string;
  }): Promise<void> {
    if (data.firstName) await this.firstNameInput.fill(data.firstName);
    if (data.lastName) await this.lastNameInput.fill(data.lastName);
    if (data.email) await this.emailInput.fill(data.email);
    if (data.phone) await this.phoneInput.fill(data.phone);
    
    await this.updateProfileButton.click();
  }

  async viewOrder(index: number = 0): Promise<void> {
    await this.viewOrderButtons.nth(index).click();
  }

  async trackOrder(index: number = 0): Promise<void> {
    await this.trackOrderButtons.nth(index).click();
  }

  async addAddress(addressData: {
    line1: string;
    line2?: string;
    city: string;
    state?: string;
    postalCode: string;
    country: string;
  }): Promise<void> {
    await this.addAddressButton.click();
    
    await this.addressLine1Input.fill(addressData.line1);
    if (addressData.line2) await this.addressLine2Input.fill(addressData.line2);
    await this.cityInput.fill(addressData.city);
    if (addressData.state) await this.stateInput.fill(addressData.state);
    await this.postalCodeInput.fill(addressData.postalCode);
    await this.countrySelect.selectOption(addressData.country);
    
    await this.saveAddressButton.click();
  }

  async editAddress(index: number = 0): Promise<void> {
    await this.editAddressButtons.nth(index).click();
  }

  async deleteAddress(index: number = 0): Promise<void> {
    await this.deleteAddressButtons.nth(index).click();
    // Handle confirmation if present
    if (await this.page.locator('[data-testid="confirm-delete"]').isVisible()) {
      await this.page.locator('[data-testid="confirm-delete"]').click();
    }
  }

  async setDefaultAddress(index: number = 0): Promise<void> {
    await this.setDefaultButtons.nth(index).click();
  }

  async removeFromWishlist(index: number = 0): Promise<void> {
    await this.removeFromWishlistButtons.nth(index).click();
  }

  async moveWishlistItemToCart(index: number = 0): Promise<void> {
    await this.moveToCartButtons.nth(index).click();
  }

  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await this.currentPasswordInput.fill(currentPassword);
    await this.newPasswordInput.fill(newPassword);
    await this.confirmPasswordInput.fill(newPassword);
    await this.changePasswordButton.click();
  }

  async enableTwoFactor(): Promise<void> {
    await this.enableTwoFactorButton.click();
  }

  async disableTwoFactor(): Promise<void> {
    await this.disableTwoFactorButton.click();
  }

  // Assertion helpers
  async getWelcomeMessage(): Promise<string> {
    return await this.welcomeMessage.textContent() || '';
  }

  async getOrdersCount(): Promise<number> {
    return await this.orderRows.count();
  }

  async getAddressesCount(): Promise<number> {
    return await this.addressCards.count();
  }

  async getWishlistItemsCount(): Promise<number> {
    return await this.wishlistItems.count();
  }

  async isWishlistEmpty(): Promise<boolean> {
    return await this.emptyWishlistMessage.isVisible();
  }

  async getOrderStatus(index: number = 0): Promise<string> {
    return await this.orderStatuses.nth(index).textContent() || '';
  }

  async getOrderTotal(index: number = 0): Promise<string> {
    return await this.orderTotals.nth(index).textContent() || '';
  }

  async hasSuccessMessage(): Promise<boolean> {
    return await this.successMessage.isVisible();
  }

  async hasErrorMessage(): Promise<boolean> {
    return await this.errorMessage.isVisible();
  }

  async getSuccessMessage(): Promise<string> {
    return await this.successMessage.textContent() || '';
  }

  async getErrorMessage(): Promise<string> {
    return await this.errorMessage.textContent() || '';
  }

  async isTwoFactorEnabled(): Promise<boolean> {
    return await this.disableTwoFactorButton.isVisible();
  }
}