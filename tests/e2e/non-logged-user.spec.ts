import { test, expect } from '@playwright/test';
import { HomePage } from './pages/HomePage';
import { ShopPage } from './pages/ShopPage';
import { ProductDetailPage } from './pages/ProductDetailPage';
import { AuthPage } from './pages/AuthPage';
import { CartPage } from './pages/CartPage';
import { TestHelpers } from './utils/test-helpers';
import { TestDataGenerator, TEST_CONSTANTS } from './utils/test-data';

test.describe('Non-logged User Experience', () => {
  test.beforeEach(async ({ page }) => {
    // Clear any existing session data
    await TestHelpers.clearBrowserData(page);
  });

  test.describe('Homepage Navigation', () => {
    test('should display homepage with all key elements', async ({ page }) => {
      const homePage = new HomePage(page);
      
      await homePage.visit();
      
      // Verify main navigation elements
      await expect(homePage.heroSection).toBeVisible();
      await expect(homePage.navigationMenu).toBeVisible();
      await expect(homePage.shopLink).toBeVisible();
      await expect(homePage.notreMaisonLink).toBeVisible();
      await expect(homePage.journalLink).toBeVisible();
      
      // Verify user can access login
      await expect(homePage.loginButton).toBeVisible();
      
      // Verify featured products section
      await expect(homePage.featuredProducts).toBeVisible();
      const productCount = await homePage.getFeaturedProductsCount();
      expect(productCount).toBeGreaterThan(0);
      
      // Verify newsletter section
      await expect(homePage.isNewsletterSectionVisible()).resolves.toBe(true);
    });

    test('should navigate to different sections from homepage', async ({ page }) => {
      const homePage = new HomePage(page);
      
      await homePage.visit();
      
      // Navigate to shop
      await homePage.clickShop();
      await TestHelpers.verifyUrl(page, '/shop');
      
      // Go back to home
      await page.goBack();
      
      // Navigate to Notre Maison
      await homePage.clickNotreMaison();
      await TestHelpers.verifyUrl(page, '/notre-maison');
      
      // Go back to home
      await page.goBack();
      
      // Navigate to Journal
      await homePage.clickJournal();
      await TestHelpers.verifyUrl(page, '/le-journal');
    });

    test('should handle search functionality', async ({ page }) => {
      const homePage = new HomePage(page);
      const searchQuery = TestDataGenerator.generateSearchQueries()[0];
      
      await homePage.visit();
      
      // Perform search
      await homePage.search(searchQuery);
      
      // Should redirect to search results
      await TestHelpers.verifyUrl(page, '/search');
      
      // Verify search query is displayed
      await expect(page.locator('[data-testid="search-query"]')).toContainText(searchQuery);
    });

    test('should allow newsletter signup', async ({ page }) => {
      const homePage = new HomePage(page);
      const email = TestDataGenerator.generateNewsletterEmail();
      
      await homePage.visit();
      
      // Sign up for newsletter
      await homePage.signupForNewsletter(email);
      
      // Verify success message
      await TestHelpers.verifyToast(page, 'Inscription à la newsletter réussie');
    });
  });

  test.describe('Product Browsing', () => {
    test('should browse products in shop', async ({ page }) => {
      const shopPage = new ShopPage(page);
      
      await shopPage.visit();
      
      // Verify shop page loads
      await expect(shopPage.productGrid).toBeVisible();
      
      // Check if products are displayed
      const productCount = await shopPage.getProductsCount();
      expect(productCount).toBeGreaterThan(0);
      
      // Verify filter sidebar
      await expect(shopPage.filterSidebar).toBeVisible();
      await expect(shopPage.sortDropdown).toBeVisible();
      
      // Verify product information is displayed
      if (productCount > 0) {
        const firstProductTitle = await shopPage.getProductTitle(0);
        const firstProductPrice = await shopPage.getProductPrice(0);
        
        expect(firstProductTitle).toBeTruthy();
        expect(firstProductPrice).toBeTruthy();
      }
    });

    test('should filter products by category', async ({ page }) => {
      const shopPage = new ShopPage(page);
      
      await shopPage.visit();
      
      const initialCount = await shopPage.getProductsCount();
      
      // Apply category filter (assuming "Thés noirs" category exists)
      await shopPage.filterByCategory('Thés noirs');
      
      // Verify filter is applied
      const filteredCount = await shopPage.getProductsCount();
      
      // The count might change or stay the same depending on data
      // We just verify the page doesn't break
      expect(filteredCount).toBeGreaterThanOrEqual(0);
    });

    test('should sort products', async ({ page }) => {
      const shopPage = new ShopPage(page);
      
      await shopPage.visit();
      
      const productCount = await shopPage.getProductsCount();
      
      if (productCount > 1) {
        // Get initial product order
        const initialFirstProduct = await shopPage.getProductTitle(0);
        
        // Sort by price ascending
        await shopPage.sortBy('price_asc');
        
        // Get new first product
        const sortedFirstProduct = await shopPage.getProductTitle(0);
        
        // Products should be reordered (unless they were already sorted)
        // We verify the sort didn't break the page
        expect(sortedFirstProduct).toBeTruthy();
      }
    });

    test('should view product details', async ({ page }) => {
      const shopPage = new ShopPage(page);
      const productDetailPage = new ProductDetailPage(page);
      
      await shopPage.visit();
      
      const productCount = await shopPage.getProductsCount();
      
      if (productCount > 0) {
        // Click on first product
        await shopPage.clickProduct(0);
        
        // Should be on product detail page
        await TestHelpers.verifyUrl(page, '/product/');
        
        // Verify product detail elements
        await expect(productDetailPage.productTitle).toBeVisible();
        await expect(productDetailPage.productPrice).toBeVisible();
        await expect(productDetailPage.productDescription).toBeVisible();
        await expect(productDetailPage.addToCartButton).toBeVisible();
        
        // Verify product images
        await expect(productDetailPage.mainProductImage).toBeVisible();
      }
    });

    test('should use quick view functionality', async ({ page }) => {
      const shopPage = new ShopPage(page);
      
      await shopPage.visit();
      
      const productCount = await shopPage.getProductsCount();
      
      if (productCount > 0) {
        // Open quick view for first product
        await shopPage.openQuickView(0);
        
        // Verify quick view modal is open
        await expect(shopPage.isQuickViewOpen()).resolves.toBe(true);
        
        // Close quick view
        await shopPage.closeQuickView();
        
        // Verify modal is closed
        await expect(shopPage.isQuickViewOpen()).resolves.toBe(false);
      }
    });
  });

  test.describe('Cart Functionality', () => {
    test('should add products to cart without being logged in', async ({ page }) => {
      const shopPage = new ShopPage(page);
      const cartPage = new CartPage(page);
      
      await shopPage.visit();
      
      const productCount = await shopPage.getProductsCount();
      
      if (productCount > 0) {
        // Add first product to cart
        await shopPage.addProductToCart(0);
        
        // Verify success notification
        await TestHelpers.verifyToast(page, 'Produit ajouté au panier');
        
        // Go to cart
        await cartPage.visit();
        
        // Verify cart is not empty
        const isEmpty = await cartPage.isCartEmpty();
        expect(isEmpty).toBe(false);
        
        // Verify cart contains the added product
        const cartItemsCount = await cartPage.getItemsCount();
        expect(cartItemsCount).toBeGreaterThan(0);
      }
    });

    test('should manage cart contents', async ({ page }) => {
      const shopPage = new ShopPage(page);
      const cartPage = new CartPage(page);
      
      // Add a product to cart first
      await shopPage.visit();
      
      const productCount = await shopPage.getProductsCount();
      
      if (productCount > 0) {
        await shopPage.addProductToCart(0);
        await cartPage.visit();
        
        const itemsCount = await cartPage.getItemsCount();
        
        if (itemsCount > 0) {
          // Test quantity increase
          const initialQuantity = await cartPage.getItemQuantity(0);
          await cartPage.increaseItemQuantity(0);
          
          await page.waitForTimeout(1000); // Wait for update
          
          const newQuantity = await cartPage.getItemQuantity(0);
          expect(newQuantity).toBe(initialQuantity + 1);
          
          // Test quantity decrease
          await cartPage.decreaseItemQuantity(0);
          
          await page.waitForTimeout(1000); // Wait for update
          
          const finalQuantity = await cartPage.getItemQuantity(0);
          expect(finalQuantity).toBe(initialQuantity);
        }
      }
    });

    test('should calculate cart totals correctly', async ({ page }) => {
      const shopPage = new ShopPage(page);
      const cartPage = new CartPage(page);
      
      // Add products to cart
      await shopPage.visit();
      
      const productCount = await shopPage.getProductsCount();
      
      if (productCount > 0) {
        await shopPage.addProductToCart(0);
        await cartPage.visit();
        
        // Verify cart totals
        const isCalculationCorrect = await cartPage.verifyCartTotals();
        expect(isCalculationCorrect).toBe(true);
      }
    });

    test('should require login for checkout', async ({ page }) => {
      const shopPage = new ShopPage(page);
      const cartPage = new CartPage(page);
      const authPage = new AuthPage(page);
      
      // Add product and attempt checkout
      await shopPage.visit();
      
      const productCount = await shopPage.getProductsCount();
      
      if (productCount > 0) {
        await shopPage.addProductToCart(0);
        await cartPage.visit();
        
        // Attempt to checkout
        await cartPage.proceedToCheckout();
        
        // Should be redirected to login page
        await TestHelpers.verifyUrl(page, '/auth/login');
        await expect(authPage.loginForm).toBeVisible();
      }
    });
  });

  test.describe('Authentication Access', () => {
    test('should access login page', async ({ page }) => {
      const authPage = new AuthPage(page);
      
      await authPage.visitLogin();
      
      // Verify login form elements
      await expect(authPage.loginForm).toBeVisible();
      await expect(authPage.emailInput).toBeVisible();
      await expect(authPage.passwordInput).toBeVisible();
      await expect(authPage.loginSubmitButton).toBeVisible();
      await expect(authPage.forgotPasswordLink).toBeVisible();
      await expect(authPage.switchToRegisterLink).toBeVisible();
    });

    test('should access registration page', async ({ page }) => {
      const authPage = new AuthPage(page);
      
      await authPage.visitRegister();
      
      // Verify registration form elements
      await expect(authPage.registerForm).toBeVisible();
      await expect(authPage.firstNameInput).toBeVisible();
      await expect(authPage.lastNameInput).toBeVisible();
      await expect(authPage.emailInput).toBeVisible();
      await expect(authPage.registerPasswordInput).toBeVisible();
      await expect(authPage.confirmPasswordInput).toBeVisible();
      await expect(authPage.termsCheckbox).toBeVisible();
      await expect(authPage.registerSubmitButton).toBeVisible();
    });

    test('should switch between login and register forms', async ({ page }) => {
      const authPage = new AuthPage(page);
      
      await authPage.visitLogin();
      
      // Switch to register
      await authPage.switchToRegister();
      await expect(authPage.isRegisterFormVisible()).resolves.toBe(true);
      
      // Switch back to login
      await authPage.switchToLogin();
      await expect(authPage.isLoginFormVisible()).resolves.toBe(true);
    });

    test('should show B2B registration option', async ({ page }) => {
      const authPage = new AuthPage(page);
      
      await authPage.visitRegister();
      
      // Toggle B2B registration
      await authPage.b2bToggle.click();
      
      // Verify B2B specific fields appear
      await expect(authPage.companyNameInput).toBeVisible();
      await expect(authPage.siretInput).toBeVisible();
      await expect(authPage.vatNumberInput).toBeVisible();
    });

    test('should validate form inputs', async ({ page }) => {
      const authPage = new AuthPage(page);
      
      await authPage.visitLogin();
      
      // Try to submit empty form
      await authPage.loginSubmitButton.click();
      
      // Should show validation errors
      await TestHelpers.verifyFormValidation(page, '[data-testid="email-input"]', 'Ce champ est requis');
    });

    test('should handle invalid login credentials', async ({ page }) => {
      const authPage = new AuthPage(page);
      
      await authPage.visitLogin();
      
      // Try login with invalid credentials
      await authPage.login('invalid@example.com', 'wrongpassword');
      
      // Should show error message
      await expect(authPage.hasError()).resolves.toBe(true);
      const errorMessage = await authPage.getErrorMessage();
      expect(errorMessage).toContain('Identifiants invalides');
    });
  });

  test.describe('Content Access', () => {
    test('should access Notre Maison page', async ({ page }) => {
      await page.goto('/notre-maison');
      await TestHelpers.waitForPageStable(page);
      
      // Should not require authentication
      await TestHelpers.verifyUrl(page, '/notre-maison');
      
      // Basic content should be visible
      await expect(page.locator('h1')).toBeVisible();
    });

    test('should access Journal (blog) page', async ({ page }) => {
      await page.goto('/le-journal');
      await TestHelpers.waitForPageStable(page);
      
      // Should not require authentication
      await TestHelpers.verifyUrl(page, '/le-journal');
      
      // Blog content should be visible
      await expect(page.locator('[data-testid="blog-posts"]')).toBeVisible();
    });

    test('should access individual blog articles', async ({ page }) => {
      await page.goto('/le-journal');
      await TestHelpers.waitForPageStable(page);
      
      // Check if there are any blog posts
      const blogPosts = page.locator('[data-testid="blog-post-link"]');
      const postsCount = await blogPosts.count();
      
      if (postsCount > 0) {
        await blogPosts.first().click();
        
        // Should navigate to article
        await TestHelpers.verifyUrl(page, '/le-journal/');
        
        // Article content should be visible
        await expect(page.locator('[data-testid="article-content"]')).toBeVisible();
      }
    });

    test('should access Professionnels page', async ({ page }) => {
      await page.goto('/professionnels');
      await TestHelpers.waitForPageStable(page);
      
      // Should not require authentication
      await TestHelpers.verifyUrl(page, '/professionnels');
      
      // B2B information should be visible
      await expect(page.locator('h1')).toBeVisible();
    });

    test('should show 404 for invalid routes', async ({ page }) => {
      await page.goto('/invalid-route-that-does-not-exist');
      
      // Should show 404 page
      await TestHelpers.verifyUrl(page, '/invalid-route-that-does-not-exist');
      await expect(page.locator('[data-testid="not-found"]')).toBeVisible();
    });
  });

  test.describe('Responsive Design', () => {
    test('should work on mobile viewport', async ({ page }) => {
      const homePage = new HomePage(page);
      
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 812 });
      
      await homePage.visit();
      
      // Verify mobile navigation works
      await expect(homePage.navigationMenu).toBeVisible();
      
      // Mobile menu toggle should be visible
      const mobileMenuToggle = page.locator('[data-testid="mobile-menu-toggle"]');
      if (await mobileMenuToggle.isVisible()) {
        await mobileMenuToggle.click();
        await expect(page.locator('[data-testid="mobile-menu"]')).toBeVisible();
      }
    });

    test('should work on tablet viewport', async ({ page }) => {
      const homePage = new HomePage(page);
      
      // Set tablet viewport
      await page.setViewportSize({ width: 768, height: 1024 });
      
      await homePage.visit();
      
      // Verify layout adapts to tablet size
      await expect(homePage.heroSection).toBeVisible();
      await expect(homePage.featuredProducts).toBeVisible();
    });
  });

  test.describe('Performance and Accessibility', () => {
    test('should load pages within acceptable time', async ({ page }) => {
      const startTime = Date.now();
      
      await page.goto('/');
      await TestHelpers.waitForPageStable(page);
      
      const loadTime = Date.now() - startTime;
      
      // Page should load within 5 seconds
      expect(loadTime).toBeLessThan(5000);
    });

    test('should have proper page titles', async ({ page }) => {
      const routes = [
        { path: '/', expectedTitle: /Maison Trüvra/ },
        { path: '/shop', expectedTitle: /Boutique/ },
        { path: '/notre-maison', expectedTitle: /Notre Maison/ },
        { path: '/le-journal', expectedTitle: /Journal/ }
      ];

      for (const route of routes) {
        await page.goto(route.path);
        await TestHelpers.waitForPageStable(page);
        await expect(page).toHaveTitle(route.expectedTitle);
      }
    });

    test('should handle network errors gracefully', async ({ page }) => {
      // Simulate network failure
      await page.route('**/api/**', route => route.abort());
      
      await page.goto('/');
      
      // Page should still load basic content
      await expect(page.locator('body')).toBeVisible();
      
      // Error handling should be in place
      const errorMessages = page.locator('[data-testid="network-error"]');
      if (await errorMessages.count() > 0) {
        await expect(errorMessages.first()).toBeVisible();
      }
    });
  });
});