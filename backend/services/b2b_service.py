import json
import logging
from decimal import Decimal

from backend.database import db
from backend.models.user_models import User
from backend.models.b2b_models import B2BUser, B2BAccount
from backend.models.b2b_loyalty_models import LoyaltyTier
from backend.models.product_models import Product
from backend.models.cart_models import Cart, CartItem
from backend.models.order_models import Order, OrderItem
from backend.models.invoice_models import Invoice
from backend.services.exceptions import NotFoundException, ServiceError
from backend.extensions import redis_client # Assuming redis_client is initialized in extensions.py
from .monitoring_service import MonitoringService

logger = logging.getLogger(__name__)
CACHE_TTL_SECONDS = 600 # Cache for 10 minutes

class B2BService:
    """
    Handles business logic related to B2B accounts, pricing, carts, and orders.
    """

    @staticmethod
    def get_company_profile_by_user(user_id: int) -> B2BAccount:
        user = db.session.get(User, user_id)
        if not user or not user.is_b2b or not user.b2b_account:
            raise NotFoundException("Profil B2B non trouvé pour cet utilisateur.")
        return user.b2b_account

    @staticmethod
    def update_company_profile_by_user(user_id: int, data: dict) -> B2BAccount:
        profile = B2BService.get_company_profile_by_user(user_id)
        for key, value in data.items():
            if hasattr(profile, key) and key not in ['id', 'user_id']:
                setattr(profile, key, value)
        db.session.commit()
        return profile

    @staticmethod
    def get_b2b_invoices_paginated(user_id: int, page: int, per_page: int):
        account = B2BService.get_company_profile_by_user(user_id)
        invoices_pagination = Invoice.query.filter_by(b2b_account_id=account.id).order_by(Invoice.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        return invoices_pagination

    @staticmethod
    def get_b2b_cart(user_id: int) -> Cart:
        account = B2BService.get_company_profile_by_user(user_id)
        cart = Cart.query.filter_by(b2b_account_id=account.id).first()
        if not cart:
            cart = Cart(user_id=user_id, b2b_account_id=account.id)
            db.session.add(cart)
            db.session.commit()
        return cart

    @staticmethod
    def get_b2b_price(user: User, product: Product) -> Decimal:
        """
        Calculates the B2B price for a product based on the user's company tier.
        Uses Redis for caching.
        """
        if not user or not user.is_b2b:
            return product.price

        account = user.b2b_account
        if not account or not account.tier_id:
            return product.price # Pas de tier, pas de réduction

        tier_id = account.tier_id
        cache_key = f"b2b_price:tier_{tier_id}:product_{product.id}"
        
        try:
            cached_price = redis_client.get(cache_key)
            if cached_price:
                return Decimal(cached_price.decode('utf-8'))
        except Exception as e:
            MonitoringService.log_error(f"Erreur Redis GET pour la clé {cache_key}: {e}", "B2BService", level='WARNING')

        tier = db.session.get(LoyaltyTier, tier_id)
        if not tier or tier.discount_percentage <= 0:
            calculated_price = product.price
        else:
            discount = (product.price * tier.discount_percentage) / Decimal(100)
            calculated_price = product.price - discount
        
        try:
            redis_client.setex(cache_key, CACHE_TTL_SECONDS, str(calculated_price))
        except Exception as e:
            MonitoringService.log_error(f"Erreur Redis SETEX pour la clé {cache_key}: {e}", "B2BService", level='WARNING')
            
        return calculated_price.quantize(Decimal("0.01"))

    @staticmethod
    def create_b2b_order(user_id: int, shipping_address_id: int, billing_address_id: int) -> Order:
        """Creates a B2B order from the company's cart."""
        user = db.session.get(User, user_id)
        if not user or not user.is_b2b:
            raise NotFoundException("Utilisateur B2B non trouvé")
            
        cart = B2BService.get_b2b_cart(user_id)
        if not cart.items:
            raise ServiceError("Impossible de créer une commande à partir d'un panier vide.", 400)
        
        total_cost = Decimal(0)
        order_items = []
        for item in cart.items:
            product_price = B2BService.get_b2b_price(user, item.product)
            total_cost += product_price * item.quantity
            order_items.append(OrderItem(
                product_id=item.product_id,
                quantity=item.quantity,
                price_at_purchase=product_price
            ))
            
        new_order = Order(
            user_id=user_id,
            b2b_account_id=user.b2b_account_id,
            total_cost=total_cost,
            items=order_items,
            shipping_address_id=shipping_address_id,
            billing_address_id=billing_address_id
        )

        db.session.add(new_order)
        # Vider le panier
        for item in cart.items:
            db.session.delete(item)
            
        db.session.commit()
        
        MonitoringService.log_info(f"Commande B2B {new_order.id} créée pour le compte {user.b2b_account_id}", "B2BService")
        return new_order
