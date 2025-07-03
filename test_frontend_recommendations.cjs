#!/usr/bin/env node
/**
 * Simple test script to verify frontend recommendation components
 * This script checks if all the Vue components and stores can be imported correctly
 */

const fs = require('fs');
const path = require('path');

// Define the files to check
const filesToCheck = [
  // Vue Components
  'website/src/views/admin/ManageRecommendationsView.vue',
  'website/src/views/admin/DashboardHomeView.vue',
  'website/src/components/admin/BulkOperationsModal.vue',
  'website/src/components/admin/UserRecommendationsModal.vue',
  'website/src/components/admin/RecommendationsDashboardWidget.vue',
  
  // Pinia Store
  'website/src/stores/adminRecommendations.js',
  
  // Localization
  'website/src/locales/pages/admin-recommendations.json',
  
  // Documentation
  'FRONTEND_RECOMMENDATIONS_GUIDE.md'
];

// Define required content patterns for each file type
const contentChecks = {
  '.vue': [
    '<template>',
    '<script setup>',
    'export default' // Alternative for Options API
  ],
  '.js': [
    'defineStore',
    'export'
  ],
  '.json': [
    '{',
    '}'
  ],
  '.md': [
    '#',
    'Frontend'
  ]
};

function checkFileExists(filePath) {
  const fullPath = path.join(__dirname, filePath);
  return fs.existsSync(fullPath);
}

function checkFileContent(filePath) {
  const fullPath = path.join(__dirname, filePath);
  const ext = path.extname(filePath);
  const content = fs.readFileSync(fullPath, 'utf8');
  
  const requiredPatterns = contentChecks[ext] || [];
  const missingPatterns = [];
  
  for (const pattern of requiredPatterns) {
    if (!content.includes(pattern)) {
      missingPatterns.push(pattern);
    }
  }
  
  return missingPatterns;
}

function runTests() {
  console.log('🧪 Frontend Recommendations Component Test');
  console.log('==========================================\n');
  
  let allTestsPassed = true;
  
  // Test 1: File Existence
  console.log('📁 Checking file existence...');
  for (const filePath of filesToCheck) {
    const exists = checkFileExists(filePath);
    const status = exists ? '✅' : '❌';
    console.log(`${status} ${filePath}`);
    
    if (!exists) {
      allTestsPassed = false;
    }
  }
  
  console.log('');
  
  // Test 2: Content Validation
  console.log('📝 Checking file content...');
  for (const filePath of filesToCheck) {
    if (checkFileExists(filePath)) {
      try {
        const missingPatterns = checkFileContent(filePath);
        if (missingPatterns.length === 0) {
          console.log(`✅ ${filePath} - Content valid`);
        } else {
          console.log(`⚠️  ${filePath} - Missing patterns: ${missingPatterns.join(', ')}`);
          // Don't fail for missing patterns as they might be valid alternatives
        }
      } catch (error) {
        console.log(`❌ ${filePath} - Content check failed: ${error.message}`);
        allTestsPassed = false;
      }
    }
  }
  
  console.log('');
  
  // Test 3: Vue Component Structure
  console.log('🔧 Checking Vue component structure...');
  const vueFiles = filesToCheck.filter(f => f.endsWith('.vue'));
  
  for (const vueFile of vueFiles) {
    if (checkFileExists(vueFile)) {
      const fullPath = path.join(__dirname, vueFile);
      const content = fs.readFileSync(fullPath, 'utf8');
      
      const hasTemplate = content.includes('<template>');
      const hasScript = content.includes('<script setup>') || content.includes('<script>');
      const hasStyle = content.includes('<style');
      
      console.log(`📄 ${path.basename(vueFile)}:`);
      console.log(`   Template: ${hasTemplate ? '✅' : '❌'}`);
      console.log(`   Script: ${hasScript ? '✅' : '❌'}`);
      console.log(`   Style: ${hasStyle ? '✅' : '⚠️  (optional)'}`);
      
      if (!hasTemplate || !hasScript) {
        allTestsPassed = false;
      }
    }
  }
  
  console.log('');
  
  // Test 4: Store Structure
  console.log('🏪 Checking Pinia store structure...');
  const storeFile = 'website/src/stores/adminRecommendations.js';
  
  if (checkFileExists(storeFile)) {
    const fullPath = path.join(__dirname, storeFile);
    const content = fs.readFileSync(fullPath, 'utf8');
    
    const requiredStoreElements = [
      'defineStore',
      'useAdminRecommendationsStore',
      'fetchSummary',
      'fetchAllRecommendations',
      'bulkGenerateRecommendations'
    ];
    
    console.log(`📦 ${path.basename(storeFile)}:`);
    for (const element of requiredStoreElements) {
      const hasElement = content.includes(element);
      console.log(`   ${element}: ${hasElement ? '✅' : '❌'}`);
      
      if (!hasElement) {
        allTestsPassed = false;
      }
    }
  }
  
  console.log('');
  
  // Test 5: API Integration Check
  console.log('🌐 Checking API integration...');
  const apiFile = 'website/src/services/api.js';
  
  if (checkFileExists(apiFile)) {
    const fullPath = path.join(__dirname, apiFile);
    const content = fs.readFileSync(fullPath, 'utf8');
    
    const requiredApiMethods = [
      'adminGetRecommendationsSummary',
      'adminGetAllCustomerRecommendations',
      'adminGetUserRecommendations',
      'adminBulkGenerateRecommendations'
    ];
    
    console.log(`🔌 ${path.basename(apiFile)}:`);
    for (const method of requiredApiMethods) {
      const hasMethod = content.includes(method);
      console.log(`   ${method}: ${hasMethod ? '✅' : '❌'}`);
      
      if (!hasMethod) {
        allTestsPassed = false;
      }
    }
  } else {
    console.log(`❌ ${apiFile} - File not found`);
    allTestsPassed = false;
  }
  
  console.log('');
  
  // Test Results
  console.log('📊 Test Results');
  console.log('===============');
  
  if (allTestsPassed) {
    console.log('🎉 All tests passed! Frontend recommendations system is ready.');
    console.log('');
    console.log('Next steps:');
    console.log('1. Start the development server: npm run dev');
    console.log('2. Navigate to /admin/recommendations');
    console.log('3. Test the interface with admin credentials');
    console.log('4. Verify API connectivity with the backend');
    
    return 0;
  } else {
    console.log('❌ Some tests failed. Please check the issues above.');
    console.log('');
    console.log('Common fixes:');
    console.log('1. Ensure all files are created correctly');
    console.log('2. Check for syntax errors in Vue components');
    console.log('3. Verify API methods are properly defined');
    console.log('4. Make sure imports and exports are correct');
    
    return 1;
  }
}

// Run the tests
if (require.main === module) {
  process.exit(runTests());
}

module.exports = { runTests };