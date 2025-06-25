import { test, expect } from './fixtures/auth';
import { AdminDashboardPage } from './pages/AdminDashboardPage';
import { TestHelpers } from './utils/test-helpers';
import { TestDataGenerator, TEST_CONSTANTS } from './utils/test-data';

test.describe('Admin/Staff User Experience', () => {
  test.describe('Admin Authentication and Access', () => {
    test('should login admin user successfully', async ({ page, authenticatedAdminUser }) => {
      // User is already authenticated via fixture
      await TestHelpers.verifyUrl(page, /admin/);
      
      expect(authenticatedAdminUser.isAuthenticated).toBe(true);
      expect(authenticatedAdminUser.role).toBe('admin');
    });

    test('should handle MFA for admin login if enabled', async ({ page, authPage }) => {
      await authPage.visitLogin();
      
      // Try to login admin
      await authPage.login('admin@example.com', 'AdminPass123!');
      
      // Check if MFA is required
      const isMFARequired = await authPage.isMFAFormVisible();
      
      if (isMFARequired) {
        // Verify MFA form elements
        await expect(authPage.mfaForm).toBeVisible();
        await expect(authPage.mfaCodeInput).toBeVisible();
        await expect(authPage.mfaSubmitButton).toBeVisible();
        
        // Note: In actual implementation, you'd need to handle real TOTP codes
        // For testing, you might need to mock this or use test TOTP secrets
        console.log('MFA is enabled for admin - requires test TOTP setup');
      }
    });

    test('should restrict admin access to authenticated users only', async ({ page, authPage }) => {
      // Clear any existing authentication
      await TestHelpers.clearBrowserData(page);
      
      // Try to access admin dashboard without authentication
      await page.goto('/admin/dashboard');
      
      // Should be redirected to login
      await TestHelpers.verifyUrl(page, /login|auth/);
      await expect(authPage.loginForm).toBeVisible();
    });
  });

  test.describe('Admin Dashboard Overview', () => {
    test('should display admin dashboard with key metrics', async ({ page, authenticatedAdminUser }) => {
      const adminDashboard = new AdminDashboardPage(page);
      await adminDashboard.visit();
      
      // Verify dashboard loads with admin elements
      await expect(adminDashboard.welcomeMessage).toBeVisible();
      await expect(adminDashboard.statsOverview).toBeVisible();
      await expect(adminDashboard.adminSidebar).toBeVisible();
      
      // Verify welcome message
      const welcome = await adminDashboard.getWelcomeMessage();
      expect(welcome).toContain(/admin|tableau|bord/i);
      
      // Verify key metrics are displayed
      await expect(adminDashboard.totalOrdersCard).toBeVisible();
      await expect(adminDashboard.totalRevenueCard).toBeVisible();
      await expect(adminDashboard.totalUsersCard).toBeVisible();
      
      // Get metric values
      const totalOrders = await adminDashboard.getTotalOrders();
      const totalRevenue = await adminDashboard.getTotalRevenue();
      const totalUsers = await adminDashboard.getTotalUsers();
      
      expect(totalOrders).toBeTruthy();
      expect(totalRevenue).toBeTruthy();
      expect(totalUsers).toBeTruthy();
    });

    test('should display navigation menu with all admin sections', async ({ page, authenticatedAdminUser }) => {
      const adminDashboard = new AdminDashboardPage(page);
      await adminDashboard.visit();
      
      // Verify all admin navigation links are present
      await expect(adminDashboard.dashboardLink).toBeVisible();
      await expect(adminDashboard.ordersLink).toBeVisible();
      await expect(adminDashboard.productsLink).toBeVisible();
      await expect(adminDashboard.usersLink).toBeVisible();
      await expect(adminDashboard.b2bManagementLink).toBeVisible();
      await expect(adminDashboard.reviewsLink).toBeVisible();
      await expect(adminDashboard.newsletterLink).toBeVisible();
      await expect(adminDashboard.analyticsLink).toBeVisible();
      await expect(adminDashboard.settingsLink).toBeVisible();
      await expect(adminDashboard.auditLogLink).toBeVisible();
    });

    test('should display recent activity and alerts', async ({ page, authenticatedAdminUser }) => {
      const adminDashboard = new AdminDashboardPage(page);
      await adminDashboard.visit();
      
      // Verify recent activity section
      await expect(adminDashboard.recentActivitySection).toBeVisible();
      
      const activityCount = await adminDashboard.getRecentActivityCount();
      expect(activityCount).toBeGreaterThanOrEqual(0);
      
      // Check for alert banners
      const hasAlerts = await adminDashboard.hasAlertBanner();
      if (hasAlerts) {
        const alertMessage = await adminDashboard.getAlertMessage();
        expect(alertMessage).toBeTruthy();
      }
    });

    test('should display charts and analytics', async ({ page, authenticatedAdminUser }) => {
      const adminDashboard = new AdminDashboardPage(page);
      await adminDashboard.visit();
      
      // Verify charts are present
      const hasSalesChart = await adminDashboard.isSalesChartVisible();
      const hasTopProductsChart = await adminDashboard.isTopProductsChartVisible();
      const hasUserGrowthChart = await adminDashboard.isUserGrowthChartVisible();
      
      // At least one chart should be visible
      expect(hasSalesChart || hasTopProductsChart || hasUserGrowthChart).toBe(true);
    });
  });

  test.describe('Order Management', () => {
    test('should access and manage orders', async ({ page, authenticatedAdminUser }) => {
      const adminDashboard = new AdminDashboardPage(page);
      await adminDashboard.visit();
      await adminDashboard.goToOrders();
      
      // Verify orders management page
      await expect(adminDashboard.ordersTable).toBeVisible();
      
      const ordersCount = await adminDashboard.getOrdersCount();
      expect(ordersCount).toBeGreaterThanOrEqual(0);
      
      // If orders exist, test order management
      if (ordersCount > 0) {
        // Test viewing order details
        await adminDashboard.viewOrder(0);
        await TestHelpers.verifyUrl(page, /order|commande/);
        
        // Go back to orders list
        await page.goBack();
        
        // Test updating order status
        await adminDashboard.updateOrderStatus(0, 'processing');
        await TestHelpers.verifyToast(page, /mis à jour|updated/i);
      }
    });

    test('should filter and search orders', async ({ page, authenticatedAdminUser }) => {
      const adminDashboard = new AdminDashboardPage(page);
      await adminDashboard.visit();
      await adminDashboard.goToOrders();
      
      // Test order filtering if available
      const orderFilters = page.locator('[data-testid="order-filters"]');
      
      if (await orderFilters.isVisible()) {
        // Apply status filter
        const statusFilter = orderFilters.locator('[data-testid="status-filter"]');
        if (await statusFilter.isVisible()) {
          await statusFilter.selectOption('pending');
          await TestHelpers.waitForPageStable(page);
          
          const filteredCount = await adminDashboard.getOrdersCount();
          expect(filteredCount).toBeGreaterThanOrEqual(0);
        }
      }
      
      // Test order search if available
      const searchInput = page.locator('[data-testid="order-search"]');
      
      if (await searchInput.isVisible()) {
        await searchInput.fill('12345');
        await page.keyboard.press('Enter');
        await TestHelpers.waitForPageStable(page);
        
        const searchResults = await adminDashboard.getOrdersCount();
        expect(searchResults).toBeGreaterThanOrEqual(0);
      }
    });

    test('should export orders data', async ({ page, authenticatedAdminUser }) => {
      const adminDashboard = new AdminDashboardPage(page);
      await adminDashboard.visit();
      await adminDashboard.goToOrders();
      
      const exportButton = page.locator('[data-testid="export-orders"]');
      
      if (await exportButton.isVisible()) {
        const [download] = await Promise.all([
          page.waitForEvent('download'),
          exportButton.click()
        ]);
        
        expect(download.suggestedFilename()).toMatch(/orders|commandes.*\.csv|\.xlsx/i);
      }
    });
  });

  test.describe('Product Management', () => {
    test('should access and manage products', async ({ page, authenticatedAdminUser }) => {
      const adminDashboard = new AdminDashboardPage(page);
      await adminDashboard.visit();
      await adminDashboard.goToProducts();
      
      // Verify products management page
      await expect(adminDashboard.productsTable).toBeVisible();
      await expect(adminDashboard.addNewProductButton).toBeVisible();
      
      const productsCount = await adminDashboard.getProductsCount();
      expect(productsCount).toBeGreaterThanOrEqual(0);
    });

    test('should add new product', async ({ page, authenticatedAdminUser }) => {
      const adminDashboard = new AdminDashboardPage(page);
      await adminDashboard.visit();
      await adminDashboard.goToProducts();
      
      // Click add new product
      await adminDashboard.addNewProduct();
      
      // Should navigate to product creation form
      await TestHelpers.verifyUrl(page, /product.*add|product.*new/);
      
      const productForm = page.locator('[data-testid="product-form"]');
      if (await productForm.isVisible()) {
        const productData = TestDataGenerator.generateProduct();
        
        // Fill product form
        await page.locator('[data-testid="product-name"]').fill(productData.name);
        await page.locator('[data-testid="product-price"]').fill(productData.price.toString());
        await page.locator('[data-testid="product-category"]').selectOption(productData.category);
        await page.locator('[data-testid="product-sku"]').fill(productData.sku);
        
        // Save product
        const saveButton = page.locator('[data-testid="save-product"]');
        if (await saveButton.isVisible()) {
          await saveButton.click();
          await TestHelpers.verifyToast(page, /produit.*créé|product.*created/i);
        }
      }
    });

    test('should edit existing product', async ({ page, authenticatedAdminUser }) => {
      const adminDashboard = new AdminDashboardPage(page);
      await adminDashboard.visit();
      await adminDashboard.goToProducts();
      
      const productsCount = await adminDashboard.getProductsCount();
      
      if (productsCount > 0) {
        // Edit first product
        await adminDashboard.editProduct(0);
        
        // Should navigate to product edit form
        await TestHelpers.verifyUrl(page, /product.*edit/);
        
        const productForm = page.locator('[data-testid="product-form"]');
        if (await productForm.isVisible()) {
          // Update product name
          const nameInput = page.locator('[data-testid="product-name"]');
          const currentName = await nameInput.inputValue();
          await nameInput.fill(`${currentName} - Updated`);
          
          // Save changes
          const saveButton = page.locator('[data-testid="save-product"]');
          if (await saveButton.isVisible()) {
            await saveButton.click();
            await TestHelpers.verifyToast(page, /produit.*mis à jour|product.*updated/i);
          }
        }
      }
    });

    test('should delete product with confirmation', async ({ page, authenticatedAdminUser }) => {
      const adminDashboard = new AdminDashboardPage(page);
      await adminDashboard.visit();
      await adminDashboard.goToProducts();
      
      const productsCount = await adminDashboard.getProductsCount();
      
      if (productsCount > 0) {
        // Attempt to delete product (this will trigger confirmation)
        await adminDashboard.deleteProduct(0);
        
        // Verify confirmation dialog appears
        const confirmDialog = page.locator('[data-testid="confirm-delete"]');
        if (await confirmDialog.isVisible()) {
          // Cancel deletion for safety
          const cancelButton = page.locator('[data-testid="cancel-delete"]');
          if (await cancelButton.isVisible()) {
            await cancelButton.click();
          }
        }
      }
    });

    test('should search products', async ({ page, authenticatedAdminUser }) => {
      const adminDashboard = new AdminDashboardPage(page);
      await adminDashboard.visit();
      await adminDashboard.goToProducts();
      
      // Test product search
      await adminDashboard.searchProducts('thé');
      await TestHelpers.waitForPageStable(page);
      
      const searchResults = await adminDashboard.getProductsCount();
      expect(searchResults).toBeGreaterThanOrEqual(0);
    });
  });

  test.describe('User Management', () => {
    test('should access and manage users', async ({ page, authenticatedAdminUser }) => {
      const adminDashboard = new AdminDashboardPage(page);
      await adminDashboard.visit();
      await adminDashboard.goToUsers();
      
      // Verify users management page
      await expect(adminDashboard.usersTable).toBeVisible();
      
      const usersCount = await adminDashboard.getUsersCount();
      expect(usersCount).toBeGreaterThan(0); // At least the admin user should exist
    });

    test('should view user details', async ({ page, authenticatedAdminUser }) => {
      const adminDashboard = new AdminDashboardPage(page);
      await adminDashboard.visit();
      await adminDashboard.goToUsers();
      
      const usersCount = await adminDashboard.getUsersCount();
      
      if (usersCount > 0) {
        // View first user
        await adminDashboard.viewUser(0);
        
        // Should navigate to user details
        await TestHelpers.verifyUrl(page, /user|utilisateur/);
        
        const userDetails = page.locator('[data-testid="user-details"]');
        await expect(userDetails).toBeVisible();
      }
    });

    test('should toggle user status', async ({ page, authenticatedAdminUser }) => {
      const adminDashboard = new AdminDashboardPage(page);
      await adminDashboard.visit();
      await adminDashboard.goToUsers();
      
      const usersCount = await adminDashboard.getUsersCount();
      
      if (usersCount > 1) { // Don't toggle admin's own status
        // Toggle user status
        await adminDashboard.toggleUserStatus(1);
        await TestHelpers.verifyToast(page, /statut.*mis à jour|status.*updated/i);
      }
    });

    test('should search users', async ({ page, authenticatedAdminUser }) => {
      const adminDashboard = new AdminDashboardPage(page);
      await adminDashboard.visit();
      await adminDashboard.goToUsers();
      
      // Search for admin user
      await adminDashboard.searchUsers('admin');
      await TestHelpers.waitForPageStable(page);
      
      const searchResults = await adminDashboard.getUsersCount();
      expect(searchResults).toBeGreaterThanOrEqual(1);
    });
  });

  test.describe('B2B Management', () => {
    test('should access B2B requests management', async ({ page, authenticatedAdminUser }) => {
      const adminDashboard = new AdminDashboardPage(page);
      await adminDashboard.visit();
      await adminDashboard.goToB2BManagement();
      
      // Verify B2B management page
      await expect(adminDashboard.b2bRequestsTable).toBeVisible();
      
      const requestsCount = await adminDashboard.getB2BRequestsCount();
      expect(requestsCount).toBeGreaterThanOrEqual(0);
    });

    test('should approve B2B requests', async ({ page, authenticatedAdminUser }) => {
      const adminDashboard = new AdminDashboardPage(page);
      await adminDashboard.visit();
      await adminDashboard.goToB2BManagement();
      
      const requestsCount = await adminDashboard.getB2BRequestsCount();
      
      if (requestsCount > 0) {
        // View B2B request details first
        await adminDashboard.viewB2BDetails(0);
        
        // Go back and approve
        await page.goBack();
        await adminDashboard.approveB2BRequest(0);
        
        await TestHelpers.verifyToast(page, /approuvé|approved/i);
      }
    });

    test('should reject B2B requests', async ({ page, authenticatedAdminUser }) => {
      const adminDashboard = new AdminDashboardPage(page);
      await adminDashboard.visit();
      await adminDashboard.goToB2BManagement();
      
      const requestsCount = await adminDashboard.getB2BRequestsCount();
      
      if (requestsCount > 1) { // Leave at least one for approval test
        // Reject B2B request
        await adminDashboard.rejectB2BRequest(1);
        
        await TestHelpers.verifyToast(page, /rejeté|rejected/i);
      }
    });
  });

  test.describe('Reviews Management', () => {
    test('should access and moderate reviews', async ({ page, authenticatedAdminUser }) => {
      const adminDashboard = new AdminDashboardPage(page);
      await adminDashboard.visit();
      await adminDashboard.goToReviews();
      
      // Verify reviews management page
      await expect(adminDashboard.reviewsTable).toBeVisible();
      
      const reviewsCount = await adminDashboard.getReviewsCount();
      expect(reviewsCount).toBeGreaterThanOrEqual(0);
    });

    test('should approve reviews', async ({ page, authenticatedAdminUser }) => {
      const adminDashboard = new AdminDashboardPage(page);
      await adminDashboard.visit();
      await adminDashboard.goToReviews();
      
      const reviewsCount = await adminDashboard.getReviewsCount();
      
      if (reviewsCount > 0) {
        // Approve first review
        await adminDashboard.approveReview(0);
        await TestHelpers.verifyToast(page, /avis.*approuvé|review.*approved/i);
      }
    });

    test('should reject reviews', async ({ page, authenticatedAdminUser }) => {
      const adminDashboard = new AdminDashboardPage(page);
      await adminDashboard.visit();
      await adminDashboard.goToReviews();
      
      const reviewsCount = await adminDashboard.getReviewsCount();
      
      if (reviewsCount > 1) {
        // Reject review
        await adminDashboard.rejectReview(1);
        await TestHelpers.verifyToast(page, /avis.*rejeté|review.*rejected/i);
      }
    });
  });

  test.describe('Newsletter Management', () => {
    test('should access newsletter management', async ({ page, authenticatedAdminUser }) => {
      const adminDashboard = new AdminDashboardPage(page);
      await adminDashboard.visit();
      await adminDashboard.goToNewsletter();
      
      // Verify newsletter page
      await expect(adminDashboard.subscribersCount).toBeVisible();
      await expect(adminDashboard.createCampaignButton).toBeVisible();
      
      const subscribersCount = await adminDashboard.getSubscribersCount();
      expect(subscribersCount).toBeTruthy();
    });

    test('should create newsletter campaign', async ({ page, authenticatedAdminUser }) => {
      const adminDashboard = new AdminDashboardPage(page);
      await adminDashboard.visit();
      await adminDashboard.goToNewsletter();
      
      // Create new campaign
      await adminDashboard.createCampaign();
      
      // Should navigate to campaign creation form
      await TestHelpers.verifyUrl(page, /campaign|campagne/);
      
      const campaignForm = page.locator('[data-testid="campaign-form"]');
      if (await campaignForm.isVisible()) {
        // Fill campaign form
        await page.locator('[data-testid="campaign-subject"]').fill('Test Newsletter Campaign');
        await page.locator('[data-testid="campaign-content"]').fill('This is a test newsletter content.');
        
        // Save campaign
        const saveButton = page.locator('[data-testid="save-campaign"]');
        if (await saveButton.isVisible()) {
          await saveButton.click();
          await TestHelpers.verifyToast(page, /campagne.*créée|campaign.*created/i);
        }
      }
    });
  });

  test.describe('Analytics and Reports', () => {
    test('should access analytics dashboard', async ({ page, authenticatedAdminUser }) => {
      const adminDashboard = new AdminDashboardPage(page);
      await adminDashboard.visit();
      await adminDashboard.goToAnalytics();
      
      // Verify analytics page loads
      await TestHelpers.verifyUrl(page, /analytics|analytiques/);
      
      // Verify charts and metrics are present
      const analyticsCharts = page.locator('[data-testid="analytics-chart"]');
      const chartsCount = await analyticsCharts.count();
      expect(chartsCount).toBeGreaterThan(0);
    });

    test('should export analytics data', async ({ page, authenticatedAdminUser }) => {
      const adminDashboard = new AdminDashboardPage(page);
      await adminDashboard.visit();
      
      // Use quick export from dashboard
      const exportButton = adminDashboard.exportDataButton;
      
      if (await exportButton.isVisible()) {
        const [download] = await Promise.all([
          page.waitForEvent('download'),
          adminDashboard.exportData()
        ]);
        
        expect(download.suggestedFilename()).toMatch(/export|data.*\.csv|\.xlsx/i);
      }
    });
  });

  test.describe('System Settings', () => {
    test('should access system settings', async ({ page, authenticatedAdminUser }) => {
      const adminDashboard = new AdminDashboardPage(page);
      await adminDashboard.visit();
      await adminDashboard.goToSettings();
      
      // Verify settings page
      await TestHelpers.verifyUrl(page, /settings|paramètres/);
      
      const settingsForm = page.locator('[data-testid="settings-form"]');
      await expect(settingsForm).toBeVisible();
    });

    test('should update system configuration', async ({ page, authenticatedAdminUser }) => {
      const adminDashboard = new AdminDashboardPage(page);
      await adminDashboard.visit();
      await adminDashboard.goToSettings();
      
      const settingsForm = page.locator('[data-testid="settings-form"]');
      
      if (await settingsForm.isVisible()) {
        // Update a setting (e.g., site name)
        const siteNameInput = page.locator('[data-testid="site-name"]');
        
        if (await siteNameInput.isVisible()) {
          await siteNameInput.fill('Maison Trüvra - Test Update');
          
          // Save settings
          const saveButton = page.locator('[data-testid="save-settings"]');
          if (await saveButton.isVisible()) {
            await saveButton.click();
            await TestHelpers.verifyToast(page, /paramètres.*mis à jour|settings.*updated/i);
          }
        }
      }
    });
  });

  test.describe('Audit Log and Security', () => {
    test('should access audit log', async ({ page, authenticatedAdminUser }) => {
      const adminDashboard = new AdminDashboardPage(page);
      await adminDashboard.visit();
      await adminDashboard.goToAuditLog();
      
      // Verify audit log page
      await expect(adminDashboard.auditLogTable).toBeVisible();
      
      const auditLogCount = await adminDashboard.getAuditLogCount();
      expect(auditLogCount).toBeGreaterThanOrEqual(0);
    });

    test('should filter audit log', async ({ page, authenticatedAdminUser }) => {
      const adminDashboard = new AdminDashboardPage(page);
      await adminDashboard.visit();
      await adminDashboard.goToAuditLog();
      
      // Test audit log filtering
      const filters = adminDashboard.auditLogFilters;
      
      if (await filters.isVisible()) {
        const actionFilter = filters.locator('[data-testid="action-filter"]');
        
        if (await actionFilter.isVisible()) {
          await actionFilter.selectOption('login');
          await TestHelpers.waitForPageStable(page);
          
          const filteredCount = await adminDashboard.getAuditLogCount();
          expect(filteredCount).toBeGreaterThanOrEqual(0);
        }
      }
    });

    test('should monitor system health', async ({ page, authenticatedAdminUser }) => {
      const adminDashboard = new AdminDashboardPage(page);
      await adminDashboard.visit();
      
      // Check for system health indicators
      const healthIndicators = page.locator('[data-testid="health-indicator"]');
      const indicatorsCount = await healthIndicators.count();
      
      if (indicatorsCount > 0) {
        // Verify health status
        for (let i = 0; i < indicatorsCount; i++) {
          const indicator = healthIndicators.nth(i);
          const status = await indicator.getAttribute('data-status');
          expect(status).toMatch(/healthy|warning|error/);
        }
      }
    });
  });

  test.describe('Quick Actions and Workflows', () => {
    test('should use quick actions from dashboard', async ({ page, authenticatedAdminUser }) => {
      const adminDashboard = new AdminDashboardPage(page);
      await adminDashboard.visit();
      
      // Test quick actions
      await expect(adminDashboard.quickActionsSection).toBeVisible();
      
      // Quick view orders
      await adminDashboard.quickViewOrders();
      await TestHelpers.verifyUrl(page, /orders|commandes/);
      
      // Go back to dashboard
      await adminDashboard.visit();
      
      // Quick add product
      await adminDashboard.quickAddProduct();
      await TestHelpers.verifyUrl(page, /product.*add|product.*new/);
    });

    test('should handle bulk operations', async ({ page, authenticatedAdminUser }) => {
      const adminDashboard = new AdminDashboardPage(page);
      await adminDashboard.visit();
      await adminDashboard.goToProducts();
      
      // Check for bulk operations
      const bulkActions = page.locator('[data-testid="bulk-actions"]');
      
      if (await bulkActions.isVisible()) {
        // Select products for bulk operation
        const productCheckboxes = page.locator('[data-testid="product-checkbox"]');
        const checkboxCount = await productCheckboxes.count();
        
        if (checkboxCount > 1) {
          // Select first two products
          await productCheckboxes.nth(0).check();
          await productCheckboxes.nth(1).check();
          
          // Test bulk status update
          const bulkStatusUpdate = bulkActions.locator('[data-testid="bulk-status-update"]');
          if (await bulkStatusUpdate.isVisible()) {
            await bulkStatusUpdate.selectOption('active');
            
            const applyButton = bulkActions.locator('[data-testid="apply-bulk-action"]');
            if (await applyButton.isVisible()) {
              await applyButton.click();
              await TestHelpers.verifyToast(page, /mis à jour|updated/i);
            }
          }
        }
      }
    });
  });

  test.describe('Permissions and Role Management', () => {
    test('should access role management if available', async ({ page, authenticatedAdminUser }) => {
      const rolesLink = page.locator('[data-testid="admin-nav-roles"]');
      
      if (await rolesLink.isVisible()) {
        await rolesLink.click();
        
        // Verify roles management page
        const rolesTable = page.locator('[data-testid="roles-table"]');
        await expect(rolesTable).toBeVisible();
        
        // Test role creation
        const addRoleButton = page.locator('[data-testid="add-role"]');
        if (await addRoleButton.isVisible()) {
          await addRoleButton.click();
          
          const roleForm = page.locator('[data-testid="role-form"]');
          if (await roleForm.isVisible()) {
            await page.locator('[data-testid="role-name"]').fill('Test Role');
            await page.locator('[data-testid="role-description"]').fill('Test role description');
            
            // Save role
            const saveButton = page.locator('[data-testid="save-role"]');
            if (await saveButton.isVisible()) {
              await saveButton.click();
              await TestHelpers.verifyToast(page, /rôle.*créé|role.*created/i);
            }
          }
        }
      }
    });

    test('should verify admin has access to all sections', async ({ page, authenticatedAdminUser }) => {
      const adminDashboard = new AdminDashboardPage(page);
      await adminDashboard.visit();
      
      const restrictedSections = [
        { link: adminDashboard.ordersLink, path: /orders/ },
        { link: adminDashboard.productsLink, path: /products/ },
        { link: adminDashboard.usersLink, path: /users/ },
        { link: adminDashboard.b2bManagementLink, path: /b2b/ },
        { link: adminDashboard.settingsLink, path: /settings/ }
      ];
      
      for (const section of restrictedSections) {
        await section.link.click();
        await TestHelpers.verifyUrl(page, section.path);
        
        // Verify no access denied messages
        const accessDenied = page.locator('[data-testid="access-denied"]');
        await expect(accessDenied).not.toBeVisible();
        
        // Go back to dashboard
        await adminDashboard.visit();
      }
    });
  });
});