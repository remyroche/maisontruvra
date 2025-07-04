from flask import Blueprint, request, jsonify, g
from backend.services.b2b_service import B2BService
from backend.services.exceptions import NotFoundException
from backend.utils.decorators import (
    roles_required,
    api_resource_handler,
)
from backend.models.enums import B2BStatus
from backend.models.b2b_models import B2BPartnershipRequest, B2BTier
from backend.models.user_models import User
from backend.utils.input_sanitizer import InputSanitizer
from backend.services.audit_log_service import AuditLogService
from backend.extensions import limiter
from backend.schemas import (
    B2BAccountStatusUpdateSchema,
    B2BTierCreateSchema,
    B2BTierUpdateSchema,
    B2BTierSchema,
    B2BUserAssignTierSchema,
    QuoteUpdateSchema,
)


b2b_management_bp = Blueprint(
    "b2b_management_api", __name__, url_prefix="/admin/api/b2b"
)
b2b_service = B2BService()

# --- B2B Account Management ---


@b2b_management_bp.route("/", methods=["GET"])
@roles_required("Admin", "Manager", "Support")
def get_b2b_accounts():
    """Returns a list of all B2B accounts with their company-specific details."""
    accounts = b2b_service.get_all_b2b_accounts()
    return jsonify([acc.to_dict() for acc in accounts])


@b2b_management_bp.route("/b2b/applications", methods=["GET"])
def get_b2b_applications():
    """
    Retrieves a paginated list of B2B applications.
    C[R]UD - Read (List)
    """
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    status_filter = InputSanitizer.sanitize_input(
        request.args.get("status", "pending", type=str)
    )

    applications_page = B2BPartnershipRequest.query.filter_by(
        status=status_filter
    ).paginate(page=page, per_page=per_page, error_out=False)

    # Format for frontend data table compatibility
    return jsonify(
        {
            "applications": [app.to_dict() for app in applications_page.items],
            "total": applications_page.total,
            "page": applications_page.page,
            "pages": applications_page.pages,
        }
    )


@b2b_management_bp.route(
    "/b2b/applications/<int:application_id>/approve", methods=["POST"]
)
@roles_required("Admin", "Manager", "Support")
@limiter.limit("10 per minute")
def approve_b2b_application(application_id):
    """
    Approves a B2B application and converts the user to a B2B account.
    CR[U]D - Update
    """
    application = B2BPartnershipRequest.query.get_or_404(application_id)

    # The service layer handles the logic of creating the B2B account, setting tiers, etc.
    B2BService.approve_b2b_application(application)

    AuditLogService.log_action(
        user_id=g.user.id,  # Using g.user.id as roles_required ensures g.user is populated
        action="approve_b2b_application",
        details=f"Approved B2B application for '{application.contact_email}' (ID: {application.id}).",
    )

    return jsonify(
        {"message": f"B2B application for {application.contact_email} approved."}
    )


@b2b_management_bp.route(
    "/b2b/applications/<int:application_id>/reject", methods=["POST"]
)
@roles_required("Admin", "Manager", "Support")
@limiter.limit("10 per minute")
def reject_b2b_application(application_id):
    """
    Rejects a B2B application.
    CR[U]D - Update
    """
    application = B2BPartnershipRequest.query.get_or_404(application_id)
    data = request.get_json()
    rejection_reason = InputSanitizer.sanitize_input(
        data.get("reason", "Application did not meet requirements.")
    )

    B2BService.reject_b2b_application(application, reason=rejection_reason)

    AuditLogService.log_action(
        user_id=g.user.id,  # Using g.user.id as roles_required ensures g.user is populated
        action="reject_b2b_application",
        details=f"Rejected B2B application for '{application.contact_email}' (ID: {application.id}). Reason: {rejection_reason}",
    )

    return jsonify(
        {"message": f"B2B application for {application.contact_email} rejected."}
    )


@b2b_management_bp.route("/<int:user_id>/status", methods=["PUT"])
@roles_required("Admin", "Manager", "Support")
@api_resource_handler(
    model=User,
    request_schema=B2BAccountStatusUpdateSchema,
    ownership_exempt_roles=["Admin", "Manager", "Support"],
    cache_timeout=0,  # No caching for updates
)
def update_b2b_account_status(user_id):
    """Updates a B2B account's status (e.g., "approved", "rejected")."""
    new_status_str = g.validated_data["status"]
    new_status = B2BStatus(new_status_str)  # Convert string from validated_data to Enum

    B2BService.update_b2b_status(user_id, new_status)

    return None  # Return None to let api_resource_handler generate a default success message


# --- Tier Management ---


@b2b_management_bp.route("/tiers", methods=["POST"])
@roles_required("Admin", "Manager")
@api_resource_handler(
    model=B2BTier,
    request_schema=B2BTierCreateSchema,
    response_schema=B2BTierSchema,
    ownership_exempt_roles=["Admin", "Manager"],
    cache_timeout=0,  # No caching for creation
)
def create_tier():
    """Creates a new B2B pricing tier."""
    tier = b2b_service.create_tier(
        name=g.validated_data["name"],
        discount_percentage=g.validated_data["discount_percentage"],
        minimum_spend=g.validated_data.get("minimum_spend"),
    )
    return tier  # Return the created object for serialization by api_resource_handler


@b2b_management_bp.route("/tiers", methods=["GET"])
@roles_required("Admin", "Manager", "Support")
def get_all_tiers():
    """Retrieves all B2B pricing tiers."""
    tiers = b2b_service.get_all_tiers()
    return jsonify(
        [
            {
                "id": tier.id,
                "name": tier.name,
                "discount_percentage": str(tier.discount_percentage),
                "minimum_spend": str(tier.minimum_spend)
                if tier.minimum_spend
                else None,
            }
            for tier in tiers
        ]
    ), 200


@b2b_management_bp.route("/tiers/<int:tier_id>", methods=["PUT"])
@roles_required("Admin", "Manager")
@api_resource_handler(
    model=B2BTier,
    request_schema=B2BTierUpdateSchema,
    response_schema=B2BTierSchema,
    ownership_exempt_roles=["Admin", "Manager"],
    cache_timeout=0,  # No caching for updates
)
def update_tier(tier_id):
    """Updates an existing B2B pricing tier."""
    tier = b2b_service.update_tier(
        tier_id,
        name=g.validated_data.get("name"),
        discount_percentage=g.validated_data.get("discount_percentage"),
        minimum_spend=g.validated_data.get("minimum_spend"),
    )
    return tier  # Return the updated object for serialization by api_resource_handler


@b2b_management_bp.route("/users/<int:user_id>/assign-tier", methods=["POST"])
@roles_required("Admin", "Manager", "Support")
@api_resource_handler(
    model=User,
    request_schema=B2BUserAssignTierSchema,
    ownership_exempt_roles=["Admin", "Manager", "Support"],
    cache_timeout=0,  # No caching for updates
)
def assign_tier_to_user(user_id):
    """Assigns a tier to a B2B user."""
    b2b_service.assign_tier_to_b2b_user(user_id, g.validated_data["tier_id"])
    return None  # Return None to let api_resource_handler generate a default success message


# --- B2B Quote Management (Consolidated) ---


@b2b_management_bp.route("/quotes", methods=["GET"])
@admin_required
def get_all_quotes():
    """
    Retrieves all B2B quotes for the admin panel.
    """
    status = request.args.get("status")
    quotes = quote_service.get_all_quotes(status=status)
    return jsonify([q.to_dict() for q in quotes]), 200


@b2b_management_bp.route("/quotes/<int:quote_id>", methods=["GET"])
@admin_required
def get_quote_details(quote_id):
    """
    Retrieves the details of a single B2B quote.
    """
    try:
        quote = quote_service.get_quote_by_id(quote_id)
        return jsonify(quote.to_dict_detailed()), 200
    except NotFoundException as e:
        return jsonify({"error": str(e)}), 404


@b2b_management_bp.route("/quotes/<int:quote_id>", methods=["PUT"])
@admin_required
@api_resource_handler(request_schema=QuoteUpdateSchema)
def update_quote(validated_data, quote_id):
    """
    Updates a B2B quote (e.g., change status, add response).
    The decorator handles validation.
    """
    quote = quote_service.update_quote(quote_id, validated_data)
    return jsonify(quote.to_dict()), 200
