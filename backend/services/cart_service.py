from backend.database import db
from backend.models.cart_models import Cart, CartItem
from backend.models.product_models import Product

class CartService:
    @staticmethod
    def get_cart(user_id: int, create_if_not_exists: bool = False) -> Cart | None:
        """Gets a user's cart, optionally creating it if it doesn't exist."""
        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart and create_if_not_exists:
            cart = Cart(user_id=user_id)
            db.session.add(cart)
            db.session.commit()
        return cart

    @staticmethod
    def add_or_update_item(user_id: int, product_id: int, quantity: int) -> Cart:
        """Adds an item to the cart or updates its quantity if it already exists."""
        cart = CartService.get_cart(user_id, create_if_not_exists=True)
        
        # Check if product exists
        product = Product.query.get(product_id)
        if not product:
            raise ValueError("Le produit n'existe pas.")

        # Check if item is already in cart
        cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()

        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
            db.session.add(cart_item)
        
        if cart_item.quantity <= 0:
            db.session.delete(cart_item)

        db.session.commit()
        return cart

    @staticmethod
    def remove_item(user_id: int, product_id: int) -> Cart:
        """Removes an item completely from the cart."""
        cart = CartService.get_cart(user_id)
        if not cart:
            raise ValueError("Panier non trouvé.")
            
        cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
        if cart_item:
            db.session.delete(cart_item)
            db.session.commit()
        
        return cart

    @staticmethod
    def clear_cart(user_id: int):
        """Removes all items from a user's cart."""
        cart = CartService.get_cart(user_id)
        if cart:
            CartItem.query.filter_by(cart_id=cart.id).delete()
            db.session.commit()
