import { test as base, expect } from '@playwright/test';
import { AuthPage } from '../pages/AuthPage';
import { HomePage } from '../pages/HomePage';

export interface AuthenticatedUser {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  role: 'b2c' | 'b2b' | 'admin';
  isAuthenticated: boolean;
}

export interface AuthFixtures {
  authenticatedB2CUser: AuthenticatedUser;
  authenticatedB2BUser: AuthenticatedUser;
  authenticatedAdminUser: AuthenticatedUser;
  authPage: AuthPage;
  homePage: HomePage;
}

// Test user data
export const testUsers = {
  b2c: {
    email: 'test.b2c@example.com',
    password: 'TestPass123!',
    firstName: 'Jean',
    lastName: 'Dupont',
    phone: '+33123456789'
  },
  b2b: {
    email: 'test.b2b@example.com',
    password: 'TestPass123!',
    firstName: 'Marie',
    lastName: 'Martin',
    phone: '+33987654321',
    companyName: 'Test Company SARL',
    siret: '12345678901234',
    vatNumber: 'FR12345678901'
  },
  admin: {
    email: 'admin@example.com',
    password: 'AdminPass123!',
    firstName: 'Admin',
    lastName: 'User'
  }
};

export const test = base.extend<AuthFixtures>({
  authPage: async ({ page }, use) => {
    const authPage = new AuthPage(page);
    await use(authPage);
  },

  homePage: async ({ page }, use) => {
    const homePage = new HomePage(page);
    await use(homePage);
  },

  authenticatedB2CUser: async ({ page, authPage }, use) => {
    // Register and login B2C user
    await authPage.visitRegister();
    
    // Check if user already exists, if not register
    try {
      await authPage.registerB2C({
        firstName: testUsers.b2c.firstName,
        lastName: testUsers.b2c.lastName,
        email: testUsers.b2c.email,
        phone: testUsers.b2c.phone,
        password: testUsers.b2c.password
      });
    } catch (error) {
      // User might already exist, try to login
      await authPage.visitLogin();
      await authPage.login(testUsers.b2c.email, testUsers.b2c.password);
    }

    // Verify login success
    await expect(page).toHaveURL(/.*account.*|.*dashboard.*/);

    const user: AuthenticatedUser = {
      email: testUsers.b2c.email,
      password: testUsers.b2c.password,
      firstName: testUsers.b2c.firstName,
      lastName: testUsers.b2c.lastName,
      role: 'b2c',
      isAuthenticated: true
    };

    await use(user);
  },

  authenticatedB2BUser: async ({ page, authPage }, use) => {
    // Register and login B2B user
    await authPage.visitRegister();
    
    try {
      await authPage.registerB2B({
        firstName: testUsers.b2b.firstName,
        lastName: testUsers.b2b.lastName,
        email: testUsers.b2b.email,
        phone: testUsers.b2b.phone,
        password: testUsers.b2b.password,
        companyName: testUsers.b2b.companyName,
        siret: testUsers.b2b.siret,
        vatNumber: testUsers.b2b.vatNumber
      });
    } catch (error) {
      // User might already exist, try to login
      await authPage.visitLogin();
      await authPage.login(testUsers.b2b.email, testUsers.b2b.password);
    }

    // B2B accounts might need approval, so check if we're on pending page or dashboard
    await page.waitForURL(/.*b2b.*|.*account.*|.*pending.*/);

    const user: AuthenticatedUser = {
      email: testUsers.b2b.email,
      password: testUsers.b2b.password,
      firstName: testUsers.b2b.firstName,
      lastName: testUsers.b2b.lastName,
      role: 'b2b',
      isAuthenticated: true
    };

    await use(user);
  },

  authenticatedAdminUser: async ({ page, authPage }, use) => {
    // Login admin user (assumes admin is pre-created)
    await authPage.visitLogin();
    await authPage.login(testUsers.admin.email, testUsers.admin.password);

    // Handle MFA if required
    const isMFARequired = await authPage.isMFAFormVisible();
    if (isMFARequired) {
      // For testing purposes, we might need to handle MFA
      // This would require either mocking or using a test TOTP code
      console.warn('MFA is required for admin login - this might need special handling in tests');
    }

    // Verify admin access
    await expect(page).toHaveURL(/.*admin.*/);

    const user: AuthenticatedUser = {
      email: testUsers.admin.email,
      password: testUsers.admin.password,
      firstName: testUsers.admin.firstName,
      lastName: testUsers.admin.lastName,
      role: 'admin',
      isAuthenticated: true
    };

    await use(user);
  }
});

export { expect } from '@playwright/test';