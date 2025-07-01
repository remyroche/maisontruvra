import logging
from flask import current_app, render_template
from backend.celery_worker import celery
from backend.extensions import cache, db
import os
from playwright.sync_api import sync_playwright

# Import all necessary services and models
from backend.services.passport_service import PassportService
from backend.models import B2BUser, User
from backend.models.invoice_models import Invoice
from backend.models.order_models import Order
from backend.services.monitoring_service import MonitoringService

from .services.order_service import OrderService
from .services.b2b_service import B2BService
from .services.invoice_service import InvoiceService
from .services.inventory_service import InventoryService

from backend.services.invoice_service import generate_invoice_pdf_for_order, generate_invoice_pdf_for_b2b_order
from backend.services.email_service import EmailService
from backend.services.notification_service import notify_user_of_loyalty_points

logger = logging.getLogger(__name__)

# --- Task Decorator Definitions ---
# A standard decorator for resilient, one-off tasks (e.g., triggered by user action)
def resilient_task(**kwargs):
    """A factory for resilient, one-off task decorators."""
    default_options = {
        'bind': True,
        'autoretry_for': (Exception,),
        'retry_kwargs': {'max_retries': 3, 'countdown': 5},
        'retry_backoff': True,
        'soft_time_limit': 300,  # 5 minutes
        'time_limit': 600        # 10 minutes
    }
    return celery.task(**default_options, **kwargs)

@celery_app.task(name='tasks.process_order_payment')
def process_order_payment(order_id):
    """
    Tâche Celery pour traiter le paiement d'une commande de manière asynchrone.
    """
    try:
        # La logique de traitement du paiement irait ici
        logger.info(f"Processing payment for order {order_id}...")
        # Simuler le traitement
        import time
        time.sleep(10) 
        # Mettre à jour le statut de la commande
        order = OrderService.get_order_by_id(order_id)
        if order:
            OrderService.update_order_status(order_id, 'PAID')
            logger.info(f"Payment for order {order_id} processed successfully.")
            # Envoyer la confirmation de paiement
            send_async_email.delay(order.user.email, "Payment Confirmation", "payment_confirmation.html", order=order)
        else:
            logger.error(f"Order {order_id} not found for payment processing.")
    except Exception as e:
        logger.error(f"Failed to process payment for order {order_id}: {e}", exc_info=True)


@celery_app.task(name='tasks.process_b2b_quick_order_task', bind=True, max_retries=3, default_retry_delay=60)
def process_b2b_quick_order_task(self, b2b_user_id, file_content):
    """
    Tâche Celery pour traiter une commande rapide B2B à partir d'un contenu de fichier CSV.
    """
    logger.info(f"Starting B2B quick order processing for user {b2b_user_id}.")
    b2b_user = B2BService.get_b2b_user_by_id(b2b_user_id)
    if not b2b_user:
        logger.error(f"B2B User with ID {b2b_user_id} not found. Aborting task.")
        return

    items_to_order = []
    errors = []
    try:
        # Utiliser io.StringIO pour lire la chaîne de contenu comme un fichier
        csv_file = io.StringIO(file_content)
        # Ignorer l'en-tête s'il y en a un
        next(csv_file, None)
        reader = csv.reader(csv_file)
        
        for i, row in enumerate(reader):
            line_num = i + 2  # +1 pour l'index 0, +1 pour l'en-tête
            if not row or len(row) < 2:
                errors.append(f"Ligne {line_num}: Ligne vide ou mal formatée.")
                continue
            
            sku, quantity_str = row[0].strip(), row[1].strip()
            
            try:
                quantity = int(quantity_str)
                if quantity <= 0:
                    raise ValueError()
                items_to_order.append({'sku': sku, 'quantity': quantity})
            except (ValueError, TypeError):
                errors.append(f"Ligne {line_num}: Quantité invalide '{quantity_str}' pour le SKU '{sku}'.")

        if errors:
            # Si des erreurs de formatage sont trouvées, notifier l'utilisateur et arrêter.
            raise ValueError("Erreurs de validation dans le fichier CSV.")

        # Appeler la logique de service pour créer la commande
        order = B2BService.create_order_from_items(b2b_user_id, items_to_order)
        
        # Envoyer un email de succès
        send_async_email.delay(
            recipient=b2b_user.user.email,
            subject="Votre commande rapide B2B a été créée avec succès",
            template="b2b_quick_order_success.html",
            order_id=order.id,
            total=order.total
        )
        logger.info(f"B2B quick order {order.id} processed successfully for user {b2b_user_id}.")

    except ValueError as e:
        # Gérer les erreurs de validation (CSV mal formaté, etc.)
        logger.error(f"Validation error in B2B quick order for user {b2b_user_id}: {e}. Errors: {errors}", exc_info=True)
        send_async_email.delay(
            recipient=b2b_user.user.email,
            subject="Échec du traitement de votre commande rapide B2B",
            template="b2b_quick_order_failure.html",
            error_list=errors,
            error_message=str(e)
        )
    except Exception as e:
        # Gérer les autres erreurs (ex: base de données, indisponibilité du service)
        logger.error(f"Failed to process B2B quick order for user {b2b_user_id}: {e}", exc_info=True)
        try:
            # Tenter une nouvelle exécution
            raise self.retry(exc=e)
        except self.MaxRetriesExceededError:
            # Si toutes les tentatives échouent, notifier l'utilisateur
            send_async_email.delay(
                recipient=b2b_user.user.email,
                subject="Échec du traitement de votre commande rapide B2B",
                template="b2b_quick_order_failure.html",
                error_message="Une erreur interne nous a empêchés de traiter votre commande. Veuillez réessayer plus tard ou contacter le support."
            )
            
@celery_app.task(name='tasks.fulfill_order', bind=True, max_retries=3, default_retry_delay=300)
def fulfill_order_task(self, order_id):
    """
    Tâche Celery pour exécuter une commande : alloue les articles, génère une facture,
    met à jour le statut et notifie le client.
    """
    logger.info(f"Starting fulfillment for order {order_id}...")
    try:
        # 1. Récupérer la commande
        order = OrderService.get_order_by_id(order_id)
        if not order:
            logger.error(f"Fulfillment failed: Order {order_id} not found.")
            return  # Tâche terminée, pas de nouvelle tentative

        # 2. Vérifier si la commande peut être traitée (par exemple, si elle est payée)
        if order.status not in ['PAID', 'PROCESSING']:
            logger.warning(f"Skipping fulfillment for order {order_id} with status '{order.status}'.")
            return

        # 3. Allouer l'inventaire
        logger.info(f"Allocating inventory for order {order_id}...")
        InventoryService.allocate_items_for_order(order_id)
        logger.info(f"Inventory allocated for order {order_id}.")

        # 4. Générer la facture
        logger.info(f"Generating invoice for order {order_id}...")
        invoice = InvoiceService.generate_invoice_for_order(order_id)
        logger.info(f"Invoice {invoice.id} generated for order {order_id}.")

        # 5. Mettre à jour le statut de la commande à 'Expédiée'
        OrderService.update_order_status(order_id, 'SHIPPED')
        logger.info(f"Order {order_id} status updated to SHIPPED.")

        # 6. Envoyer une notification d'expédition au client
        send_async_email.delay(
            recipient=order.user.email,
            subject=f"Votre commande Maison Truvra #{order.id} a été expédiée !",
            template="order_shipped.html",  # Assumer que ce template existe
            order=order.to_dict(),  # Passer les données de la commande au template
            tracking_number="XYZ123456789"  # Un numéro de suivi factice
        )
        logger.info(f"Shipping notification enqueued for order {order_id}.")

    except Exception as e:
        logger.error(f"An error occurred during fulfillment for order {order_id}: {e}", exc_info=True)
        # Tenter une nouvelle exécution en cas d'erreur (ex: verrouillage de la base de données, service externe indisponible)
        raise self.retry(exc=e)

# A standard decorator for scheduled (beat) tasks
def scheduled_task(**kwargs):
    """A factory for scheduled (beat) task decorators."""
    default_options = {
        'bind': True,
        'soft_time_limit': 1800, # 30 minutes
        'time_limit': 3600       # 1 hour
    }
    return celery.task(**default_options, **kwargs)


# --- Task Definitions ---

@resilient_task()
def send_email_task(self, recipient, subject, template_name, context):
    """Celery task to send an email asynchronously by calling the EmailService."""
    logger.info(f"Executing task id {self.request.id} to send email to {recipient}")
    with current_app.app_context():
        EmailService.send_email_immediately(recipient, subject, template_name, context)


@resilient_task()
def generate_invoice_pdf_task(self, order_id):
    """Celery task to generate a PDF invoice by calling the InvoiceService."""
    logger.info(f"Executing invoice generation task id {self.request.id} for order {order_id}")
    from backend.services.invoice_service import InvoiceService
    with current_app.app_context():
        InvoiceService.generate_pdf(order_id)
    logger.info(f"Successfully generated invoice for order {order_id}")

@celery.task(name='tasks.send_back_in_stock_notifications')
def send_back_in_stock_email_task(user_ids, product_id):
    """Sends notification emails to a list of users for a specific product."""
    from backend.models.product_models import Product
    with current_app.app_context():
        product = Product.query.get(product_id)
        if not product:
            return

        users = User.query.filter(User.id.in_(user_ids)).all()
        for user in users:
            context = {"user_name": user.first_name, "product_name": product.name, "product_url": f"/products/{product.slug}"}
            EmailService.send_email_immediately(
                recipient=user.email,
                subject=f"It's Back! {product.name} is now in stock",
                template_name='emails/back_in_stock_notification.html',
                context=context
            )

@celery.task
def generate_invoice_for_order_task(order_id):
    generate_invoice_pdf_for_order(order_id)

@celery.task
def generate_invoice_for_b2b_order_task(order_id):
    generate_invoice_pdf_for_b2b_order(order_id)

@celery.task
def send_order_confirmation_email_task(order_id):
    EmailService.send_order_confirmation_email(order_id)

@celery.task
def send_b2b_order_confirmation_email_task(order_id):
    EmailService.send_b2b_order_confirmation_email(order_id)
    
@celery.task
def notify_user_of_loyalty_points_task(user_id, points):
    notify_user_of_loyalty_points(user_id, points)

@celery.task
def send_password_reset_email_task(user_id, token, is_b2b=False):
    # You need to fetch user object here before passing to service
    from backend.models.user_models import User
    from backend.models.b2b_models import B2BUser
    user = B2BUser.query.get(user_id) if is_b2b else User.query.get(user_id)
    if user:
        EmailService.send_password_reset_email(user, token, is_b2b)

@celery.task
def send_2fa_status_change_email_task(user_id, enabled):
    from backend.models.user_models import User
    user = User.query.get(user_id)
    if user:
        EmailService.send_2fa_status_change_email(user, enabled)

@celery.task
def send_b2b_account_approved_email_task(b2b_user_id):
    from backend.models.b2b_models import B2BUser
    user = B2BUser.query.get(b2b_user_id)
    if user:
        EmailService.send_b2b_account_approved_email(user)

@celery.task
def send_security_alert_email_task(user_id, ip_address):
    from backend.models.user_models import User
    user = User.query.get(user_id)
    if user:
        EmailService.send_security_alert_email(user, ip_address)

@celery.task
def send_back_in_stock_notification_task(user_id, product_id):
    from backend.models.user_models import User
    from backend.models.product_models import Product
    user = User.query.get(user_id)
    product = Product.query.get(product_id)
    if user and product:
        EmailService.send_back_in_stock_email(user, product)

@celery.task
def send_order_shipped_email_task(order_id, tracking_link, tracking_number):
    from backend.models.order_models import Order
    order = Order.query.get(order_id)
    if order:
        EmailService.send_order_shipped_email(order, tracking_link, tracking_number)

@celery.task
def send_order_cancelled_email_task(order_id):
    from backend.models.order_models import Order
    order = Order.query.get(order_id)
    if order:
        EmailService.send_order_cancelled_email(order)

@celery.task(name='tasks.generate_invoice_pdf', bind=True, max_retries=3, default_retry_delay=60)
def generate_invoice_pdf_task(self, invoice_id: int):
    """
    Tâche Celery pour générer un fichier PDF pour une facture en utilisant Playwright.
    """
    logger.info(f"Début de la génération du PDF pour la facture ID: {invoice_id}")
    
    invoice = db.session.get(Invoice, invoice_id)
    if not invoice:
        logger.error(f"Tâche de génération de PDF : Facture {invoice_id} non trouvée. Abandon.")
        return

    order = invoice.order
    if not order:
        logger.error(f"Tâche de génération de PDF : Commande pour la facture {invoice_id} non trouvée. Abandon.")
        invoice.status = 'generation_failed'
        db.session.commit()
        return

    try:
        # --- Préparation du contexte pour le template ---
        template_name = 'non-email/b2b_invoice.html' if order.user.is_b2b else 'non-email/b2c_invoice.html'
        context = {
            'order': order,
            'invoice': invoice,
            'customer': order.user,
            'billing_address': order.billing_address,
            'shipping_address': order.shipping_address,
            'company': {
                'legal_status': current_app.config.get('COMPANY_LEGAL_STATUS', 'SAS'),
                'siret': current_app.config.get('COMPANY_SIRET', '123 456 789 00010'),
                'capital': current_app.config.get('COMPANY_CAPITAL', '10,000 €'),
                'address': current_app.config.get('COMPANY_ADDRESS', '123 Rue de la République, 75001 Paris, France'),
                'vat_number': current_app.config.get('COMPANY_VAT_NUMBER', 'FR00123456789'),
                'email': current_app.config.get('COMPANY_EMAIL', 'contact@maisontruvra.com')
            }
        }
        
        # Rendu du template HTML
        html_string = render_template(template_name, **context)

        # --- Génération du PDF avec Playwright ---
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.set_content(html_string, wait_until='networkidle')
            pdf_bytes = page.pdf(
                format='A4',
                print_background=True,
                margin={'top': '20mm', 'bottom': '20mm', 'left': '15mm', 'right': '15mm'}
            )
            browser.close()

        # --- Sauvegarde du fichier PDF ---
        # Il est recommandé d'utiliser un stockage cloud (ex: S3) en production.
        storage_path = current_app.config.get("INVOICE_STORAGE_PATH", "./invoices")
        if not os.path.exists(storage_path):
            os.makedirs(storage_path)

        pdf_filename = f"{invoice.invoice_number}.pdf"
        full_path = os.path.join(storage_path, pdf_filename)
        
        with open(full_path, 'wb') as f:
            f.write(pdf_bytes)

        # --- Mise à jour de l'enregistrement de la facture ---
        invoice.pdf_url = full_path # ou l'URL du stockage cloud
        invoice.status = 'generated'
        db.session.commit()

        MonitoringService.log_info(f"PDF pour la facture {invoice.id} généré avec succès et sauvegardé dans {full_path}", "InvoiceTask")
        logger.info(f"Génération du PDF réussie pour la facture ID: {invoice_id}")
        
        # Optionnel : lancer une autre tâche pour envoyer l'email avec le PDF en pièce jointe
        # from . import send_invoice_email_task
        # send_invoice_email_task.delay(invoice.id)

    except Exception as exc:
        logger.error(f"Échec de la génération du PDF pour la facture {invoice_id}: {exc}", exc_info=True)
        invoice.status = 'generation_failed'
        db.session.commit()
        MonitoringService.log_error(f"Échec de la génération du PDF pour la facture {invoice_id}", "InvoiceTask")
        # Relancer la tâche en cas d'erreur (ex: problème réseau)
        raise self.retry(exc=exc)

@resilient_task()
def send_tier_upgrade_email_task(self, user_id, new_tier_name):
    """Celery task to send tier upgrade notification email."""
    logger.info(f"Executing tier upgrade email task for user {user_id}")
    with current_app.app_context():
        user = User.query.get(user_id)
        if not user:
            logger.error(f"User {user_id} not found for tier upgrade email")
            return
        
        context = {
            'user_name': user.first_name,
            'new_tier': new_tier_name
        }
        EmailService.send_email_immediately(
            recipient=user.email,
            subject=f"Congratulations! You've been upgraded to {new_tier_name}",
            template_name='emails/tier_upgrade_notification.html',
            context=context
        )

@resilient_task()
def generate_passport_pdf_task(self, passport_id):
    """Celery task to generate a product passport PDF by calling the PassportService."""
    logger.info(f"Executing passport generation task id {self.request.id} for passport {passport_id}")
    with current_app.app_context():
        PassportService.generate_pdf(passport_id)
    logger.info(f"Successfully generated passport for {passport_id}")


@resilient_task()
def finalize_order_task(self, order_id):
    """
    Orchestration task to finalize an order after payment.
    It calls other tasks for invoice generation and confirmation emails.
    """
    logger.info(f"Executing 'finalize_order_task' for order {order_id}")
    with current_app.app_context():
        order = Order.query.get(order_id)
        if not order:
            logger.error(f"Order {order_id} not found in finalize_order_task.")
            return

        # Queue subsequent, independent jobs.
        generate_invoice_pdf_task.delay(order_id)
        
        user = order.user or order.b2b_user
        if not user:
             logger.error(f"No user found for order {order_id}.")
             return

        email_context = {'order_id': order.id, 'customer_name': user.first_name}
        send_email_task.delay(
            recipient=user.email,
            subject=f"Your Order Confirmation #{order_id}",
            template_name='emails/order_confirmation.html',
            context=email_context
        )

@resilient_task()
def fulfill_order_task(self, order_id):
    """
    Celery task to trigger the order fulfillment process by calling the OrderService.
    """
    logger.info(f"Executing fulfillment task for order {order_id}")
    from backend.services.order_service import OrderService
    with current_app.app_context():
        OrderService.fulfill_order(order_id)


# --- Scheduled Tasks ---

@scheduled_task(name='tasks.clear_application_cache')
def clear_application_cache(self):
    """
    A periodic task to clear the entire Flask cache as a safety net.
    """
    with current_app.app_context():
        try:
            cache.clear()
            logger.info("Successfully cleared the application cache.")
            return "Cache cleared successfully."
        except Exception as e:
            logger.error(f"Failed to clear application cache: {e}")
            raise

@scheduled_task(name='tasks.update_all_user_tiers')
def update_all_user_tiers(self):
    """
    A periodic task that calls the loyalty service to recalculate and update
    the loyalty tier for all users (B2C and B2B).
    This should be run daily.
    """
    with current_app.app_context():
        logger.info("Starting scheduled user tier recalculation task.")
        try:
            from backend.services.loyalty_service import LoyaltyService
            # Assumes LoyaltyService has a method to update tiers for all users
            result_message = LoyaltyService.update_all_user_tiers_task()
            logger.info(f"Finished user tier recalculation task. Result: {result_message}")
            return result_message
        except Exception as e:
            logger.error(f"An error occurred during the scheduled tier recalculation: {e}", exc_info=True)
            raise

@scheduled_task(name='tasks.expire_loyalty_points')
def expire_loyalty_points_task(self):
    """Scheduled task to expire old loyalty points via LoyaltyService."""
    from backend.services.loyalty_service import LoyaltyService
    logger.info("Starting scheduled task: expire_loyalty_points_task")
    with current_app.app_context():
        count = LoyaltyService.expire_points_task()
    logger.info(f"Finished scheduled task: Expired {count} loyalty point transactions.")
    return f"Expired {count} loyalty point records."
