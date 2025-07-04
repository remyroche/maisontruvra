# This file makes the 'models' directory a Python package.
# It also helps in importing all models into the application's context for tools like Flask-Migrate.

from .address_models import Address
from .admin_audit_models import AdminAuditLog
from .analytics_models import PageView, SalesAnalytics
from .auth_models import TokenBlocklist
from .b2b_loyalty_models import (
    ExclusiveReward,
    LoyaltyPointLog,
    LoyaltyTier,
    PointVoucher,
    ReferralRewardTier,
    UserLoyalty,
)
from .b2b_models import B2BAccount, B2BPartnershipRequest, B2BTier, Company, Tier
from .base import BaseModel
from .blog_models import BlogCategory, BlogPost
from .cart_models import Cart, CartItem
from .discount_models import Discount, DiscountType, DiscountUsage
from .enums import OrderStatus, RoleType, UserStatus  # loyalty_account import removed
from .inventory_models import (
    Inventory,
    InventoryReservation,
    StockMovement,  # <-- ADD THIS LINE
)
from .loyalty_account import LoyaltyAccount
from .loyalty_program import LoyaltyProgram  # <-- ADD THIS LINE
from .newsletter_models import (
    NewsletterSubscriber,
)  # Corrected: Import NewsletterSubscriber
from .order_models import Invoice, Order, OrderItem, OrderStatusEnum
from .passport_models import PassportEntry, ProductPassport, SerializedItem
from .product_models import (
    Category,
    Collection,
    Product,
    ProductImage,
    Review,
    Tag,
    product_tags,
)
from .referral_models import Referral
from .request_models import GenericRequest
from .user_models import Role, User, UserRole
from .utility_models import Setting
