# Admin Recommendations Management Guide

This guide explains the new admin recommendation functionality that allows administrators to view and manage customer recommendations with bulk operations.

## Overview

The admin recommendation system provides administrators with comprehensive tools to:
- View recommendations for all customers at once
- Get detailed recommendations for specific users
- Perform bulk operations for marketing campaigns
- Export recommendation data for analysis
- Search for users and preview their recommendations

## API Endpoints

### Base URL
All admin recommendation endpoints are prefixed with `/api/admin/recommendations`

### Authentication & Authorization
- All endpoints require JWT authentication (`@jwt_required()`)
- Access is restricted to users with roles: `Admin`, `Manager`, or `Marketing`

### Available Endpoints

#### 1. Get Recommendations Summary
```
GET /api/admin/recommendations/summary
```
Returns overview statistics about recommendations across all users.

**Response:**
```json
{
  "total_active_users": 150,
  "users_with_personalized_recommendations": 120,
  "users_with_general_recommendations": 30,
  "popular_categories": [
    {"category_id": 1, "order_count": 45},
    {"category_id": 3, "order_count": 32}
  ]
}
```

#### 2. Get All Customer Recommendations
```
GET /api/admin/recommendations/all
```
Returns paginated recommendations for all customers.

**Query Parameters:**
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 50, max: 100)
- `limit_per_user`: Recommendations per user (default: 5, max: 10)

**Response:**
```json
{
  "recommendations": [
    {
      "user_id": 123,
      "user_email": "customer@example.com",
      "user_name": "John Doe",
      "registration_date": "2024-01-15T10:30:00",
      "last_login": "2024-06-20T14:22:00",
      "recommendations": [...],
      "recommendation_count": 5
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total_users": 150,
    "total_pages": 3,
    "has_next": true,
    "has_prev": false
  }
}
```

#### 3. Get User-Specific Recommendations
```
GET /api/admin/recommendations/user/<user_id>
```
Returns detailed recommendations for a specific user.

**Query Parameters:**
- `limit`: Number of recommendations (default: 5, max: 20)

**Response:**
```json
{
  "user_id": 123,
  "user_email": "customer@example.com",
  "user_name": "John Doe",
  "recommendations": [...],
  "recommendation_count": 5
}
```

#### 4. Bulk Generate Recommendations
```
POST /api/admin/recommendations/bulk
```
Generate recommendations for multiple users at once.

**Request Body:**
```json
{
  "user_ids": [123, 456, 789],
  "limit_per_user": 5
}
```

**Response:**
```json
{
  "results": [
    {
      "user_id": 123,
      "status": "success",
      "data": {...}
    },
    {
      "user_id": 456,
      "status": "error",
      "error": "User not found"
    }
  ],
  "total_processed": 3,
  "successful": 2,
  "failed": 1
}
```

#### 5. Export Recommendations
```
GET /api/admin/recommendations/export
```
Export recommendation data in JSON or CSV format.

**Query Parameters:**
- `format`: 'json' or 'csv' (default: 'json')
- `limit_per_user`: Recommendations per user (default: 5, max: 10)
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 100, max: 500)

**CSV Export Columns:**
- User ID, User Email, User Name, Registration Date, Last Login
- Recommendation Count, Product IDs, Product Names, Product Categories

#### 6. Search Users for Recommendations
```
GET /api/admin/recommendations/users/search
```
Search for users to view their recommendations.

**Query Parameters:**
- `q`: Search query (email, name, or user ID)
- `limit`: Number of results (default: 20, max: 50)

**Response:**
```json
{
  "users": [
    {
      "user_id": 123,
      "user_email": "customer@example.com",
      "user_name": "John Doe",
      "registration_date": "2024-01-15T10:30:00",
      "has_recommendations": true,
      "recommendation_preview": [...]
    }
  ],
  "total_found": 1,
  "query": "john"
}
```

## Service Layer Methods

### RecommendationService New Methods

#### `get_all_customer_recommendations(limit_per_user=5, page=1, per_page=50)`
Retrieves recommendations for all customers with pagination support.

#### `get_recommendations_summary()`
Provides statistical overview of recommendation data across all users.

#### `bulk_generate_recommendations(user_ids, limit_per_user=5)`
Generates recommendations for multiple users in a single operation.

#### Enhanced `get_admin_recommendations_for_user(user_id, limit=5)`
Now returns enriched data including user context information.

## Usage Examples

### Python/Requests Example
```python
import requests

# Get all customer recommendations
response = requests.get(
    'http://localhost:5000/api/admin/recommendations/all',
    headers={'Authorization': 'Bearer YOUR_JWT_TOKEN'},
    params={'page': 1, 'per_page': 25, 'limit_per_user': 3}
)

recommendations = response.json()
```

### JavaScript/Fetch Example
```javascript
// Bulk generate recommendations
const response = await fetch('/api/admin/recommendations/bulk', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_JWT_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    user_ids: [123, 456, 789],
    limit_per_user: 5
  })
});

const results = await response.json();
```

### cURL Example
```bash
# Export recommendations as CSV
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     "http://localhost:5000/api/admin/recommendations/export?format=csv&limit_per_user=3" \
     -o recommendations.csv
```

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid parameters)
- `401`: Unauthorized (missing/invalid JWT)
- `403`: Forbidden (insufficient permissions)
- `404`: Not Found (user not found)
- `500`: Internal Server Error

Error responses include descriptive messages:
```json
{
  "error": "Cannot process more than 100 users at once"
}
```

## Performance Considerations

### Pagination
- Use pagination for large datasets to avoid timeouts
- Default page size is optimized for performance
- Maximum limits are enforced to prevent system overload

### Bulk Operations
- Bulk recommendation generation is limited to 100 users per request
- Failed individual operations don't stop the entire batch
- Consider breaking large operations into smaller chunks

### Caching
- Recommendation data can be cached at the application level
- Consider implementing Redis caching for frequently accessed data
- Cache invalidation should occur when user purchase patterns change

## Security Features

### Input Validation
- All user inputs are sanitized using `InputSanitizer`
- Integer parameters are validated and bounded
- SQL injection protection through SQLAlchemy ORM

### Access Control
- Role-based access control (RBAC) enforced on all endpoints
- JWT token validation required
- Audit logging for admin actions (if audit system is enabled)

### Rate Limiting
- Standard rate limiting applies to all admin endpoints
- Bulk operations have additional safeguards against abuse

## Integration with Frontend

### Admin Dashboard Integration
The new endpoints are designed to integrate seamlessly with admin dashboard interfaces:

1. **Dashboard Overview**: Use `/summary` endpoint for dashboard widgets
2. **Customer List**: Use `/all` endpoint with pagination for customer tables
3. **Individual Customer View**: Use `/user/<id>` for detailed customer pages
4. **Bulk Operations**: Use `/bulk` for marketing campaign tools
5. **Data Export**: Use `/export` for analytics and reporting

### Recommended UI Components
- Paginated data tables for customer recommendations
- Search interface for finding specific customers
- Bulk selection tools for marketing campaigns
- Export buttons for data analysis
- Progress indicators for bulk operations

## Backward Compatibility

The original admin endpoint `/api/admin/users/<user_id>/recommendations` is maintained for backward compatibility but marked as deprecated. It includes deprecation headers:
- `X-Deprecated: true`
- `X-Deprecated-Message: Use /api/admin/recommendations/user/<user_id> instead`

## Testing

A test script is provided at `test_admin_recommendations.py` to verify functionality:

```bash
python test_admin_recommendations.py
```

This script tests:
- Service method functionality
- Route structure and imports
- Basic error handling

## Future Enhancements

Potential future improvements:
1. **Real-time Updates**: WebSocket support for live recommendation updates
2. **A/B Testing**: Framework for testing different recommendation algorithms
3. **Analytics Dashboard**: Detailed metrics on recommendation performance
4. **Machine Learning**: Integration with ML models for better recommendations
5. **Personalization Rules**: Admin interface for customizing recommendation logic

## Support

For issues or questions regarding the admin recommendation system:
1. Check the error logs in the monitoring system
2. Verify user permissions and JWT tokens
3. Review the API documentation for correct parameter usage
4. Test with the provided test script to isolate issues