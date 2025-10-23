"""
Payment Service for handling Stripe payments and other payment methods.
"""

import logging
import stripe
from decimal import Decimal
from typing import Dict, Any, Optional

from backend.config import Config

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = Config.STRIPE_SECRET_KEY


class PaymentService:
    """Service for handling payment processing."""
    
    def __init__(self, logger):
        self.logger = logger
    
    def create_payment_intent(self, amount: Decimal, currency: str = "eur", 
                            metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a Stripe PaymentIntent for processing payments."""
        try:
            # Convert Decimal to cents for Stripe
            amount_cents = int(amount * 100)
            
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                metadata=metadata or {},
                automatic_payment_methods={
                    'enabled': True,
                },
            )
            
            self.logger.info(f"PaymentIntent created: {intent.id}")
            return {
                "success": True,
                "client_secret": intent.client_secret,
                "payment_intent_id": intent.id,
                "amount": amount,
                "currency": currency
            }
            
        except stripe.error.StripeError as e:
            self.logger.error(f"Stripe error creating PaymentIntent: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            self.logger.error(f"Error creating PaymentIntent: {e}")
            return {
                "success": False,
                "error": "Payment processing failed"
            }
    
    def confirm_payment_intent(self, payment_intent_id: str) -> Dict[str, Any]:
        """Confirm a Stripe PaymentIntent."""
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if intent.status == "succeeded":
                return {
                    "success": True,
                    "status": "succeeded",
                    "payment_intent_id": intent.id
                }
            elif intent.status == "requires_action":
                return {
                    "success": False,
                    "status": "requires_action",
                    "client_secret": intent.client_secret
                }
            else:
                return {
                    "success": False,
                    "status": intent.status,
                    "error": f"Payment failed with status: {intent.status}"
                }
                
        except stripe.error.StripeError as e:
            self.logger.error(f"Stripe error confirming PaymentIntent: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            self.logger.error(f"Error confirming PaymentIntent: {e}")
            return {
                "success": False,
                "error": "Payment confirmation failed"
            }
    
    def refund_payment(self, payment_intent_id: str, amount: Optional[Decimal] = None) -> Dict[str, Any]:
        """Refund a payment."""
        try:
            refund_params = {
                "payment_intent": payment_intent_id
            }
            
            if amount:
                refund_params["amount"] = int(amount * 100)  # Convert to cents
            
            refund = stripe.Refund.create(**refund_params)
            
            self.logger.info(f"Refund created: {refund.id}")
            return {
                "success": True,
                "refund_id": refund.id,
                "amount": Decimal(refund.amount) / 100,
                "status": refund.status
            }
            
        except stripe.error.StripeError as e:
            self.logger.error(f"Stripe error creating refund: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            self.logger.error(f"Error creating refund: {e}")
            return {
                "success": False,
                "error": "Refund failed"
            }
    
    def process_pos_payment(self, amount: Decimal, payment_method: str, 
                          payment_details: Dict[str, Any]) -> Dict[str, Any]:
        """Process a POS payment using Stripe Terminal or other methods."""
        try:
            if payment_method.lower() == "card":
                # For card payments, create a PaymentIntent
                return self.create_payment_intent(
                    amount=amount,
                    metadata={
                        "pos_transaction": "true",
                        "terminal_id": payment_details.get("terminal_id", "unknown")
                    }
                )
            elif payment_method.lower() == "cash":
                # For cash payments, we don't need Stripe
                return {
                    "success": True,
                    "payment_method": "cash",
                    "amount": amount,
                    "reference": f"CASH_{payment_details.get('terminal_id', 'unknown')}"
                }
            else:
                return {
                    "success": False,
                    "error": f"Unsupported payment method: {payment_method}"
                }
                
        except Exception as e:
            self.logger.error(f"Error processing POS payment: {e}")
            return {
                "success": False,
                "error": "POS payment processing failed"
            }
    
    def get_payment_methods(self) -> Dict[str, Any]:
        """Get available payment methods."""
        return {
            "success": True,
            "payment_methods": [
                {
                    "id": "card",
                    "name": "Credit/Debit Card",
                    "type": "stripe"
                },
                {
                    "id": "cash",
                    "name": "Cash",
                    "type": "pos"
                }
            ]
        }