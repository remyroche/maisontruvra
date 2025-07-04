# This file makes the 'models' directory a Python package.
# It also helps in importing all models into the application's context for tools like Flask-Migrate.

from .base import BaseModel
from .user_models import User, Role, UserRole
from .address_models import Address
from .product_models import (
    Product,
    Category,
    Collection,
    Review,
    Tag,
    product_tags,
    ProductImage,
)
from .order_models import Order, OrderItem, Invoice, OrderStatusEnum
from .cart_models import Cart, CartItem
from .b2b_models import Tier, B2BTier, B2BAccount, B2BPartnershipRequest, Company
from .b2b_loyalty_models import (
    LoyaltyTier,
    UserLoyalty,
    ReferralRewardTier,
    PointVoucher,
    ExclusiveReward,
    LoyaltyPointLog,
)
from .passport_models import ProductPassport, PassportEntry
from .blog_models import BlogPost, BlogCategory
from .newsletter_models import (
    NewsletterSubscriber,
)  # Corrected: Import NewsletterSubscriber
from .inventory_models import Inventory, InventoryReservation
from .auth_models import TokenBlocklist
from .admin_audit_models import AdminAuditLog

from .referral_models import Referral
from .request_models import GenericRequest
from .utility_models import Setting
from .analytics_models import PageView, SalesAnalytics
from .enums import OrderStatus, UserStatus, RoleType  # loyalty_account import removed
from .loyalty_account import LoyaltyAccount
from .loyalty_program import LoyaltyProgram  # <-- ADD THIS LINE
from .discount_models import Discount, DiscountType, DiscountUsage
from .passport_models import SerializedItem
from .inventory_models import StockMovement  # <-- ADD THIS LINE
