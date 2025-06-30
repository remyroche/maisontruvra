
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
        self.order = OrderService(self.db_session, self.cart, self.inventory, self.notification)
        self.checkout = CheckoutService(self.db_session, self.order, self.cart, self.inventory, self.notification, self.user)
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
        self.invoice = InvoiceService(self.db_session, self.order, self.pdf)
        self.loyalty = LoyaltyService(self.db_session, self.user)
        self.mfa = MFAService(self.db_session, self.user)
        self.monitoring = MonitoringService(self.db_session)
        self.newsletter = NewsletterService(self.db_session, self.notification)
        self.passport = PassportService(self.db_session)
        self.pdf = PDFService(self.config)
        self.pos = POSService(self.db_session, self.inventory)
        self.quote = QuoteService(self.db_session, self.user)
        self.rbac = RBACService(self.db_session)
        self.referral = ReferralService(self.db_session, self.user)
        self.review = ReviewService(self.db_session, self.product, self.user)
        self.site_settings = SiteSettingsService(self.db_session)
        self.wishlist = WishlistService(self.db_session, self.product)

def init_app(app):
    """Initializes the services with the Flask app context."""
    from backend.extensions import db, mail, celery
    app.service_provider = ServiceProvider(db.session, app.config, mail, celery)

