from flask import Blueprint, request, jsonify, g
from backend.services.blog_service import BlogService
from backend.utils.decorators import roles_required, api_resource_handler
from backend.extensions import cache
from backend.models.blog_models import BlogCategory, BlogPost
from backend.schemas import BlogCategorySchema, BlogPostSchema

blog_management_bp = Blueprint('blog_management_bp', __name__, url_prefix='/api/admin/blog')

# Category Routes
@blog_management_bp.route('/categories', methods=['GET'])
@roles_required('Admin', 'Manager', 'Editor')
def get_categories():
    categories = BlogService.get_all_categories()
    return jsonify([category.to_dict() for category in categories])

@blog_management_bp.route('/categories', methods=['POST'])
@api_resource_handler(BlogCategory, schema=BlogCategorySchema(), check_ownership=False)
@roles_required('Admin', 'Manager')
def create_category():
    category = BlogService.create_category(g.validated_data['name'])
    cache.delete_memoized(BlogService.get_all_categories)
    return jsonify(category.to_dict()), 201

@blog_management_bp.route('/categories/<int:category_id>', methods=['PUT'])
@api_resource_handler(BlogCategory, schema=BlogCategorySchema(), check_ownership=False)
@roles_required('Admin', 'Manager')
def update_category(category_id):
    category = BlogService.update_category(category_id, g.validated_data['name'])
    cache.delete_memoized(BlogService.get_all_categories)
    return jsonify(category.to_dict())

@blog_management_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@api_resource_handler(BlogCategory, check_ownership=False)
@roles_required('Admin', 'Manager')
def delete_category(category_id):
    BlogService.delete_category(category_id)
    cache.delete_memoized(BlogService.get_all_categories)
    return jsonify({'message': 'Category deleted successfully'})

# Blog Post Routes
@blog_management_bp.route('/posts', methods=['GET'])
@roles_required('Admin', 'Manager', 'Editor')
def get_posts():
    include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
    posts = BlogService.get_all_posts(include_deleted=include_deleted)
    return jsonify([post.to_dict() for post in posts])

@blog_management_bp.route('/posts', methods=['POST'])
@api_resource_handler(BlogPost, schema=BlogPostSchema(), check_ownership=False)
@roles_required('Admin', 'Manager', 'Editor')
def create_post():
    post = BlogService.create_post(g.validated_data)
    # Invalidate cache for the list of posts
    cache.delete('view//api/blog/posts')
    return jsonify(post.to_dict()), 201

@blog_management_bp.route('/posts/<int:post_id>', methods=['PUT'])
@api_resource_handler(BlogPost, schema=BlogPostSchema(), check_ownership=False)
@roles_required('Admin', 'Manager', 'Editor')
def update_post(post_id):
    post = BlogService.update_post(post_id, g.validated_data)
    if not post:
        return jsonify({"error": "Post not found or update failed"}), 404
        
    # Invalidate relevant caches
    cache.delete('view//api/blog/posts') # Clear the list cache
    cache.delete('view//api/blog/posts/{}'.format(post.slug)) # FIX: Use post.slug
    return jsonify(post.to_dict())

@blog_management_bp.route('/posts/<int:post_id>', methods=['GET'])
@api_resource_handler(BlogPost, check_ownership=False)
@roles_required('Admin', 'Manager', 'Editor')
def get_post(post_id):
    # Post is already validated and available as g.blog_post
    return jsonify(g.blog_post.to_dict())

@blog_management_bp.route('/posts/<int:post_id>', methods=['DELETE'])
@api_resource_handler(BlogPost, check_ownership=False)
@roles_required('Admin', 'Manager')
def delete_post(post_id):
    # Post is already validated and available as g.blog_post
    post_slug = g.blog_post.slug
    
    # Now, delete the post
    BlogService.delete_post(post_id)
    
    # Invalidate relevant caches
    cache.delete('view//api/blog/posts') # Clear the list cache
    cache.delete('view//api/blog/posts/{}'.format(post_slug)) # Clear the individual post cache
    
    return jsonify({"message": "Post deleted successfully"})

@blog_management_bp.route('/posts/<int:post_id>/restore', methods=['POST'])
@roles_required('Admin', 'Manager')
def restore_post(post_id):
    post = BlogService.restore_post(post_id)
    if not post:
        return jsonify({"error": "Post not found or could not be restored"}), 404

    # Invalidate relevant caches
    cache.delete('view//api/blog/posts')
    cache.delete('view//api/blog/posts/{}'.format(post.slug))
    return jsonify({"message": "Post restored successfully"})