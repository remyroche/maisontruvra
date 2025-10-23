"""
Performance Monitoring Utilities

This module provides utilities for monitoring and optimizing database query performance.
"""

import time
import logging
from functools import wraps
from sqlalchemy import event
from sqlalchemy.engine import Engine
from ..extensions import db

logger = logging.getLogger(__name__)

# Track slow queries
slow_queries = []


@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log the start time of each query."""
    context._query_start_time = time.time()


@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log slow queries and their execution time."""
    total = time.time() - context._query_start_time
    
    # Log queries that take more than 100ms
    if total > 0.1:
        slow_queries.append({
            'statement': statement,
            'parameters': parameters,
            'duration': total
        })
        logger.warning(f"Slow query detected: {total:.3f}s - {statement[:100]}...")


def monitor_query_performance(threshold=0.1):
    """
    Decorator to monitor query performance.
    
    Args:
        threshold (float): Time threshold in seconds to log slow queries
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            if execution_time > threshold:
                logger.warning(
                    f"Slow function {func.__name__} took {execution_time:.3f}s "
                    f"(threshold: {threshold}s)"
                )
            
            return result
        return wrapper
    return decorator


def get_slow_queries():
    """Get a list of slow queries that have been detected."""
    return slow_queries


def clear_slow_queries():
    """Clear the slow queries list."""
    global slow_queries
    slow_queries = []


def analyze_query_patterns():
    """
    Analyze query patterns to identify optimization opportunities.
    
    Returns:
        dict: Analysis results with recommendations
    """
    if not slow_queries:
        return {"message": "No slow queries detected"}
    
    # Group by query pattern
    patterns = {}
    for query in slow_queries:
        # Extract table name from query
        statement = query['statement'].lower()
        if 'from' in statement:
            table_start = statement.find('from') + 5
            table_end = statement.find(' ', table_start)
            if table_end == -1:
                table_end = statement.find('\n', table_start)
            if table_end == -1:
                table_end = len(statement)
            
            table = statement[table_start:table_end].strip()
            if table not in patterns:
                patterns[table] = []
            patterns[table].append(query)
    
    # Generate recommendations
    recommendations = []
    for table, queries in patterns.items():
        avg_duration = sum(q['duration'] for q in queries) / len(queries)
        max_duration = max(q['duration'] for q in queries)
        
        recommendations.append({
            'table': table,
            'query_count': len(queries),
            'avg_duration': avg_duration,
            'max_duration': max_duration,
            'suggestion': f"Consider adding indexes or eager loading for {table}"
        })
    
    return {
        'total_slow_queries': len(slow_queries),
        'patterns': patterns,
        'recommendations': recommendations
    }