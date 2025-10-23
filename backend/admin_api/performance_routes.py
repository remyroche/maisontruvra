"""
Performance Monitoring Routes

This module provides admin routes for monitoring application performance,
including slow queries, endpoint performance, and optimization recommendations.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from ..utils.decorators import roles_required
from ..utils.performance_monitor import (
    get_slow_queries,
    clear_slow_queries,
    analyze_query_patterns
)
import logging

logger = logging.getLogger(__name__)

# Create a Blueprint for performance monitoring routes
performance_bp = Blueprint(
    "performance_bp", __name__, url_prefix="/api/admin/performance"
)


@performance_bp.route("/slow-queries", methods=["GET"])
@jwt_required()
@roles_required("Admin", "Manager")
def get_slow_queries_endpoint():
    """
    Get a list of slow queries that have been detected.
    """
    try:
        slow_queries = get_slow_queries()
        return jsonify({
            "status": "success",
            "data": {
                "slow_queries": slow_queries,
                "count": len(slow_queries)
            }
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving slow queries: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "Failed to retrieve slow queries"
        }), 500


@performance_bp.route("/slow-queries", methods=["DELETE"])
@jwt_required()
@roles_required("Admin")
def clear_slow_queries_endpoint():
    """
    Clear the slow queries list.
    """
    try:
        clear_slow_queries()
        return jsonify({
            "status": "success",
            "message": "Slow queries cleared successfully"
        }), 200
    except Exception as e:
        logger.error(f"Error clearing slow queries: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "Failed to clear slow queries"
        }), 500


@performance_bp.route("/analysis", methods=["GET"])
@jwt_required()
@roles_required("Admin", "Manager")
def get_performance_analysis():
    """
    Get performance analysis and optimization recommendations.
    """
    try:
        analysis = analyze_query_patterns()
        return jsonify({
            "status": "success",
            "data": analysis
        }), 200
    except Exception as e:
        logger.error(f"Error analyzing performance: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "Failed to analyze performance"
        }), 500


@performance_bp.route("/health", methods=["GET"])
@jwt_required()
@roles_required("Admin", "Manager")
def get_performance_health():
    """
    Get overall performance health status.
    """
    try:
        slow_queries = get_slow_queries()
        analysis = analyze_query_patterns()
        
        # Determine health status based on slow queries
        health_status = "healthy"
        if len(slow_queries) > 50:
            health_status = "critical"
        elif len(slow_queries) > 20:
            health_status = "warning"
        elif len(slow_queries) > 5:
            health_status = "caution"
        
        return jsonify({
            "status": "success",
            "data": {
                "health_status": health_status,
                "slow_queries_count": len(slow_queries),
                "recommendations_count": len(analysis.get("recommendations", [])),
                "last_updated": analysis.get("last_updated")
            }
        }), 200
    except Exception as e:
        logger.error(f"Error checking performance health: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "Failed to check performance health"
        }), 500