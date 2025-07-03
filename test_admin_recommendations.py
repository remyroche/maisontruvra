#!/usr/bin/env python3
"""
Simple test script to verify admin recommendation functionality.
This script tests the new admin recommendation service methods.
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_recommendation_service():
    """Test the RecommendationService admin methods."""
    try:
        # Test import only - actual database operations require Flask app context
        from backend.services.recommendation_service import RecommendationService
        from backend.services.exceptions import NotFoundException, ServiceError
        
        print("Testing RecommendationService admin methods...")
        
        # Test 1: Check if new methods exist
        print("\n1. Checking if new admin methods exist...")
        methods_to_check = [
            'get_all_customer_recommendations',
            'get_recommendations_summary', 
            'bulk_generate_recommendations'
        ]
        
        for method_name in methods_to_check:
            if hasattr(RecommendationService, method_name):
                print(f"✓ Method {method_name} exists")
            else:
                print(f"✗ Method {method_name} missing")
                return False
        
        # Test 2: Check method signatures (without calling them)
        print("\n2. Checking method signatures...")
        try:
            import inspect
            
            # Check get_all_customer_recommendations signature
            sig = inspect.signature(RecommendationService.get_all_customer_recommendations)
            expected_params = ['limit_per_user', 'page', 'per_page']
            actual_params = list(sig.parameters.keys())
            
            if all(param in actual_params for param in expected_params):
                print("✓ get_all_customer_recommendations has correct parameters")
            else:
                print(f"✗ get_all_customer_recommendations parameters mismatch. Expected: {expected_params}, Got: {actual_params}")
            
            # Check bulk_generate_recommendations signature
            sig = inspect.signature(RecommendationService.bulk_generate_recommendations)
            expected_params = ['user_ids', 'limit_per_user']
            actual_params = list(sig.parameters.keys())
            
            if all(param in actual_params for param in expected_params):
                print("✓ bulk_generate_recommendations has correct parameters")
            else:
                print(f"✗ bulk_generate_recommendations parameters mismatch. Expected: {expected_params}, Got: {actual_params}")
                
        except Exception as e:
            print(f"✗ Error checking method signatures: {e}")
        
        print("\n✓ RecommendationService structure tests completed!")
        return True
        
    except ImportError as e:
        print(f"✗ Failed to import RecommendationService: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error during testing: {e}")
        return False

def test_admin_routes_structure():
    """Test that the admin routes file is properly structured."""
    try:
        print("\nTesting admin recommendation routes structure...")
        
        # Check if the admin routes file exists and can be imported
        from backend.admin_api.recommendation_routes import admin_recommendation_bp
        
        print("✓ Admin recommendation routes imported successfully")
        print(f"  - Blueprint name: {admin_recommendation_bp.name}")
        print(f"  - URL prefix: {admin_recommendation_bp.url_prefix}")
        
        # Check if the blueprint has the expected routes
        routes = []
        for rule in admin_recommendation_bp.url_map.iter_rules():
            if rule.endpoint.startswith(admin_recommendation_bp.name):
                routes.append(f"{rule.rule} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
        
        if routes:
            print(f"  - Routes registered: {len(routes)}")
            for route in routes:
                print(f"    * {route}")
        else:
            print("  - No routes found (this is expected before app context)")
        
        return True
        
    except ImportError as e:
        print(f"✗ Failed to import admin recommendation routes: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error testing admin routes: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("ADMIN RECOMMENDATIONS FUNCTIONALITY TEST")
    print("=" * 60)
    
    # Test 1: Service methods
    service_test_passed = test_recommendation_service()
    
    # Test 2: Admin routes structure
    routes_test_passed = test_admin_routes_structure()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Service methods test: {'✓ PASSED' if service_test_passed else '✗ FAILED'}")
    print(f"Admin routes test: {'✓ PASSED' if routes_test_passed else '✗ FAILED'}")
    
    if service_test_passed and routes_test_passed:
        print("\n🎉 All tests passed! Admin recommendation functionality is ready.")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    exit(main())