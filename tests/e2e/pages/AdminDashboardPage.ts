import { Page, Locator } from '@playwright/test';
import { BasePage } from './BasePage';

export class AdminDashboardPage extends BasePage {
  constructor(page: Page) {
    super(page);
  }

  // Admin Navigation
  get adminSidebar(): Locator {
    return this.page.locator('[data-testid="admin-sidebar"]');
  }

  get dashboardLink(): Locator {
    return this.page.locator('[data-testid="admin-nav-dashboard"]');
  }

  get ordersLink(): Locator {
    return this.page.locator('[data-testid="admin-nav-orders"]');
  }

  get productsLink(): Locator {
    return this.page.locator('[data-testid="admin-nav-products"]');
  }

  get usersLink(): Locator {
    return this.page.locator('[data-testid="admin-nav-users"]');
  }

  get b2bManagementLink(): Locator {
    return this.page.locator('[data-testid="admin-nav-b2b"]');
  }

  get reviewsLink(): Locator {
    return this.page.locator('[data-testid="admin-nav-reviews"]');
  }

  get newsletterLink(): Locator {
    return this.page.locator('[data-testid="admin-nav-newsletter"]');
  }

  get blogLink(): Locator {
    return this.page.locator('[data-testid="admin-nav-blog"]');
  }

  get analyticsLink(): Locator {
    return this.page.locator('[data-testid="admin-nav-analytics"]');
  }

  get settingsLink(): Locator {
    return this.page.locator('[data-testid="admin-nav-settings"]');
  }

  get auditLogLink(): Locator {
    return this.page.locator('[data-testid="admin-nav-audit"]');
  }

  // Dashboard Overview
  get welcomeMessage(): Locator {
    return this.page.locator('[data-testid="admin-welcome"]');
  }

  get statsOverview(): Locator {
    return this.page.locator('[data-testid="stats-overview"]');
  }

  // Key Metrics Cards
  get totalOrdersCard(): Locator {
    return this.page.locator('[data-testid="metric-total-orders"]');
  }

  get totalRevenueCard(): Locator {
    return this.page.locator('[data-testid="metric-total-revenue"]');
  }

  get totalUsersCard(): Locator {
    return this.page.locator('[data-testid="metric-total-users"]');
  }

  get pendingOrdersCard(): Locator {
    return this.page.locator('[data-testid="metric-pending-orders"]');
  }

  get lowStockCard(): Locator {
    return this.page.locator('[data-testid="metric-low-stock"]');
  }

  get pendingReviewsCard(): Locator {
    return this.page.locator('[data-testid="metric-pending-reviews"]');
  }

  // Recent Activity
  get recentActivitySection(): Locator {
    return this.page.locator('[data-testid="recent-activity"]');
  }

  get activityItems(): Locator {
    return this.page.locator('[data-testid="activity-item"]');
  }

  // Quick Actions
  get quickActionsSection(): Locator {
    return this.page.locator('[data-testid="quick-actions"]');
  }

  get addProductButton(): Locator {
    return this.page.locator('[data-testid="quick-add-product"]');
  }

  get viewOrdersButton(): Locator {
    return this.page.locator('[data-testid="quick-view-orders"]');
  }

  get exportDataButton(): Locator {
    return this.page.locator('[data-testid="quick-export-data"]');
  }

  // Charts and Analytics
  get salesChart(): Locator {
    return this.page.locator('[data-testid="sales-chart"]');
  }

  get topProductsChart(): Locator {
    return this.page.locator('[data-testid="top-products-chart"]');
  }

  get userGrowthChart(): Locator {
    return this.page.locator('[data-testid="user-growth-chart"]');
  }

  // Orders Management
  get ordersTable(): Locator {
    return this.page.locator('[data-testid="admin-orders-table"]');
  }

  get orderRows(): Locator {
    return this.page.locator('[data-testid="admin-order-row"]');
  }

  get orderStatusSelects(): Locator {
    return this.page.locator('[data-testid="order-status-select"]');
  }

  get updateOrderButtons(): Locator {
    return this.page.locator('[data-testid="update-order-button"]');
  }

  get viewOrderButtons(): Locator {
    return this.page.locator('[data-testid="admin-view-order"]');
  }

  // Products Management
  get productsTable(): Locator {
    return this.page.locator('[data-testid="admin-products-table"]');
  }

  get productRows(): Locator {
    return this.page.locator('[data-testid="admin-product-row"]');
  }

  get editProductButtons(): Locator {
    return this.page.locator('[data-testid="edit-product-button"]');
  }

  get deleteProductButtons(): Locator {
    return this.page.locator('[data-testid="delete-product-button"]');
  }

  get productSearchInput(): Locator {
    return this.page.locator('[data-testid="product-search-input"]');
  }

  get addNewProductButton(): Locator {
    return this.page.locator('[data-testid="add-new-product"]');
  }

  // Users Management
  get usersTable(): Locator {
    return this.page.locator('[data-testid="admin-users-table"]');
  }

  get userRows(): Locator {
    return this.page.locator('[data-testid="admin-user-row"]');
  }

  get userStatusToggles(): Locator {
    return this.page.locator('[data-testid="user-status-toggle"]');
  }

  get viewUserButtons(): Locator {
    return this.page.locator('[data-testid="view-user-button"]');
  }

  get userSearchInput(): Locator {
    return this.page.locator('[data-testid="user-search-input"]');
  }

  // B2B Management
  get b2bRequestsTable(): Locator {
    return this.page.locator('[data-testid="b2b-requests-table"]');
  }

  get b2bRequestRows(): Locator {
    return this.page.locator('[data-testid="b2b-request-row"]');
  }

  get approveB2BButtons(): Locator {
    return this.page.locator('[data-testid="approve-b2b-button"]');
  }

  get rejectB2BButtons(): Locator {
    return this.page.locator('[data-testid="reject-b2b-button"]');
  }

  get viewB2BDetailsButtons(): Locator {
    return this.page.locator('[data-testid="view-b2b-details"]');
  }

  // Reviews Management
  get reviewsTable(): Locator {
    return this.page.locator('[data-testid="admin-reviews-table"]');
  }

  get reviewRows(): Locator {
    return this.page.locator('[data-testid="admin-review-row"]');
  }

  get approveReviewButtons(): Locator {
    return this.page.locator('[data-testid="approve-review-button"]');
  }

  get rejectReviewButtons(): Locator {
    return this.page.locator('[data-testid="reject-review-button"]');
  }

  // Newsletter Management
  get subscribersCount(): Locator {
    return this.page.locator('[data-testid="subscribers-count"]');
  }

  get createCampaignButton(): Locator {
    return this.page.locator('[data-testid="create-campaign-button"]');
  }

  get campaignsList(): Locator {
    return this.page.locator('[data-testid="campaigns-list"]');
  }

  // Audit Log
  get auditLogTable(): Locator {
    return this.page.locator('[data-testid="audit-log-table"]');
  }

  get auditLogRows(): Locator {
    return this.page.locator('[data-testid="audit-log-row"]');
  }

  get auditLogFilters(): Locator {
    return this.page.locator('[data-testid="audit-log-filters"]');
  }

  // Notifications and alerts
  get alertBanner(): Locator {
    return this.page.locator('[data-testid="alert-banner"]');
  }

  get notificationsList(): Locator {
    return this.page.locator('[data-testid="notifications-list"]');
  }

  // Actions
  async visit(): Promise<void> {
    await this.navigateTo('/admin/dashboard');
    await this.waitForPageLoad();
  }

  async goToOrders(): Promise<void> {
    await this.ordersLink.click();
  }

  async goToProducts(): Promise<void> {
    await this.productsLink.click();
  }

  async goToUsers(): Promise<void> {
    await this.usersLink.click();
  }

  async goToB2BManagement(): Promise<void> {
    await this.b2bManagementLink.click();
  }

  async goToReviews(): Promise<void> {
    await this.reviewsLink.click();
  }

  async goToNewsletter(): Promise<void> {
    await this.newsletterLink.click();
  }

  async goToBlog(): Promise<void> {
    await this.blogLink.click();
  }

  async goToAnalytics(): Promise<void> {
    await this.analyticsLink.click();
  }

  async goToSettings(): Promise<void> {
    await this.settingsLink.click();
  }

  async goToAuditLog(): Promise<void> {
    await this.auditLogLink.click();
  }

  async quickAddProduct(): Promise<void> {
    await this.addProductButton.click();
  }

  async quickViewOrders(): Promise<void> {
    await this.viewOrdersButton.click();
  }

  async exportData(): Promise<void> {
    await this.exportDataButton.click();
  }

  async updateOrderStatus(orderIndex: number, status: string): Promise<void> {
    await this.orderStatusSelects.nth(orderIndex).selectOption(status);
    await this.updateOrderButtons.nth(orderIndex).click();
  }

  async viewOrder(index: number = 0): Promise<void> {
    await this.viewOrderButtons.nth(index).click();
  }

  async editProduct(index: number = 0): Promise<void> {
    await this.editProductButtons.nth(index).click();
  }

  async deleteProduct(index: number = 0): Promise<void> {
    await this.deleteProductButtons.nth(index).click();
    // Handle confirmation dialog
    if (await this.page.locator('[data-testid="confirm-delete"]').isVisible()) {
      await this.page.locator('[data-testid="confirm-delete"]').click();
    }
  }

  async searchProducts(query: string): Promise<void> {
    await this.productSearchInput.fill(query);
    await this.page.keyboard.press('Enter');
  }

  async addNewProduct(): Promise<void> {
    await this.addNewProductButton.click();
  }

  async toggleUserStatus(index: number = 0): Promise<void> {
    await this.userStatusToggles.nth(index).click();
  }

  async viewUser(index: number = 0): Promise<void> {
    await this.viewUserButtons.nth(index).click();
  }

  async searchUsers(query: string): Promise<void> {
    await this.userSearchInput.fill(query);
    await this.page.keyboard.press('Enter');
  }

  async approveB2BRequest(index: number = 0): Promise<void> {
    await this.approveB2BButtons.nth(index).click();
  }

  async rejectB2BRequest(index: number = 0): Promise<void> {
    await this.rejectB2BButtons.nth(index).click();
  }

  async viewB2BDetails(index: number = 0): Promise<void> {
    await this.viewB2BDetailsButtons.nth(index).click();
  }

  async approveReview(index: number = 0): Promise<void> {
    await this.approveReviewButtons.nth(index).click();
  }

  async rejectReview(index: number = 0): Promise<void> {
    await this.rejectReviewButtons.nth(index).click();
  }

  async createCampaign(): Promise<void> {
    await this.createCampaignButton.click();
  }

  // Assertion helpers
  async getTotalOrders(): Promise<string> {
    return await this.totalOrdersCard.locator('[data-testid="metric-value"]').textContent() || '';
  }

  async getTotalRevenue(): Promise<string> {
    return await this.totalRevenueCard.locator('[data-testid="metric-value"]').textContent() || '';
  }

  async getTotalUsers(): Promise<string> {
    return await this.totalUsersCard.locator('[data-testid="metric-value"]').textContent() || '';
  }

  async getPendingOrders(): Promise<string> {
    return await this.pendingOrdersCard.locator('[data-testid="metric-value"]').textContent() || '';
  }

  async getLowStockCount(): Promise<string> {
    return await this.lowStockCard.locator('[data-testid="metric-value"]').textContent() || '';
  }

  async getPendingReviews(): Promise<string> {
    return await this.pendingReviewsCard.locator('[data-testid="metric-value"]').textContent() || '';
  }

  async getOrdersCount(): Promise<number> {
    return await this.orderRows.count();
  }

  async getProductsCount(): Promise<number> {
    return await this.productRows.count();
  }

  async getUsersCount(): Promise<number> {
    return await this.userRows.count();
  }

  async getB2BRequestsCount(): Promise<number> {
    return await this.b2bRequestRows.count();
  }

  async getReviewsCount(): Promise<number> {
    return await this.reviewRows.count();
  }

  async getSubscribersCount(): Promise<string> {
    return await this.subscribersCount.textContent() || '';
  }

  async getRecentActivityCount(): Promise<number> {
    return await this.activityItems.count();
  }

  async getAuditLogCount(): Promise<number> {
    return await this.auditLogRows.count();
  }

  async hasAlertBanner(): Promise<boolean> {
    return await this.alertBanner.isVisible();
  }

  async getAlertMessage(): Promise<string> {
    return await this.alertBanner.textContent() || '';
  }

  async isSalesChartVisible(): Promise<boolean> {
    return await this.salesChart.isVisible();
  }

  async isTopProductsChartVisible(): Promise<boolean> {
    return await this.topProductsChart.isVisible();
  }

  async isUserGrowthChartVisible(): Promise<boolean> {
    return await this.userGrowthChart.isVisible();
  }

  async getWelcomeMessage(): Promise<string> {
    return await this.welcomeMessage.textContent() || '';
  }
}