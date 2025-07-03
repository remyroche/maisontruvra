import enum

class UserType(enum.Enum):
    ALL = "all"
    B2C = "B2C"
    B2B = "B2B"
    Staff = "Staff"
    NEW_CUSTOMERS = "new_customers"
    RETURNING_CUSTOMERS = "returning_customers"

class DiscountType(enum.Enum):
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    FREE_SHIPPING = "free_shipping"

class NotificationFrequency(enum.Enum):
    NEVER = 'never'
    INSTANT = 'instant'
    DAILY = 'daily'
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'

class OrderStatus(enum.Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    SHIPPED = 'shipped'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    REFUNDED = 'refunded'

class UserStatus(enum.Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    SUSPENDED = 'suspended'
    PENDING_VERIFICATION = 'pending_verification'

class RoleType(enum.Enum):
    ADMIN = 'admin'
    B2C_USER = 'b2c_user'
    B2B_USER = 'b2b_user'
    
class B2BRequestStatus(enum.Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'

class B2BStatus(enum.Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    SUSPENDED = 'suspended'

    
class B2BTier(enum.Enum):
    T1 = 'collaborateur'
    T2 = 'partenaire'
    T3 = 'associé'

class UserRole(enum.Enum):
    ADMIN = 'admin'
    B2C_USER = 'b2c_user'
    B2B_USER = 'b2b_user'
    STAFF = 'staff'

class LanguagePreference(enum.Enum):
    EN = 'en'
    FR = 'fr'
