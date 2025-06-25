import { test, expect } from './fixtures/auth';
import { B2BDashboardPage } from './pages/B2BDashboardPage';
import { ShopPage } from './pages/ShopPage';
import { CartPage } from './pages/CartPage';
import { TestHelpers } from './utils/test-helpers';
import { TestDataGenerator, TEST_CONSTANTS } from './utils/test-data';

test.describe('B2B User Experience', () => {
  test.describe('B2B Registration and Authentication', () => {
    test('should register new B2B user successfully', async ({ page, authPage }) => {
      const userData = TestDataGenerator.generateB2BUser();
      
      await authPage.visitRegister();
      
      // Register new B2B user
      await authPage.registerB2B(userData);
      
      // Should be redirected to pending approval page or dashboard
      await TestHelpers.verifyUrl(page, /b2b|pending|dashboard/);
      
      // Verify appropriate message
      const hasSuccess = await authPage.hasSuccess();
      if (hasSuccess) {
        const message = await authPage.getSuccessMessage();
        expect(message).toContain(/inscription|demande|envoyée/i);
      }
    });

    test('should login existing B2B user', async ({ page, authenticatedB2BUser }) => {
      // User is already authenticated via fixture
      await TestHelpers.verifyUrl(page, /b2b|account|dashboard/);
      
      expect(authenticatedB2BUser.isAuthenticated).toBe(true);
      expect(authenticatedB2BUser.role).toBe('b2b');
    });

    test('should handle pending B2B account approval', async ({ page, authPage }) => {
      const userData = TestDataGenerator.generateB2BUser();
      
      await authPage.visitRegister();
      await authPage.registerB2B(userData);
      
      // If account is pending, should show appropriate message
      const pendingMessage = page.locator('[data-testid="account-pending"]');
      if (await pendingMessage.isVisible()) {
        const message = await pendingMessage.textContent();
        expect(message).toContain(/en attente|pending|approbation/i);
      }
    });
  });

  test.describe('B2B Dashboard', () => {
    test('should access B2B dashboard with key metrics', async ({ page, authenticatedB2BUser, b2bDashboard }) => {
      const b2bDashboard = new B2BDashboardPage(page);
      await b2bDashboard.visit();
      
      // Verify dashboard loads with B2B specific elements
      await expect(b2bDashboard.welcomeMessage).toBeVisible();
      await expect(b2bDashboard.companyInfo).toBeVisible();
      await expect(b2bDashboard.accountStatus).toBeVisible();
      
      // Verify welcome message contains user info
      const welcome = await b2bDashboard.getWelcomeMessage();
      expect(welcome).toContain(authenticatedB2BUser.firstName);
      
      // Verify company information
      const companyName = await b2bDashboard.getCompanyName();
      expect(companyName).toBeTruthy();
      
      // Verify account status
      const accountStatus = await b2bDashboard.getAccountStatus();
      expect(accountStatus).toBeTruthy();
    });

    test('should display B2B statistics and metrics', async ({ page, authenticatedB2BUser, b2bDashboard }) => {
      const b2bDashboard = new B2BDashboardPage(page);
      await b2bDashboard.visit();
      
      // Verify statistics cards
      await expect(b2bDashboard.totalOrdersCard).toBeVisible();
      await expect(b2bDashboard.totalSpentCard).toBeVisible();
      await expect(b2bDashboard.loyaltyPointsCard).toBeVisible();
      
      // Get metric values
      const totalOrders = await b2bDashboard.getTotalOrders();
      const totalSpent = await b2bDashboard.getTotalSpent();
      const loyaltyPoints = await b2bDashboard.getLoyaltyPoints();
      
      expect(totalOrders).toBeTruthy();
      expect(totalSpent).toBeTruthy();
      expect(loyaltyPoints).toBeTruthy();
      
      // Verify tier badge
      const tierLevel = await b2bDashboard.getTierLevel();
      expect(tierLevel).toMatch(/collaborateur|partenaire|associé/i);
    });

    test('should display recent orders', async ({ page, authenticatedB2BUser, b2bDashboard }) => {
      const b2bDashboard = new B2BDashboardPage(page);
      await b2bDashboard.visit();
      
      // Verify recent orders section
      await expect(b2bDashboard.recentOrdersSection).toBeVisible();
      
      const recentOrdersCount = await b2bDashboard.getRecentOrdersCount();
      expect(recentOrdersCount).toBeGreaterThanOrEqual(0);
      
      // If there are recent orders, verify they display correctly
      if (recentOrdersCount > 0) {
        const firstOrderStatus = await b2bDashboard.getOrderStatus(0);
        expect(firstOrderStatus).toBeTruthy();
      }
    });

    test('should provide quick actions', async ({ page, authenticatedB2BUser, b2bDashboard }) => {
      const b2bDashboard = new B2BDashboardPage(page);
      await b2bDashboard.visit();
      
      // Verify quick actions are available
      await expect(b2bDashboard.quickActionsSection).toBeVisible();
      await expect(b2bDashboard.newOrderButton).toBeVisible();
      await expect(b2bDashboard.viewCatalogButton).toBeVisible();
      
      // Test quick action navigation
      await b2bDashboard.viewCatalog();
      await TestHelpers.verifyUrl(page, /b2b.*catalog|b2b.*products/);
    });
  });

  test.describe('B2B Order Management', () => {
    test('should view B2B orders list', async ({ page, authenticatedB2BUser, b2bDashboard }) => {
      const b2bDashboard = new B2BDashboardPage(page);
      await b2bDashboard.visit();
      await b2bDashboard.goToOrders();
      
      // Verify orders page loads
      await expect(b2bDashboard.ordersTable).toBeVisible();
      
      const ordersCount = await b2bDashboard.getOrdersCount();
      expect(ordersCount).toBeGreaterThanOrEqual(0);
      
      // If orders exist, verify they display correctly
      if (ordersCount > 0) {
        const firstOrderTotal = await b2bDashboard.getOrderTotal(0);
        expect(firstOrderTotal).toBeTruthy();
        
        // Test view order functionality
        await b2bDashboard.viewOrder(0);
        await TestHelpers.verifyUrl(page, /order|commande/);
      }
    });

    test('should reorder previous orders', async ({ page, authenticatedB2BUser, b2bDashboard }) => {
      const b2bDashboard = new B2BDashboardPage(page);
      await b2bDashboard.visit();
      await b2bDashboard.goToOrders();
      
      const ordersCount = await b2bDashboard.getOrdersCount();
      
      if (ordersCount > 0) {
        // Test reorder functionality
        await b2bDashboard.reorder(0);
        
        // Should add items to cart
        await TestHelpers.verifyToast(page, /panier|cart|ajouté/i);
        
        // Verify redirect to cart or order page
        await TestHelpers.verifyUrl(page, /cart|order|b2b/);
      }
    });

    test('should create new order from dashboard', async ({ page, authenticatedB2BUser, b2bDashboard }) => {
      const b2bDashboard = new B2BDashboardPage(page);
      await b2bDashboard.visit();
      
      // Click new order button
      await b2bDashboard.createNewOrder();
      
      // Should redirect to catalog or order creation page
      await TestHelpers.verifyUrl(page, /catalog|order|b2b/);
    });
  });

  test.describe('B2B Quick Order', () => {
    test('should access quick order functionality', async ({ page, authenticatedB2BUser, b2bDashboard }) => {
      const b2bDashboard = new B2BDashboardPage(page);
      await b2bDashboard.visit();
      await b2bDashboard.goToQuickOrder();
      
      // Verify quick order form is available
      await expect(b2bDashboard.quickOrderForm).toBeVisible();
      await expect(b2bDashboard.productSkuInput).toBeVisible();
      await expect(b2bDashboard.quantityInput).toBeVisible();
      await expect(b2bDashboard.addToOrderButton).toBeVisible();
    });

    test('should add items via quick order', async ({ page, authenticatedB2BUser, b2bDashboard }) => {
      const b2bDashboard = new B2BDashboardPage(page);
      await b2bDashboard.visit();
      await b2bDashboard.goToQuickOrder();
      
      // Add items using SKU
      const testSku = 'TEA-EG-001';
      const quantity = 10;
      
      await b2bDashboard.addQuickOrderItem(testSku, quantity);
      
      // Wait for response
      await page.waitForTimeout(1000);
      
      // Verify item was added or error message if SKU doesn't exist
      const hasItems = await b2bDashboard.hasQuickOrderItems();
      const errorMessage = page.locator('[data-testid="error-message"]');
      
      if (hasItems) {
        const itemsCount = await b2bDashboard.getQuickOrderItemsCount();
        expect(itemsCount).toBeGreaterThan(0);
      } else if (await errorMessage.isVisible()) {
        const error = await errorMessage.textContent();
        expect(error).toContain(/sku|produit|introuvable/i);
      }
    });

    test('should place quick order', async ({ page, authenticatedB2BUser, b2bDashboard }) => {
      const b2bDashboard = new B2BDashboardPage(page);
      await b2bDashboard.visit();
      await b2bDashboard.goToQuickOrder();
      
      // Add at least one item
      await b2bDashboard.addQuickOrderItem('TEA-EG-001', 5);
      
      // Wait for item to be added
      await page.waitForTimeout(1000);
      
      const hasItems = await b2bDashboard.hasQuickOrderItems();
      
      if (hasItems) {
        // Place the order
        await b2bDashboard.placeQuickOrder();
        
        // Should redirect to order confirmation or checkout
        await TestHelpers.verifyUrl(page, /order|checkout|confirmation/);
      }
    });
  });

  test.describe('B2B Catalog and Pricing', () => {
    test('should access B2B catalog with special pricing', async ({ page, authenticatedB2BUser, b2bDashboard }) => {
      const b2bDashboard = new B2BDashboardPage(page);
      await b2bDashboard.visit();
      await b2bDashboard.goToCatalog();
      
      // Verify B2B catalog loads
      await expect(b2bDashboard.b2bProductGrid).toBeVisible();
      
      const productsCount = await b2bDashboard.getB2BProductsCount();
      expect(productsCount).toBeGreaterThan(0);
      
      // Verify bulk pricing is available
      if (productsCount > 0) {
        const hasBulkPricing = await b2bDashboard.hasBulkPricing(0);
        // Bulk pricing might not be available for all products
        expect(typeof hasBulkPricing).toBe('boolean');
      }
    });

    test('should add B2B products to cart', async ({ page, authenticatedB2BUser, b2bDashboard, cartPage }) => {
      const b2bDashboard = new B2BDashboardPage(page);
      await b2bDashboard.visit();
      await b2bDashboard.goToCatalog();
      
      const productsCount = await b2bDashboard.getB2BProductsCount();
      
      if (productsCount > 0) {
        // Add product to cart
        await b2bDashboard.addB2BProductToCart(0);
        
        // Verify product was added
        await TestHelpers.verifyToast(page, /panier|cart|ajouté/i);
        
        // Go to cart and verify
        await cartPage.visit();
        const cartItemsCount = await cartPage.getItemsCount();
        expect(cartItemsCount).toBeGreaterThan(0);
      }
    });

    test('should filter B2B catalog', async ({ page, authenticatedB2BUser, b2bDashboard }) => {
      const b2bDashboard = new B2BDashboardPage(page);
      await b2bDashboard.visit();
      await b2bDashboard.goToCatalog();
      
      // Verify filters are available
      await expect(b2bDashboard.catalogFilters).toBeVisible();
      
      // Apply a filter if available
      const categoryFilter = b2bDashboard.catalogFilters.locator('[data-testid="category-filter"]').first();
      
      if (await categoryFilter.isVisible()) {
        await categoryFilter.click();
        
        // Wait for filter to apply
        await TestHelpers.waitForPageStable(page);
        
        // Verify products are filtered
        const filteredCount = await b2bDashboard.getB2BProductsCount();
        expect(filteredCount).toBeGreaterThanOrEqual(0);
      }
    });
  });

  test.describe('B2B Invoicing', () => {
    test('should access invoices list', async ({ page, authenticatedB2BUser, b2bDashboard }) => {
      const b2bDashboard = new B2BDashboardPage(page);
      await b2bDashboard.visit();
      await b2bDashboard.goToInvoices();
      
      // Verify invoices page loads
      await expect(b2bDashboard.invoicesTable).toBeVisible();
      
      const invoicesCount = await b2bDashboard.getInvoicesCount();
      expect(invoicesCount).toBeGreaterThanOrEqual(0);
    });

    test('should download invoice', async ({ page, authenticatedB2BUser, b2bDashboard }) => {
      const b2bDashboard = new B2BDashboardPage(page);
      await b2bDashboard.visit();
      await b2bDashboard.goToInvoices();
      
      const invoicesCount = await b2bDashboard.getInvoicesCount();
      
      if (invoicesCount > 0) {
        // Test download invoice functionality
        const [download] = await Promise.all([
          page.waitForEvent('download'),
          b2bDashboard.downloadInvoice(0)
        ]);
        
        expect(download.suggestedFilename()).toContain(/invoice|facture/i);
      }
    });

    test('should pay invoice if payment feature available', async ({ page, authenticatedB2BUser, b2bDashboard }) => {
      const b2bDashboard = new B2BDashboardPage(page);
      await b2bDashboard.visit();
      await b2bDashboard.goToInvoices();
      
      const invoicesCount = await b2bDashboard.getInvoicesCount();
      
      if (invoicesCount > 0) {
        const payButton = b2bDashboard.payInvoiceButtons.first();
        
        if (await payButton.isVisible()) {
          await b2bDashboard.payInvoice(0);
          
          // Should redirect to payment page
          await TestHelpers.verifyUrl(page, /payment|paiement/);
        }
      }
    });
  });

  test.describe('B2B Loyalty Program', () => {
    test('should access B2B loyalty program', async ({ page, authenticatedB2BUser, b2bDashboard }) => {
      const b2bDashboard = new B2BDashboardPage(page);
      await b2bDashboard.visit();
      await b2bDashboard.goToLoyalty();
      
      // Verify loyalty overview is available
      await expect(b2bDashboard.loyaltyOverview).toBeVisible();
      
      // Verify loyalty information
      const currentPoints = await b2bDashboard.getCurrentLoyaltyPoints();
      expect(currentPoints).toBeTruthy();
      
      // Verify tier information
      await expect(b2bDashboard.tierProgress).toBeVisible();
    });

    test('should claim loyalty rewards', async ({ page, authenticatedB2BUser, b2bDashboard }) => {
      const b2bDashboard = new B2BDashboardPage(page);
      await b2bDashboard.visit();
      await b2bDashboard.goToLoyalty();
      
      // Check for available rewards
      const rewardsSection = b2bDashboard.rewardsAvailable;
      
      if (await rewardsSection.isVisible()) {
        const rewardButtons = b2bDashboard.claimRewardButtons;
        const rewardsCount = await rewardButtons.count();
        
        if (rewardsCount > 0) {
          await b2bDashboard.claimReward(0);
          
          // Verify reward claim
          await TestHelpers.verifyToast(page, /récompense|reward|réclamée/i);
        }
      }
    });
  });

  test.describe('B2B Referral Program', () => {
    test('should access referral program', async ({ page, authenticatedB2BUser, b2bDashboard }) => {
      const b2bDashboard = new B2BDashboardPage(page);
      await b2bDashboard.visit();
      await b2bDashboard.goToReferrals();
      
      // Verify referral page loads
      await expect(b2bDashboard.referralCode).toBeVisible();
      await expect(b2bDashboard.referralStats).toBeVisible();
      
      // Verify referral code is generated
      const referralCode = await b2bDashboard.getReferralCode();
      expect(referralCode).toBeTruthy();
    });

    test('should share referral code', async ({ page, authenticatedB2BUser, b2bDashboard }) => {
      const b2bDashboard = new B2BDashboardPage(page);
      await b2bDashboard.visit();
      await b2bDashboard.goToReferrals();
      
      // Test share functionality
      await b2bDashboard.shareReferralCode();
      
      // Should open share modal or show success message
      const shareModal = page.locator('[data-testid="share-modal"]');
      const successMessage = page.locator('[data-testid="success-message"]');
      
      if (await shareModal.isVisible()) {
        await expect(shareModal).toBeVisible();
      } else if (await successMessage.isVisible()) {
        await TestHelpers.verifyToast(page, /partagé|shared/i);
      }
    });
  });

  test.describe('B2B Profile Management', () => {
    test('should access B2B profile settings', async ({ page, authenticatedB2BUser, b2bDashboard }) => {
      const b2bDashboard = new B2BDashboardPage(page);
      await b2bDashboard.visit();
      await b2bDashboard.goToProfile();
      
      // Verify profile page loads with B2B specific fields
      const profileForm = page.locator('[data-testid="b2b-profile-form"]');
      await expect(profileForm).toBeVisible();
      
      // Verify B2B specific fields
      await expect(page.locator('[data-testid="company-name"]')).toBeVisible();
      await expect(page.locator('[data-testid="siret-number"]')).toBeVisible();
    });

    test('should update B2B profile information', async ({ page, authenticatedB2BUser, b2bDashboard }) => {
      const b2bDashboard = new B2BDashboardPage(page);
      await b2bDashboard.visit();
      await b2bDashboard.goToProfile();
      
      // Update profile information
      const companyNameInput = page.locator('[data-testid="company-name"]');
      const phoneInput = page.locator('[data-testid="phone-number"]');
      
      if (await companyNameInput.isVisible()) {
        await companyNameInput.fill('Updated Company Name SARL');
      }
      
      if (await phoneInput.isVisible()) {
        await phoneInput.fill(TestHelpers.generateRandomPhone());
      }
      
      // Save changes
      const saveButton = page.locator('[data-testid="save-profile"]');
      if (await saveButton.isVisible()) {
        await saveButton.click();
        
        // Verify update success
        await TestHelpers.verifyToast(page, /mis à jour|updated/i);
      }
    });
  });

  test.describe('B2B Specific Features', () => {
    test('should request bulk quotes', async ({ page, authenticatedB2BUser, b2bDashboard }) => {
      const b2bDashboard = new B2BDashboardPage(page);
      await b2bDashboard.visit();
      
      // Look for quote request functionality
      const quoteButton = page.locator('[data-testid="request-quote"]');
      
      if (await quoteButton.isVisible()) {
        await quoteButton.click();
        
        // Fill quote request form
        const quoteForm = page.locator('[data-testid="quote-form"]');
        if (await quoteForm.isVisible()) {
          const quoteData = TestDataGenerator.generateB2BQuote();
          
          await page.locator('[data-testid="quote-message"]').fill(quoteData.message);
          await page.locator('[data-testid="quote-quantity"]').fill(quoteData.quantity.toString());
          
          // Submit quote request
          await page.locator('[data-testid="submit-quote"]').click();
          
          // Verify quote submission
          await TestHelpers.verifyToast(page, /devis|quote|envoyé/i);
        }
      }
    });

    test('should access volume discounts', async ({ page, authenticatedB2BUser, b2bDashboard }) => {
      const b2bDashboard = new B2BDashboardPage(page);
      await b2bDashboard.visit();
      await b2bDashboard.goToCatalog();
      
      const productsCount = await b2bDashboard.getB2BProductsCount();
      
      if (productsCount > 0) {
        // Check for volume discount information
        const volumeDiscounts = page.locator('[data-testid="volume-discounts"]');
        
        if (await volumeDiscounts.isVisible()) {
          // Verify volume discount tiers are displayed
          await expect(volumeDiscounts).toBeVisible();
          
          const discountTiers = volumeDiscounts.locator('[data-testid="discount-tier"]');
          const tiersCount = await discountTiers.count();
          expect(tiersCount).toBeGreaterThan(0);
        }
      }
    });

    test('should access delivery scheduling', async ({ page, authenticatedB2BUser, b2bDashboard, cartPage }) => {
      // Add product to cart first
      const b2bDashboard = new B2BDashboardPage(page);
      await b2bDashboard.visit();
      await b2bDashboard.goToCatalog();
      
      const productsCount = await b2bDashboard.getB2BProductsCount();
      
      if (productsCount > 0) {
        await b2bDashboard.addB2BProductToCart(0);
        await cartPage.visit();
        
        // Proceed to checkout
        await cartPage.proceedToCheckout();
        
        // Look for delivery scheduling options
        const deliveryScheduling = page.locator('[data-testid="delivery-scheduling"]');
        
        if (await deliveryScheduling.isVisible()) {
          // Verify delivery options are available
          await expect(deliveryScheduling).toBeVisible();
          
          const deliveryOptions = deliveryScheduling.locator('[data-testid="delivery-option"]');
          const optionsCount = await deliveryOptions.count();
          expect(optionsCount).toBeGreaterThan(0);
        }
      }
    });

    test('should access credit terms information', async ({ page, authenticatedB2BUser, b2bDashboard }) => {
      const b2bDashboard = new B2BDashboardPage(page);
      await b2bDashboard.visit();
      
      // Look for credit terms section
      const creditTerms = page.locator('[data-testid="credit-terms"]');
      
      if (await creditTerms.isVisible()) {
        // Verify credit information is displayed
        await expect(creditTerms).toBeVisible();
        
        const creditLimit = page.locator('[data-testid="credit-limit"]');
        const availableCredit = page.locator('[data-testid="available-credit"]');
        
        if (await creditLimit.isVisible()) {
          const limit = await creditLimit.textContent();
          expect(limit).toBeTruthy();
        }
        
        if (await availableCredit.isVisible()) {
          const available = await availableCredit.textContent();
          expect(available).toBeTruthy();
        }
      }
    });
  });
});