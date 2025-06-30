"""
Point of Sale (POS) Service for handling in-store transactions.
"""
import logging
from backend.database import db
from backend.services.exceptions import NotFoundException, ValidationException, ServiceError

from ..models import db, Order, OrderItem, Product, User
from .inventory_service import InventoryService
from .order_service import OrderService
from .pdf_service import PDFService
from .exceptions import InsufficientStockException


logger = logging.getLogger(__name__)

class PosService:
    """Service for handling Point of Sale transactions."""

    def __init__(self):
        self.inventory_service = InventoryService()
        self.order_service = OrderService()
        self.pdf_service = PDFService()

    def process_pos_sale(self, sale_data):
        """
        Processes a Point-of-Sale transaction.
        - Validates inventory
        - Creates an order
        - Processes payment (mocked)
        - Adjusts inventory
        - Generates a receipt (mocked)
        """
        customer_id = sale_data.get('customer_id')
        items = sale_data.get('items', []) # Expects a list of {'product_id': x, 'quantity': y}

        # Step 1: Validate that there is enough stock for all items in the sale.
        for item_data in items:
            if not self.inventory_service.check_stock(item_data['product_id'], item_data['quantity']):
                product = Product.query.get(item_data['product_id'])
                raise InsufficientStockException(f"Not enough stock for product: {product.name}")

        # Step 2: Calculate total and create the Order object.
        user = User.query.get(customer_id) if customer_id else None
        
        total_amount = 0
        order_items = []
        for item_data in items:
            product = Product.query.get(item_data['product_id'])
            quantity = item_data['quantity']
            item_total = product.price * quantity
            total_amount += item_total
            order_items.append(OrderItem(product_id=product.id, quantity=quantity, price=product.price))

        new_order = Order(
            user_id=customer_id,
            total_amount=total_amount,
            status='COMPLETED', # POS orders are considered completed immediately.
            items=order_items
        )

        # Step 3: Process the payment.
        # THIS IS A MOCK. Replace with actual POS payment integration (e.g., Stripe Terminal).
        payment_successful = self._process_pos_payment(total_amount, sale_data.get("payment_details"))
        
        if not payment_successful:
            return {"success": False, "error": "Payment processing failed."}
            
        new_order.payment_status = 'PAID'
        db.session.add(new_order)
        db.session.commit()

        # Step 4: Adjust inventory levels now that the sale is confirmed.
        for item_data in items:
            self.inventory_service.decrease_stock(item_data['product_id'], item_data['quantity'])

        # Step 5: Generate a receipt for the customer.
        # This is a mock; it would ideally generate a PDF or send a digital receipt.
        receipt_url = self.pdf_service.generate_receipt_for_order(new_order.id)
        
        db.session.commit()

        return {"success": True, "order_id": new_order.id, "receipt_url": receipt_url}

    def _process_pos_payment(self, amount, payment_details):
        """Mock POS payment processing. In a real app, this would interact with a payment terminal SDK."""
        print(f"Processing POS payment of {amount} with details: {payment_details}")
        return True # Assume success for this mock.

    @staticmethod
    def create_transaction(transaction_data):
        """Create a POS transaction."""
        # TODO: Implement POS transaction logic
        # This should handle:
        # - Inventory checks
        # - Payment processing
        # - Order creation
        # - Receipt generation
        
        logger.info(f"POS transaction requested: {transaction_data}")
        
        # Placeholder implementation
        class MockTransaction:
            def __init__(self, data):
                self.id = 1
                self.data = data
                
            def to_dict(self):
                return {
                    'id': self.id,
                    'status': 'completed',
                    'message': 'Transaction processed successfully'
                }
        
        return MockTransaction(transaction_data)
    
    @staticmethod
    def get_transaction(transaction_id):
        """Get a POS transaction by ID."""
        # TODO: Implement transaction retrieval logic
        logger.info(f"POS transaction {transaction_id} requested")
        return None
    
    @staticmethod
    def void_transaction(transaction_id):
        """Void a POS transaction."""
        # TODO: Implement transaction voiding logic
        logger.info(f"POS transaction {transaction_id} void requested")
        return True
