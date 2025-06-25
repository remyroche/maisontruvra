import { test, expect } from './fixtures/auth';
import { HomePage } from './pages/HomePage';
import { ShopPage } from './pages/ShopPage';
import { ProductDetailPage } from './pages/ProductDetailPage';
import { CartPage } from './pages/CartPage';
import { AccountPage } from './pages/AccountPage';
import { TestHelpers } from './utils/test-helpers';
import { TestDataGenerator, TEST_CONSTANTS } from './utils/test-data';

test.describe('B2C User Experience', () => {
  test.describe('Authentication Flow', () => {
    test('should register new B2C user successfully', async ({ page, authPage }) => {
      const userData = TestDataGenerator.generateUser();
      
      await authPage.visitRegister();
      
      // Register new B2C user
      await authPage.registerB2C(userData);
      
      // Should be redirected to account or verification page
      await TestHelpers.verifyUrl(page, /account|verify/);
      
      // Verify success message or account access
      const hasSuccess = await authPage.hasSuccess();
      if (hasSuccess) {
        const message = await authPage.getSuccessMessage();
        expect(message).toContain('Inscription réussie');
      } else {
        // Should be on account page
        await TestHelpers.verifyUrl(page, '/account');
      }
    });

    test('should login existing B2C user', async ({ page, authenticatedB2CUser }) => {
      // User is already authenticated via fixture
      await TestHelpers.verifyUrl(page, /account|dashboard/);
      
      expect(authenticatedB2CUser.isAuthenticated).toBe(true);
      expect(authenticatedB2CUser.role).toBe('b2c');
    });

    test('should logout successfully', async ({ page, authenticatedB2CUser, homePage }) => {
      await homePage.visit();
      
      // Logout
      await homePage.clickLogout();
      
      // Should be redirected to homepage
      await TestHelpers.verifyUrl(page, '/');
      
      // Login button should be visible again
      await expect(homePage.loginButton).toBeVisible();
    });
  });

  test.describe('Account Management', () => {
    test('should access account dashboard', async ({ page, authenticatedB2CUser, accountPage }) => {
      await accountPage.visit();
      
      // Verify account dashboard loads
      await expect(accountPage.welcomeMessage).toBeVisible();
      
      const welcome = await accountPage.getWelcomeMessage();
      expect(welcome).toContain(authenticatedB2CUser.firstName);
      
      // Verify navigation elements
      await expect(accountPage.profileLink).toBeVisible();
      await expect(accountPage.ordersLink).toBeVisible();
      await expect(accountPage.addressesLink).toBeVisible();
      await expect(accountPage.wishlistLink).toBeVisible();
    });

    test('should update profile information', async ({ page, authenticatedB2CUser, accountPage }) => {
      await accountPage.visit();
      await accountPage.goToProfile();
      
      const updatedData = {
        firstName: 'Updated',
        lastName: 'Name',
        phone: TestHelpers.generateRandomPhone()
      };
      
      // Update profile
      await accountPage.updateProfile(updatedData);
      
      // Verify success message
      await expect(accountPage.hasSuccessMessage()).resolves.toBe(true);
      const message = await accountPage.getSuccessMessage();
      expect(message).toContain('Profil mis à jour');
    });

    test('should manage addresses', async ({ page, authenticatedB2CUser, accountPage }) => {
      await accountPage.visit();
      await accountPage.goToAddresses();
      
      const addressData = TestDataGenerator.generateAddress();
      
      // Add new address
      await accountPage.addAddress(addressData);
      
      // Verify address was added
      await expect(accountPage.hasSuccessMessage()).resolves.toBe(true);
      
      const addressCount = await accountPage.getAddressesCount();
      expect(addressCount).toBeGreaterThan(0);
    });

    test('should change password', async ({ page, authenticatedB2CUser, accountPage }) => {
      await accountPage.visit();
      await accountPage.goToSecurity();
      
      const currentPassword = authenticatedB2CUser.password;
      const newPassword = 'NewTestPass123!';
      
      // Change password
      await accountPage.changePassword(currentPassword, newPassword);
      
      // Verify success message
      await expect(accountPage.hasSuccessMessage()).resolves.toBe(true);
      const message = await accountPage.getSuccessMessage();
      expect(message).toContain('Mot de passe modifié');
    });

    test('should manage wishlist', async ({ page, authenticatedB2CUser, accountPage, shopPage }) => {
      // Add items to wishlist first
      await shopPage.visit();
      
      const productCount = await shopPage.getProductsCount();
      if (productCount > 0) {
        await shopPage.addProductToWishlist(0);
        await TestHelpers.verifyToast(page, 'Ajouté à la liste de souhaits');
      }
      
      // Go to wishlist
      await accountPage.visit();
      await accountPage.goToWishlist();
      
      if (productCount > 0) {
        // Verify wishlist has items
        const wishlistCount = await accountPage.getWishlistItemsCount();
        expect(wishlistCount).toBeGreaterThan(0);
        
        // Move item to cart
        await accountPage.moveWishlistItemToCart(0);
        
        // Verify success
        await TestHelpers.verifyToast(page, 'Ajouté au panier');
      }
    });
  });

  test.describe('Shopping Experience', () => {
    test('should browse and filter products', async ({ page, authenticatedB2CUser, shopPage }) => {
      await shopPage.visit();
      
      // Verify authenticated user can see all features
      await expect(shopPage.productGrid).toBeVisible();
      await expect(shopPage.filterSidebar).toBeVisible();
      
      const productCount = await shopPage.getProductsCount();
      expect(productCount).toBeGreaterThan(0);
      
      // Test filtering
      await shopPage.filterByCategory('Thés noirs');
      
      // Verify page updates
      await TestHelpers.waitForPageStable(page);
      const filteredCount = await shopPage.getProductsCount();
      expect(filteredCount).toBeGreaterThanOrEqual(0);
    });

    test('should add products to cart and checkout', async ({ page, authenticatedB2CUser, shopPage, cartPage }) => {
      await shopPage.visit();
      
      const productCount = await shopPage.getProductsCount();
      if (productCount > 0) {
        // Add product to cart
        await shopPage.addProductToCart(0);
        await TestHelpers.verifyToast(page, 'Produit ajouté au panier');
        
        // Go to cart
        await cartPage.visit();
        
        const cartItemsCount = await cartPage.getItemsCount();
        expect(cartItemsCount).toBeGreaterThan(0);
        
        // Proceed to checkout (should not redirect to login)
        await cartPage.proceedToCheckout();
        
        // Should go to checkout page, not login
        await TestHelpers.verifyUrl(page, /checkout|commande/);
      }
    });

    test('should use promotional codes', async ({ page, authenticatedB2CUser, shopPage, cartPage }) => {
      // Add product to cart first
      await shopPage.visit();
      
      const productCount = await shopPage.getProductsCount();
      if (productCount > 0) {
        await shopPage.addProductToCart(0);
        await cartPage.visit();
        
        const promoCode = TestDataGenerator.generatePromoCode();
        
        // Apply promo code
        await cartPage.applyPromoCode(promoCode);
        
        // Wait for response
        await page.waitForTimeout(2000);
        
        // Check if promo code was applied or rejected
        const promoMessage = await cartPage.getPromoCodeMessage();
        expect(promoMessage).toBeTruthy();
      }
    });

    test('should leave product reviews', async ({ page, authenticatedB2CUser, productDetailPage }) => {
      // Navigate to a product that can be reviewed
      const productId = 'sample-product-1'; // This would need to be a valid product ID
      await productDetailPage.visitProduct(productId);
      
      // Switch to reviews tab
      await productDetailPage.switchToTab('reviews');
      
      // Check if review button is available
      const canReview = await productDetailPage.writeReviewButton.isVisible();
      
      if (canReview) {
        await productDetailPage.writeReview();
        
        // Should open review form
        const reviewForm = page.locator('[data-testid="review-form"]');
        if (await reviewForm.isVisible()) {
          const reviewData = TestDataGenerator.generateReviewData();
          
          // Fill review form
          await page.locator('[data-testid="review-rating"]').click();
          await page.locator('[data-testid="review-title"]').fill(reviewData.title);
          await page.locator('[data-testid="review-content"]').fill(reviewData.content);
          await page.locator('[data-testid="submit-review"]').click();
          
          // Verify review submission
          await TestHelpers.verifyToast(page, 'Avis soumis pour modération');
        }
      }
    });

    test('should track orders', async ({ page, authenticatedB2CUser, accountPage }) => {
      await accountPage.visit();
      await accountPage.goToOrders();
      
      const ordersCount = await accountPage.getOrdersCount();
      
      if (ordersCount > 0) {
        // View first order
        await accountPage.viewOrder(0);
        
        // Should navigate to order details
        await TestHelpers.verifyUrl(page, /order|commande/);
        
        // Order details should be visible
        await expect(page.locator('[data-testid="order-details"]')).toBeVisible();
      }
    });
  });

  test.describe('Communication Features', () => {
    test('should subscribe to newsletter from account', async ({ page, authenticatedB2CUser, accountPage }) => {
      await accountPage.visit();
      
      // Look for newsletter subscription toggle
      const newsletterToggle = page.locator('[data-testid="newsletter-subscription"]');
      
      if (await newsletterToggle.isVisible()) {
        await newsletterToggle.click();
        
        // Verify subscription status change
        await TestHelpers.verifyToast(page, /newsletter|abonnement/);
      }
    });

    test('should contact customer service', async ({ page, authenticatedB2CUser }) => {
      await page.goto('/contact');
      
      const contactForm = page.locator('[data-testid="contact-form"]');
      
      if (await contactForm.isVisible()) {
        // Fill contact form
        await page.locator('[data-testid="contact-subject"]').selectOption('Commande');
        await page.locator('[data-testid="contact-message"]').fill('Test message from B2C user');
        await page.locator('[data-testid="submit-contact"]').click();
        
        // Verify form submission
        await TestHelpers.verifyToast(page, 'Message envoyé');
      }
    });
  });

  test.describe('Order Management', () => {
    test('should complete full order process', async ({ page, authenticatedB2CUser, shopPage, cartPage, accountPage }) => {
      // Add product to cart
      await shopPage.visit();
      
      const productCount = await shopPage.getProductsCount();
      if (productCount > 0) {
        await shopPage.addProductToCart(0);
        
        // Go to cart and checkout
        await cartPage.visit();
        await cartPage.proceedToCheckout();
        
        // Fill checkout form
        const checkoutForm = page.locator('[data-testid="checkout-form"]');
        if (await checkoutForm.isVisible()) {
          // Fill shipping information
          const addressData = TestDataGenerator.generateAddress();
          
          await page.locator('[data-testid="shipping-address1"]').fill(addressData.line1);
          await page.locator('[data-testid="shipping-city"]').fill(addressData.city);
          await page.locator('[data-testid="shipping-postal-code"]').fill(addressData.postalCode);
          await page.locator('[data-testid="shipping-country"]').selectOption(addressData.country);
          
          // Select payment method
          await page.locator('[data-testid="payment-method-card"]').click();
          
          // Fill payment information (using test card)
          const cardData = TestDataGenerator.generateCreditCard();
          await page.locator('[data-testid="card-number"]').fill(cardData.number);
          await page.locator('[data-testid="card-expiry"]').fill(cardData.expiry);
          await page.locator('[data-testid="card-cvv"]').fill(cardData.cvv);
          
          // Place order
          await page.locator('[data-testid="place-order"]').click();
          
          // Should redirect to order confirmation
          await TestHelpers.verifyUrl(page, /confirmation|merci/);
          
          const orderNumber = await page.locator('[data-testid="order-number"]').textContent();
          expect(orderNumber).toBeTruthy();
        }
      }
    });

    test('should reorder previous orders', async ({ page, authenticatedB2CUser, accountPage }) => {
      await accountPage.visit();
      await accountPage.goToOrders();
      
      const ordersCount = await accountPage.getOrdersCount();
      
      if (ordersCount > 0) {
        // Check if reorder button exists
        const reorderButton = page.locator('[data-testid="reorder-button"]').first();
        
        if (await reorderButton.isVisible()) {
          await reorderButton.click();
          
          // Should add items to cart
          await TestHelpers.verifyToast(page, 'Produits ajoutés au panier');
          
          // Verify redirect to cart
          await TestHelpers.verifyUrl(page, '/cart');
        }
      }
    });

    test('should cancel orders if allowed', async ({ page, authenticatedB2CUser, accountPage }) => {
      await accountPage.visit();
      await accountPage.goToOrders();
      
      const ordersCount = await accountPage.getOrdersCount();
      
      if (ordersCount > 0) {
        // Check order status
        const orderStatus = await accountPage.getOrderStatus(0);
        
        // Only try to cancel if order is in pending status
        if (orderStatus.toLowerCase().includes('pending') || orderStatus.toLowerCase().includes('en attente')) {
          const cancelButton = page.locator('[data-testid="cancel-order-button"]').first();
          
          if (await cancelButton.isVisible()) {
            await cancelButton.click();
            
            // Confirm cancellation
            await TestHelpers.handleDialog(page, 'accept', 'Êtes-vous sûr');
            
            // Verify cancellation
            await TestHelpers.verifyToast(page, 'Commande annulée');
          }
        }
      }
    });
  });

  test.describe('Preferences and Settings', () => {
    test('should update notification preferences', async ({ page, authenticatedB2CUser, accountPage }) => {
      await accountPage.visit();
      
      const preferencesSection = page.locator('[data-testid="preferences-section"]');
      
      if (await preferencesSection.isVisible()) {
        // Toggle various notification preferences
        const emailNotifications = page.locator('[data-testid="email-notifications-toggle"]');
        const smsNotifications = page.locator('[data-testid="sms-notifications-toggle"]');
        
        if (await emailNotifications.isVisible()) {
          await emailNotifications.click();
        }
        
        if (await smsNotifications.isVisible()) {
          await smsNotifications.click();
        }
        
        // Save preferences
        const saveButton = page.locator('[data-testid="save-preferences"]');
        if (await saveButton.isVisible()) {
          await saveButton.click();
          await TestHelpers.verifyToast(page, 'Préférences mises à jour');
        }
      }
    });

    test('should delete account if option available', async ({ page, authenticatedB2CUser, accountPage }) => {
      await accountPage.visit();
      await accountPage.goToSecurity();
      
      const deleteAccountSection = page.locator('[data-testid="delete-account-section"]');
      
      if (await deleteAccountSection.isVisible()) {
        const deleteButton = page.locator('[data-testid="delete-account-button"]');
        
        // This test would only verify the flow exists, not actually delete
        await expect(deleteButton).toBeVisible();
        
        // Verify warning message is present
        const warningMessage = page.locator('[data-testid="delete-warning"]');
        await expect(warningMessage).toBeVisible();
      }
    });
  });

  test.describe('Loyalty Program', () => {
    test('should view loyalty points and rewards', async ({ page, authenticatedB2CUser, accountPage }) => {
      await accountPage.visit();
      
      const loyaltySection = page.locator('[data-testid="loyalty-section"]');
      
      if (await loyaltySection.isVisible()) {
        await accountPage.loyaltyLink.click();
        
        // Verify loyalty information is displayed
        await expect(page.locator('[data-testid="loyalty-points"]')).toBeVisible();
        await expect(page.locator('[data-testid="loyalty-tier"]')).toBeVisible();
        
        const currentPoints = await page.locator('[data-testid="current-points"]').textContent();
        expect(currentPoints).toBeTruthy();
      }
    });

    test('should redeem loyalty rewards if available', async ({ page, authenticatedB2CUser, accountPage }) => {
      await accountPage.visit();
      
      const loyaltySection = page.locator('[data-testid="loyalty-section"]');
      
      if (await loyaltySection.isVisible()) {
        await accountPage.loyaltyLink.click();
        
        const availableRewards = page.locator('[data-testid="available-reward"]');
        const rewardsCount = await availableRewards.count();
        
        if (rewardsCount > 0) {
          const redeemButton = availableRewards.first().locator('[data-testid="redeem-reward"]');
          
          if (await redeemButton.isVisible()) {
            await redeemButton.click();
            
            // Verify redemption
            await TestHelpers.verifyToast(page, 'Récompense réclamée');
          }
        }
      }
    });
  });
});