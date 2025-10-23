"""
Point of Sale (POS) Service for handling in-store transactions.
"""

import logging

from backend.database import db

from ..models import Order, OrderItem, Product, User, POSTransaction, db
from .exceptions import InsufficientStockException
from .inventory_service import InventoryService
from .order_service import OrderService
from .pdf_service import PDFService
from .payment_service import PaymentService

logger = logging.getLogger(__name__)


class POSService:
    """Service for handling Point of Sale transactions."""

    def __init__(self, logger):
        self.logger = logger
        self.product_service = ProductService(logger)
        self.cart_service = CartService(logger)
        self.inventory_service = InventoryService()
        self.order_service = OrderService()
        self.pdf_service = PDFService()
        self.payment_service = PaymentService(logger)

    def process_pos_sale(self, sale_data):
        """
        Processes a Point-of-Sale transaction.
        - Validates inventory
        - Creates an order
        - Processes payment (mocked)
        - Adjusts inventory
        - Generates a receipt (mocked)
        """
        customer_id = sale_data.get("customer_id")
        items = sale_data.get(
            "items", []
        )  # Expects a list of {'product_id': x, 'quantity': y}

        # Step 1: Validate that there is enough stock for all items in the sale.
        for item_data in items:
            if not self.inventory_service.check_stock(
                item_data["product_id"], item_data["quantity"]
            ):
                product = Product.query.get(item_data["product_id"])
                raise InsufficientStockException(
                    f"Not enough stock for product: {product.name}"
                )

        # Step 2: Calculate total and create the Order object.
        User.query.get(customer_id) if customer_id else None

        total_amount = 0
        order_items = []
        for item_data in items:
            product = Product.query.get(item_data["product_id"])
            quantity = item_data["quantity"]
            item_total = product.price * quantity
            total_amount += item_total
            order_items.append(
                OrderItem(product_id=product.id, quantity=quantity, price=product.price)
            )

        new_order = Order(
            user_id=customer_id,
            total_amount=total_amount,
            status="COMPLETED",  # POS orders are considered completed immediately.
            items=order_items,
        )

        # Step 3: Process the payment using real payment service.
        payment_result = self.payment_service.process_pos_payment(
            amount=total_amount,
            payment_method=sale_data.get("payment_method", "card"),
            payment_details=sale_data.get("payment_details", {})
        )
        
        payment_successful = payment_result.get("success", False)

        if not payment_successful:
            return {
                "success": False, 
                "error": payment_result.get("error", "Payment processing failed.")
            }

        new_order.payment_status = "PAID"
        new_order.payment_reference = payment_result.get("payment_intent_id") or payment_result.get("reference")
        db.session.add(new_order)
        db.session.commit()

        # Step 4: Adjust inventory levels now that the sale is confirmed.
        for item_data in items:
            self.inventory_service.decrease_stock(
                item_data["product_id"], item_data["quantity"]
            )

        # Step 5: Generate a receipt for the customer.
        # This is a mock; it would ideally generate a PDF or send a digital receipt.
        receipt_url = self.pdf_service.generate_receipt_for_order(new_order.id)

        db.session.commit()

        return {"success": True, "order_id": new_order.id, "receipt_url": receipt_url}

    def _process_pos_payment(self, amount, payment_details):
        """Process POS payment using the payment service."""
        return self.payment_service.process_pos_payment(
            amount=amount,
            payment_method=payment_details.get("payment_method", "card"),
            payment_details=payment_details
        )

    @staticmethod
    def create_transaction(transaction_data):
        """Create a POS transaction."""
        try:
            # Generate unique transaction ID
            import uuid
            transaction_id = f"POS_{uuid.uuid4().hex[:8].upper()}"
            
            # Create POS transaction record
            pos_transaction = POSTransaction(
                transaction_id=transaction_id,
                user_id=transaction_data.get("user_id"),
                total_amount=transaction_data.get("total_amount", 0),
                payment_method=transaction_data.get("payment_method", "cash"),
                payment_reference=transaction_data.get("payment_reference"),
                terminal_id=transaction_data.get("terminal_id"),
                cashier_id=transaction_data.get("cashier_id"),
                status="pending"
            )
            
            db.session.add(pos_transaction)
            db.session.flush()
            
            # Process the transaction
            result = POSService._process_transaction(pos_transaction, transaction_data)
            
            if result["success"]:
                pos_transaction.status = "completed"
                pos_transaction.processed_at = datetime.utcnow()
                pos_transaction.order_id = result.get("order_id")
            else:
                pos_transaction.status = "failed"
            
            db.session.commit()
            
            logger.info(f"POS transaction {transaction_id} created with status: {pos_transaction.status}")
            return pos_transaction
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating POS transaction: {e}")
            raise

    @staticmethod
    def _process_transaction(pos_transaction, transaction_data):
        """Process the actual transaction logic."""
        try:
            # Check inventory for all items
            items = transaction_data.get("items", [])
            for item in items:
                product = Product.query.get(item["product_id"])
                if not product or product.stock < item["quantity"]:
                    return {
                        "success": False,
                        "error": f"Insufficient stock for product {product.name if product else 'unknown'}"
                    }
            
            # Create order
            order = Order(
                user_id=transaction_data.get("user_id"),
                total_amount=pos_transaction.total_amount,
                order_status="COMPLETED",  # POS orders are completed immediately
                shipping_address_id=transaction_data.get("shipping_address_id"),
                billing_address_id=transaction_data.get("billing_address_id")
            )
            
            db.session.add(order)
            db.session.flush()
            
            # Create order items and update inventory
            for item in items:
                product = Product.query.get(item["product_id"])
                
                # Create order item
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=item["quantity"],
                    price_at_purchase=product.price
                )
                db.session.add(order_item)
                
                # Update inventory
                product.stock -= item["quantity"]
            
            db.session.commit()
            
            return {
                "success": True,
                "order_id": order.id
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error processing transaction: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def create_custom_cart_for_user(self, user_id, items_data):
        """
        Creates a new cart for a user with custom items and pricing.
        This is the core of the "direct-to-cart" B2B workflow.

        items_data should be a list of dicts, e.g.:
        [{
            "custom_item_name": "Special Truffle Oil",
            "custom_item_description": "Aged in oak barrels.",
            "quantity": 10,
            "price": 50.00
        }, {
            "product_id": 5, // Existing product
            "quantity": 20,
            "price": 15.00 // Special price for this product
        }]
        """
        try:
            # Create a new, empty cart for this transaction
            cart = Cart(user_id=user_id)
            db.session.add(cart)
            db.session.flush()

            for item_data in items_data:
                price = item_data["price"]
                quantity = item_data["quantity"]
                product_id_to_add = item_data.get("product_id")

                # If it's a custom item, create an exclusive product for it
                if "custom_item_name" in item_data:
                    exclusive_product = (
                        self.product_service.create_exclusive_product_for_quote(
                            name=item_data["custom_item_name"],
                            description=item_data.get("custom_item_description"),
                            price=price,
                            owner_id=user_id,
                        )
                    )
                    product_id_to_add = exclusive_product.id

                if not product_id_to_add:
                    raise ValueError(
                        "Item data is missing a product_id or custom_item_name."
                    )

                # Add the item to the new cart with the specified price
                cart_item = CartItem(
                    cart_id=cart.id,
                    product_id=product_id_to_add,
                    quantity=quantity,
                    price=price,
                )
                db.session.add(cart_item)

            db.session.commit()
            self.logger.info(
                f"POS Service created new cart {cart.id} for user {user_id} with custom items."
            )
            return cart

        except (SQLAlchemyError, ValueError) as e:
            db.session.rollback()
            self.logger.error(
                f"Error creating custom cart via POS service for user {user_id}: {e}"
            )
            raise

    @staticmethod
    def get_transaction(transaction_id):
        """Get a POS transaction by ID."""
        try:
            # Try to find by transaction_id first, then by UUID
            transaction = db.session.query(POSTransaction).filter(
                POSTransaction.transaction_id == transaction_id
            ).first()
            
            if not transaction:
                # Try as UUID
                try:
                    import uuid
                    transaction_uuid = uuid.UUID(transaction_id)
                    transaction = db.session.query(POSTransaction).filter(
                        POSTransaction.id == transaction_uuid
                    ).first()
                except ValueError:
                    pass
            
            if transaction:
                logger.info(f"POS transaction {transaction_id} retrieved successfully")
                return transaction
            else:
                logger.warning(f"POS transaction {transaction_id} not found")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving POS transaction {transaction_id}: {e}")
            return None

    @staticmethod
    def void_transaction(transaction_id, reason=None):
        """Void a POS transaction."""
        try:
            transaction = POSService.get_transaction(transaction_id)
            
            if not transaction:
                return {
                    "success": False,
                    "error": "Transaction not found"
                }
            
            if transaction.status == "voided":
                return {
                    "success": False,
                    "error": "Transaction already voided"
                }
            
            if transaction.status != "completed":
                return {
                    "success": False,
                    "error": "Only completed transactions can be voided"
                }
            
            # Update transaction status
            transaction.status = "voided"
            transaction.voided_at = datetime.utcnow()
            transaction.void_reason = reason or "Voided by admin"
            
            # Restore inventory if order exists
            if transaction.order_id:
                order = Order.query.get(transaction.order_id)
                if order:
                    for item in order.items:
                        product = Product.query.get(item.product_id)
                        if product:
                            product.stock += item.quantity
                    
                    # Mark order as cancelled
                    order.order_status = "CANCELLED"
            
            db.session.commit()
            
            logger.info(f"POS transaction {transaction_id} voided successfully")
            return {
                "success": True,
                "message": "Transaction voided successfully",
                "transaction": transaction.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error voiding POS transaction {transaction_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
