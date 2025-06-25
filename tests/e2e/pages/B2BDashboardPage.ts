import { Page, Locator } from '@playwright/test';
import { BasePage } from './BasePage';

export class B2BDashboardPage extends BasePage {
  constructor(page: Page) {
    super(page);
  }

  // B2B Navigation
  get b2bSidebar(): Locator {
    return this.page.locator('[data-testid="b2b-sidebar"]');
  }

  get dashboardLink(): Locator {
    return this.page.locator('[data-testid="b2b-nav-dashboard"]');
  }

  get ordersLink(): Locator {
    return this.page.locator('[data-testid="b2b-nav-orders"]');
  }

  get catalogLink(): Locator {
    return this.page.locator('[data-testid="b2b-nav-catalog"]');
  }

  get quickOrderLink(): Locator {
    return this.page.locator('[data-testid="b2b-nav-quick-order"]');
  }

  get invoicesLink(): Locator {
    return this.page.locator('[data-testid="b2b-nav-invoices"]');
  }

  get loyaltyLink(): Locator {
    return this.page.locator('[data-testid="b2b-nav-loyalty"]');
  }

  get referralsLink(): Locator {
    return this.page.locator('[data-testid="b2b-nav-referrals"]');
  }

  get profileLink(): Locator {
    return this.page.locator('[data-testid="b2b-nav-profile"]');
  }

  // Dashboard Overview
  get welcomeMessage(): Locator {
    return this.page.locator('[data-testid="b2b-welcome-message"]');
  }

  get companyInfo(): Locator {
    return this.page.locator('[data-testid="company-info"]');
  }

  get accountStatus(): Locator {
    return this.page.locator('[data-testid="account-status"]');
  }

  get tierBadge(): Locator {
    return this.page.locator('[data-testid="tier-badge"]');
  }

  // Statistics Cards
  get statsCards(): Locator {
    return this.page.locator('[data-testid="stats-card"]');
  }

  get totalOrdersCard(): Locator {
    return this.page.locator('[data-testid="total-orders-card"]');
  }

  get totalSpentCard(): Locator {
    return this.page.locator('[data-testid="total-spent-card"]');
  }

  get pendingOrdersCard(): Locator {
    return this.page.locator('[data-testid="pending-orders-card"]');
  }

  get loyaltyPointsCard(): Locator {
    return this.page.locator('[data-testid="loyalty-points-card"]');
  }

  // Recent Orders
  get recentOrdersSection(): Locator {
    return this.page.locator('[data-testid="recent-orders-section"]');
  }

  get recentOrdersList(): Locator {
    return this.page.locator('[data-testid="recent-orders-list"]');
  }

  get recentOrderItems(): Locator {
    return this.page.locator('[data-testid="recent-order-item"]');
  }

  // Quick Actions
  get quickActionsSection(): Locator {
    return this.page.locator('[data-testid="quick-actions-section"]');
  }

  get newOrderButton(): Locator {
    return this.page.locator('[data-testid="new-order-button"]');
  }

  get reorderButton(): Locator {
    return this.page.locator('[data-testid="reorder-button"]');
  }

  get viewCatalogButton(): Locator {
    return this.page.locator('[data-testid="view-catalog-button"]');
  }

  get downloadInvoiceButton(): Locator {
    return this.page.locator('[data-testid="download-invoice-button"]');
  }

  // B2B Orders Page
  get ordersTable(): Locator {
    return this.page.locator('[data-testid="b2b-orders-table"]');
  }

  get orderRows(): Locator {
    return this.page.locator('[data-testid="b2b-order-row"]');
  }

  get orderNumbers(): Locator {
    return this.page.locator('[data-testid="b2b-order-number"]');
  }

  get orderDates(): Locator {
    return this.page.locator('[data-testid="b2b-order-date"]');
  }

  get orderStatuses(): Locator {
    return this.page.locator('[data-testid="b2b-order-status"]');
  }

  get orderTotals(): Locator {
    return this.page.locator('[data-testid="b2b-order-total"]');
  }

  get viewOrderButtons(): Locator {
    return this.page.locator('[data-testid="b2b-view-order"]');
  }

  get reorderButtons(): Locator {
    return this.page.locator('[data-testid="b2b-reorder"]');
  }

  // Quick Order Form
  get quickOrderForm(): Locator {
    return this.page.locator('[data-testid="quick-order-form"]');
  }

  get productSkuInput(): Locator {
    return this.page.locator('[data-testid="product-sku-input"]');
  }

  get quantityInput(): Locator {
    return this.page.locator('[data-testid="quick-order-quantity"]');
  }

  get addToOrderButton(): Locator {
    return this.page.locator('[data-testid="add-to-order"]');
  }

  get quickOrderItems(): Locator {
    return this.page.locator('[data-testid="quick-order-item"]');
  }

  get placeQuickOrderButton(): Locator {
    return this.page.locator('[data-testid="place-quick-order"]');
  }

  // B2B Catalog
  get catalogFilters(): Locator {
    return this.page.locator('[data-testid="b2b-catalog-filters"]');
  }

  get b2bProductGrid(): Locator {
    return this.page.locator('[data-testid="b2b-product-grid"]');
  }

  get b2bProductCards(): Locator {
    return this.page.locator('[data-testid="b2b-product-card"]');
  }

  get bulkPricing(): Locator {
    return this.page.locator('[data-testid="bulk-pricing"]');
  }

  get addToB2BCartButtons(): Locator {
    return this.page.locator('[data-testid="add-to-b2b-cart"]');
  }

  // Invoices
  get invoicesTable(): Locator {
    return this.page.locator('[data-testid="invoices-table"]');
  }

  get invoiceRows(): Locator {
    return this.page.locator('[data-testid="invoice-row"]');
  }

  get downloadInvoiceButtons(): Locator {
    return this.page.locator('[data-testid="download-invoice"]');
  }

  get payInvoiceButtons(): Locator {
    return this.page.locator('[data-testid="pay-invoice"]');
  }

  // Loyalty Program
  get loyaltyOverview(): Locator {
    return this.page.locator('[data-testid="loyalty-overview"]');
  }

  get currentPoints(): Locator {
    return this.page.locator('[data-testid="current-points"]');
  }

  get tierProgress(): Locator {
    return this.page.locator('[data-testid="tier-progress"]');
  }

  get rewardsAvailable(): Locator {
    return this.page.locator('[data-testid="rewards-available"]');
  }

  get claimRewardButtons(): Locator {
    return this.page.locator('[data-testid="claim-reward"]');
  }

  // Referrals
  get referralCode(): Locator {
    return this.page.locator('[data-testid="referral-code"]');
  }

  get referralStats(): Locator {
    return this.page.locator('[data-testid="referral-stats"]');
  }

  get shareReferralButton(): Locator {
    return this.page.locator('[data-testid="share-referral"]');
  }

  // Actions
  async visit(): Promise<void> {
    await this.navigateTo('/b2b/dashboard');
    await this.waitForPageLoad();
  }

  async goToOrders(): Promise<void> {
    await this.ordersLink.click();
  }

  async goToCatalog(): Promise<void> {
    await this.catalogLink.click();
  }

  async goToQuickOrder(): Promise<void> {
    await this.quickOrderLink.click();
  }

  async goToInvoices(): Promise<void> {
    await this.invoicesLink.click();
  }

  async goToLoyalty(): Promise<void> {
    await this.loyaltyLink.click();
  }

  async goToReferrals(): Promise<void> {
    await this.referralsLink.click();
  }

  async goToProfile(): Promise<void> {
    await this.profileLink.click();
  }

  async createNewOrder(): Promise<void> {
    await this.newOrderButton.click();
  }

  async reorderLast(): Promise<void> {
    await this.reorderButton.click();
  }

  async viewCatalog(): Promise<void> {
    await this.viewCatalogButton.click();
  }

  async viewOrder(index: number = 0): Promise<void> {
    await this.viewOrderButtons.nth(index).click();
  }

  async reorder(index: number = 0): Promise<void> {
    await this.reorderButtons.nth(index).click();
  }

  async addQuickOrderItem(sku: string, quantity: number): Promise<void> {
    await this.productSkuInput.fill(sku);
    await this.quantityInput.fill(quantity.toString());
    await this.addToOrderButton.click();
  }

  async placeQuickOrder(): Promise<void> {
    await this.placeQuickOrderButton.click();
  }

  async downloadInvoice(index: number = 0): Promise<void> {
    await this.downloadInvoiceButtons.nth(index).click();
  }

  async payInvoice(index: number = 0): Promise<void> {
    await this.payInvoiceButtons.nth(index).click();
  }

  async claimReward(index: number = 0): Promise<void> {
    await this.claimRewardButtons.nth(index).click();
  }

  async shareReferralCode(): Promise<void> {
    await this.shareReferralButton.click();
  }

  async addB2BProductToCart(index: number = 0): Promise<void> {
    await this.addToB2BCartButtons.nth(index).click();
  }

  // Assertion helpers
  async getWelcomeMessage(): Promise<string> {
    return await this.welcomeMessage.textContent() || '';
  }

  async getCompanyName(): Promise<string> {
    const companyInfo = await this.companyInfo.textContent() || '';
    return companyInfo.split('\n')[0] || '';
  }

  async getAccountStatus(): Promise<string> {
    return await this.accountStatus.textContent() || '';
  }

  async getTierLevel(): Promise<string> {
    return await this.tierBadge.textContent() || '';
  }

  async getTotalOrders(): Promise<string> {
    return await this.totalOrdersCard.locator('[data-testid="stat-value"]').textContent() || '';
  }

  async getTotalSpent(): Promise<string> {
    return await this.totalSpentCard.locator('[data-testid="stat-value"]').textContent() || '';
  }

  async getPendingOrders(): Promise<string> {
    return await this.pendingOrdersCard.locator('[data-testid="stat-value"]').textContent() || '';
  }

  async getLoyaltyPoints(): Promise<string> {
    return await this.loyaltyPointsCard.locator('[data-testid="stat-value"]').textContent() || '';
  }

  async getRecentOrdersCount(): Promise<number> {
    return await this.recentOrderItems.count();
  }

  async getOrdersCount(): Promise<number> {
    return await this.orderRows.count();
  }

  async getInvoicesCount(): Promise<number> {
    return await this.invoiceRows.count();
  }

  async getQuickOrderItemsCount(): Promise<number> {
    return await this.quickOrderItems.count();
  }

  async getCurrentLoyaltyPoints(): Promise<string> {
    return await this.currentPoints.textContent() || '';
  }

  async getReferralCode(): Promise<string> {
    return await this.referralCode.textContent() || '';
  }

  async isAccountApproved(): Promise<boolean> {
    const status = await this.getAccountStatus();
    return status.toLowerCase().includes('approuvé') || status.toLowerCase().includes('approved');
  }

  async isAccountPending(): Promise<boolean> {
    const status = await this.getAccountStatus();
    return status.toLowerCase().includes('en attente') || status.toLowerCase().includes('pending');
  }

  async hasQuickOrderItems(): Promise<boolean> {
    return await this.getQuickOrderItemsCount() > 0;
  }

  async getOrderStatus(index: number = 0): Promise<string> {
    return await this.orderStatuses.nth(index).textContent() || '';
  }

  async getOrderTotal(index: number = 0): Promise<string> {
    return await this.orderTotals.nth(index).textContent() || '';
  }

  async getB2BProductsCount(): Promise<number> {
    return await this.b2bProductCards.count();
  }

  async hasBulkPricing(index: number = 0): Promise<boolean> {
    const productCard = this.b2bProductCards.nth(index);
    return await productCard.locator('[data-testid="bulk-pricing"]').isVisible();
  }
}