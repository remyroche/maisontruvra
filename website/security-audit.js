#!/usr/bin/env node

/**
 * Frontend Security Audit Script
 * This script performs a comprehensive security audit of the frontend application
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class SecurityAuditor {
  constructor() {
    this.issues = [];
    this.warnings = [];
    this.recommendations = [];
    this.srcDir = path.join(__dirname, 'src');
  }

  /**
   * Run the complete security audit
   */
  async runAudit() {
    console.log('🔍 Starting Frontend Security Audit...\n');

    await this.checkDependencies();
    await this.checkVulnerablePatterns();
    await this.checkInputValidation();
    await this.checkXSSProtection();
    await this.checkCSRFProtection();
    await this.checkAuthentication();
    await this.checkStorageSecurity();
    await this.checkHTTPSConfiguration();
    await this.checkSecurityHeaders();
    await this.checkFileUploads();
    await this.checkErrorHandling();

    this.generateReport();
  }

  /**
   * Check for vulnerable dependencies
   */
  async checkDependencies() {
    console.log('📦 Checking dependencies...');
    
    try {
      const packageJson = JSON.parse(fs.readFileSync(path.join(__dirname, 'package.json'), 'utf8'));
      const dependencies = { ...packageJson.dependencies, ...packageJson.devDependencies };
      
      // Check for known vulnerable packages
      const vulnerablePackages = [
        'axios@<1.7.0',
        'lodash@<4.17.21',
        'moment@<2.29.4',
        'jquery@<3.6.0'
      ];

      for (const [name, version] of Object.entries(dependencies)) {
        if (vulnerablePackages.some(vuln => vuln.startsWith(name + '@'))) {
          this.issues.push({
            type: 'vulnerable_dependency',
            severity: 'high',
            message: `Vulnerable dependency: ${name}@${version}`,
            file: 'package.json'
          });
        }
      }

      // Check for missing security packages
      if (!dependencies['dompurify']) {
        this.warnings.push({
          type: 'missing_security_package',
          severity: 'medium',
          message: 'DOMPurify not found - XSS protection recommended',
          file: 'package.json'
        });
      }

    } catch (error) {
      this.issues.push({
        type: 'audit_error',
        severity: 'medium',
        message: `Failed to check dependencies: ${error.message}`,
        file: 'package.json'
      });
    }
  }

  /**
   * Check for vulnerable code patterns
   */
  async checkVulnerablePatterns() {
    console.log('🔍 Checking for vulnerable patterns...');
    
    const patterns = [
      {
        pattern: /eval\s*\(/g,
        type: 'eval_usage',
        severity: 'high',
        message: 'eval() usage detected - potential code injection risk'
      },
      {
        pattern: /innerHTML\s*=/g,
        type: 'innerhtml_usage',
        severity: 'high',
        message: 'innerHTML usage detected - potential XSS risk'
      },
      {
        pattern: /document\.write/g,
        type: 'document_write',
        severity: 'high',
        message: 'document.write usage detected - potential XSS risk'
      },
      {
        pattern: /setTimeout\s*\(\s*['"][^'"]*['"]/g,
        type: 'string_settimeout',
        severity: 'medium',
        message: 'setTimeout with string detected - use function instead'
      },
      {
        pattern: /new Function\s*\(/g,
        type: 'function_constructor',
        severity: 'high',
        message: 'Function constructor usage detected - potential code injection risk'
      }
    ];

    await this.scanFiles(patterns);
  }

  /**
   * Check input validation
   */
  async checkInputValidation() {
    console.log('✅ Checking input validation...');
    
    const patterns = [
      {
        pattern: /v-html\s*=\s*[^s].*[^e]/g,
        type: 'unsafe_html',
        severity: 'high',
        message: 'v-html usage without sanitization - potential XSS risk'
      },
      {
        pattern: /\.value\s*=\s*[^;]*input/g,
        type: 'unsafe_value_assignment',
        severity: 'medium',
        message: 'Direct value assignment without validation'
      }
    ];

    await this.scanFiles(patterns);
  }

  /**
   * Check XSS protection
   */
  async checkXSSProtection() {
    console.log('🛡️ Checking XSS protection...');
    
    // Check if DOMPurify is being used
    const dompurifyUsage = await this.grepFiles(/DOMPurify|dompurify/g);
    if (dompurifyUsage.length === 0) {
      this.warnings.push({
        type: 'missing_xss_protection',
        severity: 'medium',
        message: 'No DOMPurify usage found - XSS protection recommended'
      });
    }

    // Check for unsanitized HTML output (more sophisticated check)
    const vHtmlFiles = await this.grepFiles(/v-html/g);
    for (const file of vHtmlFiles) {
      const content = await this.readFile(file);
      if (content) {
        const vHtmlMatches = content.match(/v-html/g);
        const sanitizeMatches = content.match(/DOMPurify|sanitize|sanitized/gi);
        
        if (vHtmlMatches && vHtmlMatches.length > 0) {
          // Check if the file has proper sanitization
          const hasProperSanitization = sanitizeMatches && sanitizeMatches.length > 0;
          
          // Also check if v-html is using sanitized variables
          const sanitizedVariableUsage = /v-html\s*=\s*"[^"]*[Ss]anitiz/i.test(content);
          
          if (!hasProperSanitization && !sanitizedVariableUsage) {
            this.issues.push({
              type: 'unsanitized_html',
              severity: 'high',
              message: 'Unsanitized v-html usage detected',
              file: file
            });
          }
        }
      }
    }
  }

  /**
   * Check CSRF protection
   */
  async checkCSRFProtection() {
    console.log('🔒 Checking CSRF protection...');
    
    const csrfTokenUsage = await this.grepFiles(/X-CSRF-TOKEN|csrf.*token/gi);
    if (csrfTokenUsage.length === 0) {
      this.warnings.push({
        type: 'missing_csrf_protection',
        severity: 'medium',
        message: 'No CSRF token usage found - CSRF protection recommended'
      });
    }
  }

  /**
   * Check authentication mechanisms
   */
  async checkAuthentication() {
    console.log('🔐 Checking authentication...');
    
    // Check for secure password handling
    const passwordPatterns = await this.grepFiles(/password.*type.*text/gi);
    if (passwordPatterns.length > 0) {
      this.issues.push({
        type: 'insecure_password_field',
        severity: 'high',
        message: 'Password field with type="text" detected - use type="password"'
      });
    }

    // Check for client-side password validation
    const passwordValidation = await this.grepFiles(/password.*validation|validatePassword/gi);
    if (passwordValidation.length === 0) {
      this.warnings.push({
        type: 'missing_password_validation',
        severity: 'medium',
        message: 'No client-side password validation found'
      });
    }
  }

  /**
   * Check storage security
   */
  async checkStorageSecurity() {
    console.log('💾 Checking storage security...');
    
    const localStorageUsage = await this.grepFiles(/localStorage\.(get|set|remove)Item/g);
    if (localStorageUsage.length > 0) {
      this.warnings.push({
        type: 'localstorage_usage',
        severity: 'medium',
        message: 'localStorage usage detected - consider encryption for sensitive data',
        files: localStorageUsage
      });
    }

    const sessionStorageUsage = await this.grepFiles(/sessionStorage\.(get|set|remove)Item/g);
    if (sessionStorageUsage.length > 0) {
      this.warnings.push({
        type: 'sessionstorage_usage',
        severity: 'low',
        message: 'sessionStorage usage detected - ensure sensitive data is not stored'
      });
    }
  }

  /**
   * Check HTTPS configuration
   */
  async checkHTTPSConfiguration() {
    console.log('🔐 Checking HTTPS configuration...');
    
    const viteConfig = await this.readFile('vite.config.js');
    if (viteConfig && !viteConfig.includes('https: true')) {
      this.warnings.push({
        type: 'missing_https_config',
        severity: 'medium',
        message: 'HTTPS not configured in Vite - required for production'
      });
    }
  }

  /**
   * Check security headers
   */
  async checkSecurityHeaders() {
    console.log('🛡️ Checking security headers...');
    
    const indexHtml = await this.readFile('index.html');
    if (indexHtml) {
      const requiredHeaders = [
        'X-Content-Type-Options',
        'X-Frame-Options',
        'Content-Security-Policy'
      ];

      for (const header of requiredHeaders) {
        if (!indexHtml.includes(header)) {
          this.warnings.push({
            type: 'missing_security_header',
            severity: 'medium',
            message: `Missing security header: ${header}`
          });
        }
      }
    }
  }

  /**
   * Check file upload security
   */
  async checkFileUploads() {
    console.log('📁 Checking file upload security...');
    
    const fileInputs = await this.grepFiles(/type.*file|input.*file/gi);
    if (fileInputs.length > 0) {
      const validationChecks = await this.grepFiles(/accept=|file.*type|file.*size/gi);
      if (validationChecks.length === 0) {
        this.warnings.push({
          type: 'missing_file_validation',
          severity: 'medium',
          message: 'File uploads detected without validation - add file type and size checks'
        });
      }
    }
  }

  /**
   * Check error handling
   */
  async checkErrorHandling() {
    console.log('⚠️ Checking error handling...');
    
    const errorHandling = await this.grepFiles(/try\s*\{|catch\s*\(/g);
    if (errorHandling.length === 0) {
      this.warnings.push({
        type: 'missing_error_handling',
        severity: 'low',
        message: 'No try-catch blocks found - error handling recommended'
      });
    }

    // Check for console.error usage
    const consoleErrors = await this.grepFiles(/console\.error/g);
    if (consoleErrors.length === 0) {
      this.warnings.push({
        type: 'missing_error_logging',
        severity: 'low',
        message: 'No console.error usage found - error logging recommended'
      });
    }
  }

  /**
   * Scan files for patterns
   */
  async scanFiles(patterns) {
    const files = await this.getVueFiles();
    
    for (const file of files) {
      const content = await this.readFile(file);
      if (!content) continue;

      for (const { pattern, type, severity, message } of patterns) {
        const matches = content.match(pattern);
        if (matches) {
          this.issues.push({
            type,
            severity,
            message,
            file,
            matches: matches.length
          });
        }
      }
    }
  }

  /**
   * Get all Vue files
   */
  async getVueFiles() {
    const files = [];
    const scanDir = (dir) => {
      const items = fs.readdirSync(dir);
      for (const item of items) {
        const fullPath = path.join(dir, item);
        const stat = fs.statSync(fullPath);
        if (stat.isDirectory()) {
          scanDir(fullPath);
        } else if (item.endsWith('.vue') || item.endsWith('.js') || item.endsWith('.ts')) {
          files.push(fullPath.replace(__dirname + '/', ''));
        }
      }
    };
    scanDir(this.srcDir);
    return files;
  }

  /**
   * Grep files for pattern
   */
  async grepFiles(pattern) {
    const files = await this.getVueFiles();
    const results = [];
    
    for (const file of files) {
      const content = await this.readFile(file);
      if (content && pattern.test(content)) {
        results.push(file);
      }
    }
    
    return results;
  }

  /**
   * Read file content
   */
  async readFile(filePath) {
    try {
      const fullPath = path.join(__dirname, filePath);
      return fs.readFileSync(fullPath, 'utf8');
    } catch (error) {
      return null;
    }
  }

  /**
   * Generate security report
   */
  generateReport() {
    console.log('\n📊 Security Audit Report');
    console.log('=' .repeat(50));
    
    console.log(`\n🚨 Issues Found: ${this.issues.length}`);
    this.issues.forEach((issue, index) => {
      console.log(`\n${index + 1}. [${issue.severity.toUpperCase()}] ${issue.message}`);
      console.log(`   File: ${issue.file}`);
      if (issue.matches) {
        console.log(`   Matches: ${issue.matches}`);
      }
    });

    console.log(`\n⚠️ Warnings: ${this.warnings.length}`);
    this.warnings.forEach((warning, index) => {
      console.log(`\n${index + 1}. [${warning.severity.toUpperCase()}] ${warning.message}`);
      if (warning.file) {
        console.log(`   File: ${warning.file}`);
      }
    });

    console.log(`\n💡 Recommendations: ${this.recommendations.length}`);
    this.recommendations.forEach((rec, index) => {
      console.log(`\n${index + 1}. ${rec}`);
    });

    // Generate recommendations
    this.generateRecommendations();

    console.log('\n' + '='.repeat(50));
    console.log('✅ Security audit completed!');
    
    if (this.issues.length > 0) {
      console.log(`\n🚨 ${this.issues.length} security issues need immediate attention!`);
      process.exit(1);
    } else {
      console.log('\n🎉 No critical security issues found!');
    }
  }

  /**
   * Generate security recommendations
   */
  generateRecommendations() {
    this.recommendations = [
      'Implement Content Security Policy (CSP) headers',
      'Use HTTPS in production',
      'Sanitize all user inputs with DOMPurify',
      'Implement rate limiting for API calls',
      'Add input validation on both client and server side',
      'Use secure storage for sensitive data',
      'Implement proper error handling and logging',
      'Regular security audits and dependency updates',
      'Use security headers (X-Frame-Options, X-Content-Type-Options, etc.)',
      'Implement CSRF protection for state-changing operations'
    ];
  }
}

// Run the audit
const auditor = new SecurityAuditor();
auditor.runAudit().catch(console.error);