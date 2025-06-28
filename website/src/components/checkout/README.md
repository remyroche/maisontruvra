# Checkout Components

This directory contains all the components for the checkout flow implementation.

## Components Overview

### 1. **CheckoutView.vue** (Main View)
- **Location**: `src/views/public/CheckoutView.vue`
- **Purpose**: Main checkout page that orchestrates the entire checkout flow
- **Features**:
  - Multi-step progress indicator
  - Responsive layout with order summary sidebar
  - Authentication state management
  - Step-by-step navigation
  - Integration with all checkout components

### 2. **AddressSelector.vue**
- **Purpose**: Manages shipping address selection and creation
- **Features**:
  - Displays user's saved addresses
  - Address creation/editing modal
  - Form validation for address fields
  - Default address selection
  - Integration with user store

### 3. **DeliveryMethodSelector.vue**
- **Purpose**: Handles delivery method selection
- **Features**:
  - Fetches available delivery methods based on address
  - Displays delivery options with pricing and timing
  - Shows delivery features (tracking, insurance, etc.)
  - Handles unavailable delivery methods
  - Estimated delivery date calculation

### 4. **OrderSummary.vue**
- **Purpose**: Displays cart contents and order totals
- **Features**:
  - Cart items display with images and details
  - Promo code application/removal
  - Order totals calculation including delivery
  - Loyalty points display
  - Real-time updates when delivery method changes

### 5. **GuestCheckoutForm.vue**
- **Purpose**: Handles guest checkout information collection
- **Features**:
  - Contact information form (email, phone, name)
  - Optional account creation
  - Newsletter subscription options
  - Terms and conditions acceptance
  - Form validation with real-time feedback

### 6. **LoginForm.vue**
- **Purpose**: User authentication for existing customers
- **Features**:
  - Email/password login
  - Remember me functionality
  - Forgot password modal
  - Switch to guest checkout option
  - Form validation and error handling

### 7. **PaymentForm.vue**
- **Purpose**: Payment information collection
- **Features**:
  - Credit card form with validation
  - Card number formatting and Luhn validation
  - Expiry date and CVC validation
  - Payment method selection (card/PayPal)
  - Security notices and terms acceptance

## Store Integration

### CheckoutStore (`src/stores/checkout.js`)
- Manages checkout flow state
- Handles step progression
- Stores selected address and delivery method
- Manages guest vs authenticated user modes
- Handles order submission

### CartStore (`src/stores/cart.js`)
- Manages cart state and operations
- Provides cart clearing functionality
- Integrates with order summary

### UserStore (`src/stores/user.js`)
- Manages user authentication state
- Provides user profile information

## API Endpoints Expected

The checkout flow expects the following API endpoints:

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/forgot-password` - Password reset
- `GET /api/auth/status` - Check authentication status

### Addresses
- `GET /api/user/addresses` - Fetch user addresses
- `POST /api/user/addresses` - Create new address
- `PUT /api/user/addresses/:id` - Update address

### Cart
- `GET /api/cart` - Fetch cart contents
- `POST /api/cart/promo-code` - Apply promo code
- `DELETE /api/cart/promo-code` - Remove promo code

### Delivery
- `GET /api/delivery/methods` - Fetch delivery methods for address

### Orders
- `POST /api/orders/create` - Create new order
- `GET /api/orders/:id` - Fetch order details

## Usage

```vue
<template>
  <CheckoutView />
</template>
```

The checkout flow automatically:
1. Checks authentication status
2. Validates cart contents
3. Guides users through the checkout steps
4. Handles both guest and authenticated checkout
5. Redirects to order confirmation on success

## Styling

All components use Tailwind CSS with the custom brand colors:
- `brand-burgundy` - Primary brand color
- `brand-cream` - Light background color
- `brand-dark-brown` - Dark text color

## Form Validation

All forms include:
- Real-time validation
- Error message display
- Required field indicators
- Accessibility features (ARIA labels, proper form structure)

## Responsive Design

The checkout flow is fully responsive:
- Mobile-first design
- Collapsible sections on small screens
- Sticky order summary on desktop
- Touch-friendly form controls

## Error Handling

- API errors are handled by the global API interceptor
- Form validation errors are displayed inline
- Network errors show user-friendly messages
- Graceful degradation for missing data