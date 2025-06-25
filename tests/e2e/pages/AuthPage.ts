import { Page, Locator } from '@playwright/test';
import { BasePage } from './BasePage';

export class AuthPage extends BasePage {
  constructor(page: Page) {
    super(page);
  }

  // Login form elements
  get loginForm(): Locator {
    return this.page.locator('[data-testid="login-form"]');
  }

  get emailInput(): Locator {
    return this.page.locator('[data-testid="email-input"]');
  }

  get passwordInput(): Locator {
    return this.page.locator('[data-testid="password-input"]');
  }

  get loginSubmitButton(): Locator {
    return this.page.locator('[data-testid="login-submit"]');
  }

  get forgotPasswordLink(): Locator {
    return this.page.locator('[data-testid="forgot-password-link"]');
  }

  // Registration form elements
  get registerForm(): Locator {
    return this.page.locator('[data-testid="register-form"]');
  }

  get firstNameInput(): Locator {
    return this.page.locator('[data-testid="first-name-input"]');
  }

  get lastNameInput(): Locator {
    return this.page.locator('[data-testid="last-name-input"]');
  }

  get phoneInput(): Locator {
    return this.page.locator('[data-testid="phone-input"]');
  }

  get registerPasswordInput(): Locator {
    return this.page.locator('[data-testid="register-password-input"]');
  }

  get confirmPasswordInput(): Locator {
    return this.page.locator('[data-testid="confirm-password-input"]');
  }

  get registerSubmitButton(): Locator {
    return this.page.locator('[data-testid="register-submit"]');
  }

  get termsCheckbox(): Locator {
    return this.page.locator('[data-testid="terms-checkbox"]');
  }

  // B2B registration elements
  get b2bToggle(): Locator {
    return this.page.locator('[data-testid="b2b-toggle"]');
  }

  get companyNameInput(): Locator {
    return this.page.locator('[data-testid="company-name-input"]');
  }

  get siretInput(): Locator {
    return this.page.locator('[data-testid="siret-input"]');
  }

  get vatNumberInput(): Locator {
    return this.page.locator('[data-testid="vat-number-input"]');
  }

  // Two-factor authentication elements
  get mfaForm(): Locator {
    return this.page.locator('[data-testid="mfa-form"]');
  }

  get mfaCodeInput(): Locator {
    return this.page.locator('[data-testid="mfa-code-input"]');
  }

  get mfaSubmitButton(): Locator {
    return this.page.locator('[data-testid="mfa-submit"]');
  }

  // Toggle between login and register
  get switchToRegisterLink(): Locator {
    return this.page.locator('[data-testid="switch-to-register"]');
  }

  get switchToLoginLink(): Locator {
    return this.page.locator('[data-testid="switch-to-login"]');
  }

  // Error and success messages
  get errorMessage(): Locator {
    return this.page.locator('[data-testid="error-message"]');
  }

  get successMessage(): Locator {
    return this.page.locator('[data-testid="success-message"]');
  }

  // Actions
  async visitLogin(): Promise<void> {
    await this.navigateTo('/auth/login');
    await this.waitForPageLoad();
  }

  async visitRegister(): Promise<void> {
    await this.navigateTo('/auth/register');
    await this.waitForPageLoad();
  }

  async login(email: string, password: string): Promise<void> {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.loginSubmitButton.click();
  }

  async loginWithMFA(email: string, password: string, mfaCode: string): Promise<void> {
    await this.login(email, password);
    await this.mfaCodeInput.waitFor({ state: 'visible' });
    await this.mfaCodeInput.fill(mfaCode);
    await this.mfaSubmitButton.click();
  }

  async registerB2C(userData: {
    firstName: string;
    lastName: string;
    email: string;
    phone?: string;
    password: string;
  }): Promise<void> {
    await this.firstNameInput.fill(userData.firstName);
    await this.lastNameInput.fill(userData.lastName);
    await this.emailInput.fill(userData.email);
    if (userData.phone) {
      await this.phoneInput.fill(userData.phone);
    }
    await this.registerPasswordInput.fill(userData.password);
    await this.confirmPasswordInput.fill(userData.password);
    await this.termsCheckbox.check();
    await this.registerSubmitButton.click();
  }

  async registerB2B(userData: {
    firstName: string;
    lastName: string;
    email: string;
    phone?: string;
    password: string;
    companyName: string;
    siret: string;
    vatNumber?: string;
  }): Promise<void> {
    await this.b2bToggle.click();
    await this.firstNameInput.fill(userData.firstName);
    await this.lastNameInput.fill(userData.lastName);
    await this.emailInput.fill(userData.email);
    if (userData.phone) {
      await this.phoneInput.fill(userData.phone);
    }
    await this.companyNameInput.fill(userData.companyName);
    await this.siretInput.fill(userData.siret);
    if (userData.vatNumber) {
      await this.vatNumberInput.fill(userData.vatNumber);
    }
    await this.registerPasswordInput.fill(userData.password);
    await this.confirmPasswordInput.fill(userData.password);
    await this.termsCheckbox.check();
    await this.registerSubmitButton.click();
  }

  async switchToRegister(): Promise<void> {
    await this.switchToRegisterLink.click();
  }

  async switchToLogin(): Promise<void> {
    await this.switchToLoginLink.click();
  }

  async clickForgotPassword(): Promise<void> {
    await this.forgotPasswordLink.click();
  }

  // Assertion helpers
  async isLoginFormVisible(): Promise<boolean> {
    return await this.loginForm.isVisible();
  }

  async isRegisterFormVisible(): Promise<boolean> {
    return await this.registerForm.isVisible();
  }

  async isMFAFormVisible(): Promise<boolean> {
    return await this.mfaForm.isVisible();
  }

  async getErrorMessage(): Promise<string> {
    return await this.errorMessage.textContent() || '';
  }

  async getSuccessMessage(): Promise<string> {
    return await this.successMessage.textContent() || '';
  }

  async hasError(): Promise<boolean> {
    return await this.errorMessage.isVisible();
  }

  async hasSuccess(): Promise<boolean> {
    return await this.successMessage.isVisible();
  }
}