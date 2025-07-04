# Service Provider for Dependency Injection
from backend.services.address_service import AddressService
from backend.services.admin_dashboard_service import AdminDashboardService
from backend.services.asset_service import AssetService
from backend.services.audit_log_service import AuditLogService
from backend.services.auth_service import AuthService
from backend.services.b2b_service import B2BService
from backend.services.background_task_service import BackgroundTaskService
from backend.services.blog_service import BlogService
from backend.services.cart_service import CartService
from backend.services.checkout_service import CheckoutService
from backend.services.contact_service import ContactService
from backend.services.dashboard_service import DashboardService
from backend.services.delivery_service import DeliveryService
from backend.services.discount_service import DiscountService
from backend.services.email_service import EmailService
from backend.services.inventory_service import InventoryService
from backend.services.invoice_service import InvoiceService
from backend.services.loyalty_service import LoyaltyService
from backend.services.mfa_service import MFAService
from backend.services.monitoring_service import MonitoringService
from backend.services.newsletter_service import NewsletterService
from backend.services.notification_service import NotificationService
from backend.services.order_service import OrderService
from backend.services.passport_service import PassportService
from backend.services.pdf_service import PDFService
from backend.services.pos_service import POSService
from backend.services.product_service import ProductService
from backend.services.quote_service import QuoteService
from backend.services.rbac_service import RBACService
from backend.services.referral_service import ReferralService
from backend.services.review_service import ReviewService
from backend.services.site_settings_service import SiteSettingsService
from backend.services.user_service import UserService
from backend.services.wishlist_service import WishlistService


class ServiceProvider:
    """Central service provider for dependency injection."""

    def __init__(self, db_session, config, mail, celery_app):
        self.db_session = db_session
        self.config = config
        self.mail = mail
        self.celery_app = celery_app

        # Initialize services
        self.email = EmailService(mail, config)
        self.notification = NotificationService(self.db_session, self.email)
        self.user = UserService(self.db_session, self.notification)
        self.auth = AuthService(self.db_session, self.user)
        self.inventory = InventoryService(self.db_session, self.notification)
        self.product = ProductService(self.db_session, self.inventory)
        self.cart = CartService(self.db_session, self.product, self.inventory)
        self.order = OrderService(
            self.db_session, self.cart, self.inventory, self.notification
        )
        self.checkout = CheckoutService(
            self.db_session,
            self.order,
            self.cart,
            self.inventory,
            self.notification,
            self.user,
        )
        self.b2b = B2BService(self.db_session, self.user, self.notification)

        # ... initialize other services here, injecting dependencies as needed
        self.address = AddressService(self.db_session)
        self.admin_dashboard = AdminDashboardService(self.db_session)
        self.asset = AssetService(self.db_session, self.config)
        self.audit_log = AuditLogService(self.db_session)
        self.background_task = BackgroundTaskService(self.celery_app)
        self.blog = BlogService(self.db_session)
        self.contact = ContactService(self.db_session, self.notification)
        self.dashboard = DashboardService(self.db_session, self.user)
        self.delivery = DeliveryService(self.db_session)
        self.discount = DiscountService(self.db_session)
        self.pdf = PDFService(self.config)
        self.invoice = InvoiceService(self.db_session, self.order, self.pdf)
        self.loyalty = LoyaltyService(self.db_session, self.user)
        self.mfa = MFAService(self.db_session, self.user)
        self.monitoring = MonitoringService(self.db_session)
        self.newsletter = NewsletterService(self.db_session, self.notification)
        self.passport = PassportService(self.db_session)
        self.pos = POSService(self.db_session, self.inventory)
        self.quote = QuoteService(self.db_session, self.user)
        self.rbac = RBACService(self.db_session)
        self.referral = ReferralService(self.db_session, self.user)
        self.review = ReviewService(self.db_session, self.product, self.user)
        self.site_settings = SiteSettingsService(self.db_session)
        self.wishlist = WishlistService(self.db_session, self.product)


def init_app(app):
    """Initializes the services with the Flask app context."""
    from backend.extensions import celery, db, mail

    app.service_provider = ServiceProvider(db.session, app.config, mail, celery)
