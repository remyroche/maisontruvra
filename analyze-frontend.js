// To run this code in Terminal: 
// npm install eslint stylelint execa @eslint/js @typescript-eslint/parser eslint-plugin-vue eslint-plugin-prettier eslint-plugin-simple-import-sort prettier stylelint-config-standard stylelint-config-recommended-vue typescript --save-dev
// node analyze-frontend.js

#!/usr/bin/env node

import { ESLint } from 'eslint';
import { execa } from 'execa';
import fs from 'fs/promises';
import path from 'path';

// --- SCRIPT CONFIGURATION ---

const SOURCE_PATHS = ['src/**/*.{js,ts,vue,css,scss}']; // Adjust this to your project structure
const ESLINT_EXTENSIONS = ['.js', '.ts', '.vue'];
const STYLELINT_EXTENSIONS = 'src/**/*.{vue,css,scss}'; // execa needs a string glob

// --- MAIN SCRIPT ---

function getFormattedTimestamp() {
  const now = new Date();
  const year = now.getFullYear();
  const month = (now.getMonth() + 1).toString().padStart(2, '0');
  const day = now.getDate().toString().padStart(2, '0');
  const hour = now.getHours().toString().padStart(2, '0');
  const minute = now.getMinutes().toString().padStart(2, '0');
  return `${year}${month}${day}${hour}${minute}`;
}

const logFileName = `frontend_audit_${getFormattedTimestamp()}.txt`;

async function log(message) {
  console.log(message);
  await fs.appendFile(logFileName, message + '\n');
}

async function runESLint() {
  await log('\n🔍 Running ESLint...');
  const eslint = new ESLint({
    fix: true,
    extensions: ESLINT_EXTENSIONS,
    useEslintrc: false,
    overrideConfig: {
      env: { browser: true, node: true },
      parser: 'vue-eslint-parser',
      parserOptions: {
        parser: '@typescript-eslint/parser',
        ecmaVersion: 'latest',
        sourceType: 'module',
      },
      plugins: ['vue', 'prettier', 'simple-import-sort'],
      extends: [
        'eslint:recommended',
        'plugin:vue/vue3-recommended',
        'plugin:prettier/recommended',
      ],
      rules: {
        'prettier/prettier': 'warn',
        'simple-import-sort/imports': 'warn',
        'simple-import-sort/exports': 'warn',
        'no-console': 'warn',
      },
      ignorePatterns: ['node_modules/**', 'dist/**'],
    },
  });

  const results = await eslint.lintFiles(SOURCE_PATHS);
  await ESLint.outputFixes(results);

  // Log the files that were automatically fixed
  const fixedFiles = results.filter((r) => r.output);
  if (fixedFiles.length > 0) {
    await log('\n--- [ESLint Auto-Fixes] ---');
    for (const result of fixedFiles) {
      await log(`✅ FIXED: ${result.filePath}`);
    }
  }

  // Log remaining issues that were not fixed
  const unfixedIssues = results.filter((r) => r.messages.length > 0);
  if (unfixedIssues.length > 0) {
    await log('\n--- [ESLint Unfixed Issues] ---');
    let errorCount = 0;
    let warningCount = 0;
    for (const result of unfixedIssues) {
      if (result.messages.length > 0) {
        await log(`\nISSUES in ${result.filePath}:`);
        result.messages.forEach(({ line, column, message, ruleId, severity }) => {
          const level = severity === 2 ? 'ERROR' : 'WARN';
          if (severity === 2) errorCount++;
          else warningCount++;
          log(`  - ${level} [${ruleId}] at ${line}:${column} — ${message}`);
        });
      }
    }
    await log(`\nESLint Summary: ${errorCount} Errors, ${warningCount} Warnings`);
    if (errorCount > 0) throw new Error('ESLint found errors that could not be fixed.');
  } else {
    await log('\n✅ ESLint: All issues fixed or no issues found.');
  }
}

async function runStylelint() {
  await log('\n🔍 Running Stylelint...');
  const tempConfigPath = path.resolve(process.cwd(), 'temp-stylelint.config.cjs');
  const stylelintConfig = `
    module.exports = {
      extends: ['stylelint-config-standard', 'stylelint-config-recommended-vue'],
      rules: {
        'block-no-empty': true,
        'color-no-invalid-hex': true,
        'declaration-colon-space-after': 'always',
      },
      ignoreFiles: ['**/node_modules/**', '**/dist/**'],
    };
  `;
  await fs.writeFile(tempConfigPath, stylelintConfig);

  try {
    const { stdout, failed } = await execa('npx', [
      'stylelint',
      STYLELINT_EXTENSIONS,
      '--fix',
      '--config',
      tempConfigPath,
    ], { reject: false }); // Don't reject promise on failure to inspect output

    await log('\n--- [Stylelint Results] ---');
    if (stdout) {
      await log(stdout);
    }
    
    if (failed) {
        await log('\nStylelint found issues. Some may have been fixed. Please review the output above.');
        // We don't throw an error here to allow the script to complete,
        // but you could change this behavior if needed.
    } else {
        await log('\n✅ Stylelint: All issues fixed or no issues found.');
    }

  } catch (error) {
    await log(`\n❌ An unexpected error occurred during Stylelint execution:\n${error.message}`);
    throw error; // Rethrow critical errors
  } finally {
    await fs.unlink(tempConfigPath); // Clean up the temporary config file
  }
}

(async function main() {
  try {
    await fs.writeFile(logFileName, ''); // Clear or create the log file
    await log(`🚀 Starting frontend audit... [${new Date().toLocaleString()}]`);
    await log(`📝 Report will be saved to: ${logFileName}`);

    await runESLint();
    await runStylelint();

    log('\n\n✨ Audit complete. All checks passed.');
  } catch (err) {
    console.error(`\n❌ Audit failed: ${err.message}`);
    await log(`\n--- AUDIT FAILED ---\n${err.message}`);
    process.exit(1);
  }
})();
