# Frontend Admin Recommendations Management

This document describes the Vue.js frontend implementation for the admin recommendations management system.

## Overview

The frontend provides a comprehensive interface for administrators to manage customer recommendations, including:

- Dashboard overview with recommendation statistics
- Bulk operations for marketing campaigns
- Individual customer recommendation management
- Data export capabilities
- Real-time search and filtering

## Architecture

### Components Structure

```
website/src/
├── views/admin/
│   ├── ManageRecommendationsView.vue     # Main recommendations management page
│   └── DashboardHomeView.vue             # Admin dashboard with widgets
├── components/admin/
│   ├── BulkOperationsModal.vue           # Bulk operations interface
│   ├── UserRecommendationsModal.vue      # Individual user details
│   └── RecommendationsDashboardWidget.vue # Dashboard widget
├── stores/
│   └── adminRecommendations.js           # Pinia store for state management
└── locales/pages/
    └── admin-recommendations.json        # Internationalization strings
```

### State Management

The application uses Pinia for state management with the `useAdminRecommendationsStore` store that handles:

- Fetching recommendation summaries and data
- Managing user selections for bulk operations
- Handling search functionality
- Coordinating API calls and error handling

## Features

### 1. Dashboard Integration

**RecommendationsDashboardWidget.vue**
- Shows key recommendation statistics
- Displays recommendation coverage percentage
- Lists popular categories
- Provides quick access to full management interface

**Usage in Dashboard:**
```vue
<template>
  <RecommendationsDashboardWidget />
</template>

<script setup>
import RecommendationsDashboardWidget from '@/components/admin/RecommendationsDashboardWidget.vue';
</script>
```

### 2. Main Management Interface

**ManageRecommendationsView.vue**
- Paginated table of all customers with recommendations
- Bulk selection and operations
- Real-time search functionality
- Export capabilities
- Individual user detail access

**Key Features:**
- **Summary Cards**: Overview statistics at the top
- **Search Bar**: Real-time user search with debouncing
- **Bulk Selection**: Checkbox-based user selection
- **Pagination**: Efficient data loading with page controls
- **Export**: CSV/JSON export functionality

### 3. Bulk Operations

**BulkOperationsModal.vue**
- Generate recommendations for multiple users
- Export data for selected users
- Email campaign preparation (future feature)
- Progress tracking and result reporting

**Supported Operations:**
- **Generate Fresh Recommendations**: Bulk recommendation generation
- **Export Data**: CSV/JSON export for selected users
- **Email Campaign Prep**: Placeholder for future email integration

### 4. Individual User Management

**UserRecommendationsModal.vue**
- Detailed view of user's recommendations
- Grid and list view modes
- Individual user data export
- Recommendation refresh capability

**Features:**
- **User Information Panel**: Shows user details and recommendation stats
- **Product Display**: Grid or list view of recommended products
- **Export Function**: Individual user data export
- **Refresh Capability**: Generate new recommendations for the user

## API Integration

### Service Layer

The frontend integrates with the backend through the main API service (`/src/services/api.js`):

```javascript
// Admin Recommendations API methods
adminGetRecommendationsSummary()
adminGetAllCustomerRecommendations(params)
adminGetUserRecommendations(userId, params)
adminSearchUsers(params)
adminBulkGenerateRecommendations(data)
adminExportRecommendations(params)
```

### Store Actions

The Pinia store provides these main actions:

```javascript
// Data fetching
fetchSummary()
fetchAllRecommendations(options)
fetchUserRecommendations(userId, limit)
searchUsers(query, limit)

// Operations
bulkGenerateRecommendations(userIds, limitPerUser)
exportRecommendations(format, options)

// User selection management
toggleUserSelection(userId)
selectAllUsers()
clearSelection()
isUserSelected(userId)

// Pagination
goToPage(page)
nextPage()
prevPage()
```

## Routing

The recommendations management is integrated into the admin routing system:

```javascript
// Router configuration
{
  path: '/admin/recommendations',
  name: 'AdminManageRecommendations',
  component: () => import('@/views/admin/ManageRecommendationsView.vue'),
  meta: { 
    requiresAuth: true, 
    requiredRoles: ['Admin', 'Manager', 'Marketing'] 
  }
}
```

**Navigation Integration:**
- Added to admin sidebar with LightBulb icon
- Accessible from dashboard quick actions
- Integrated into main admin navigation flow

## User Experience

### Responsive Design

The interface is fully responsive with:
- **Mobile**: Stacked layout with simplified controls
- **Tablet**: Two-column layout with condensed information
- **Desktop**: Full multi-column layout with all features

### Loading States

Comprehensive loading states for:
- Initial data loading with skeleton screens
- Bulk operation progress indicators
- Search result loading
- Individual user data fetching

### Error Handling

Robust error handling with:
- User-friendly error messages
- Retry mechanisms for failed operations
- Graceful degradation for partial failures
- Toast notifications for operation results

### Performance Optimizations

- **Debounced Search**: 300ms delay to prevent excessive API calls
- **Pagination**: Efficient data loading with configurable page sizes
- **Lazy Loading**: Components loaded on demand
- **Caching**: Store-level caching of frequently accessed data

## Internationalization

Full i18n support with French translations in `admin-recommendations.json`:

```json
{
  "title": "Customer Recommendations",
  "actions": {
    "export_csv": "Export CSV",
    "refresh": "Refresh"
  },
  "messages": {
    "export_success": "Recommendations exported successfully"
  }
}
```

## Styling

### Design System

The interface follows the existing admin design system:

- **Colors**: Blue primary, green success, red error, gray neutrals
- **Typography**: Consistent font sizes and weights
- **Spacing**: 4px grid system with Tailwind CSS
- **Components**: Consistent button styles, form elements, and cards

### Custom Styles

```css
/* Smooth transitions */
.transition-colors {
  transition: background-color 0.2s ease, color 0.2s ease;
}

/* Custom scrollbars */
.overflow-x-auto::-webkit-scrollbar {
  height: 8px;
}

/* Loading animations */
.animate-spin {
  animation: spin 1s linear infinite;
}
```

## Security

### Access Control

- **Route Guards**: Role-based access control
- **Component Guards**: Permission checks within components
- **API Security**: JWT token validation on all requests

### Data Protection

- **Input Sanitization**: All user inputs are sanitized
- **XSS Prevention**: Proper data binding and sanitization
- **CSRF Protection**: Token-based CSRF protection

## Testing

### Component Testing

Recommended test coverage:

```javascript
// Example test structure
describe('ManageRecommendationsView', () => {
  it('loads recommendation data on mount', async () => {
    // Test data loading
  });
  
  it('handles user selection correctly', () => {
    // Test selection logic
  });
  
  it('performs bulk operations', async () => {
    // Test bulk operations
  });
});
```

### Integration Testing

- **API Integration**: Mock API responses for testing
- **Store Testing**: Test Pinia store actions and state
- **Router Testing**: Test navigation and route guards

## Deployment

### Build Configuration

The components are included in the standard Vue.js build process:

```bash
# Development
npm run dev

# Production build
npm run build

# Preview production build
npm run preview
```

### Environment Variables

No additional environment variables required - uses existing API configuration.

## Future Enhancements

### Planned Features

1. **Real-time Updates**: WebSocket integration for live data updates
2. **Advanced Filtering**: More sophisticated filtering options
3. **Analytics Dashboard**: Detailed recommendation performance metrics
4. **A/B Testing**: Interface for testing different recommendation algorithms
5. **Email Integration**: Direct email campaign creation from recommendations

### Performance Improvements

1. **Virtual Scrolling**: For large datasets
2. **Background Sync**: Offline capability with sync when online
3. **Caching Strategy**: More sophisticated caching with TTL
4. **Lazy Loading**: Progressive loading of recommendation data

## Troubleshooting

### Common Issues

**1. Recommendations not loading**
- Check API endpoint availability
- Verify user permissions
- Check browser console for errors

**2. Bulk operations failing**
- Ensure user selection is within limits (max 100)
- Check network connectivity
- Verify backend service status

**3. Export not working**
- Check browser popup blockers
- Verify file download permissions
- Ensure sufficient data for export

### Debug Mode

Enable debug mode by setting localStorage:

```javascript
localStorage.setItem('debug', 'true');
```

This will enable additional console logging for troubleshooting.

## Support

For technical support:

1. Check the browser console for error messages
2. Verify API connectivity using browser dev tools
3. Test with different user roles to isolate permission issues
4. Review the backend logs for API-related issues

## Contributing

When contributing to the recommendations frontend:

1. Follow the existing Vue.js patterns and conventions
2. Ensure responsive design across all screen sizes
3. Add appropriate error handling and loading states
4. Include internationalization strings for new text
5. Test with different user roles and permissions
6. Update this documentation for significant changes