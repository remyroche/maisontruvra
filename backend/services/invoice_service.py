import os
import logging
from datetime import datetime
from flask import render_template, current_app

from backend.database import db
from backend.models.b2b_models import B2BOrder
from backend.models.invoice_models import Invoice
from backend.models.order_models import Order, OrderStatus
from backend.services.pdf_service import create_invoice_pdf
from backend.services.monitoring_service import MonitoringService

logger = logging.getLogger(__name__)

class InvoiceService:
    """
    Service pour la gestion des factures.
    Sépare la création de l'enregistrement de la facture de la génération du fichier PDF.
    """

    @staticmethod
    def _generate_invoice_number(prefix: str = "INV") -> str:
        """Génère un numéro de facture unique basé sur la date et un compteur."""
        today = datetime.utcnow()
        # Cherche la dernière facture du mois en cours pour incrémenter le compteur
        last_invoice = Invoice.query.filter(
            db.func.strftime('%Y-%m', Invoice.created_at) == today.strftime('%Y-%m')
        ).order_by(Invoice.id.desc()).first()
        
        count = 1
        if last_invoice and last_invoice.invoice_number:
            try:
                # Extrait le dernier numéro de la séquence
                count = int(last_invoice.invoice_number.split('-')[-1]) + 1
            except (ValueError, IndexError):
                logger.warning(f"Impossible d'analyser le numéro de facture : {last_invoice.invoice_number}. Réinitialisation du compteur.")
                
        return f"{prefix}-{today.strftime('%Y%m')}-{count:04d}"

    @staticmethod
    def create_and_dispatch_invoice_for_order(order_id: int):
        """
        Crée un enregistrement de facture pour une commande et lance une tâche Celery
        pour générer le fichier PDF en arrière-plan.
        """
        order = db.session.get(Order, order_id)
        if not order:
            logger.error(f"Impossible de créer la facture : commande {order_id} non trouvée.")
            raise ValueError(f"Commande {order_id} non trouvée.")

        if order.invoice:
            logger.warning(f"La commande {order_id} a déjà une facture associée (ID: {order.invoice.id}).")
            return order.invoice

        try:
            # Déterminer le préfixe et le type de document
            prefix = "INV" if order.user.is_b2b else "RECU"
            invoice_number = InvoiceService._generate_invoice_number(prefix)

            # Créer l'enregistrement de la facture dans la base de données
            new_invoice = Invoice(
                invoice_number=invoice_number,
                user_id=order.user_id,
                order_id=order.id,
                total_amount=order.total_cost, # Assumant que le modèle Order a un 'total_cost'
                status='pending_generation', # Statut initial
                pdf_url=None # Le PDF n'est pas encore créé
            )
            db.session.add(new_invoice)
            db.session.commit()

            # Lancer la tâche Celery pour la génération du PDF
            from backend.tasks import generate_invoice_pdf_task
            generate_invoice_pdf_task.delay(new_invoice.id)

            MonitoringService.log_info(
                f"Facture {new_invoice.id} créée. Génération du PDF mise en file d'attente.",
                "InvoiceService"
            )
            logger.info(f"Facture {new_invoice.id} pour la commande {order_id} envoyée à la file d'attente de génération.")
            
            return new_invoice

        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la création de la facture pour la commande {order_id}: {e}", exc_info=True)
            MonitoringService.log_error(f"Échec de la création de la facture pour la commande {order_id}", "InvoiceService")
            raise

