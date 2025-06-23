import random

def seed_database():
    app = create_app()
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        # Seed Categories
        categories_data = ["Fromages", "Charcuteries", "Vins", "Épicerie Fine"]
        categories = [Category(name=name) for name in categories_data]
        db.session.add_all(categories)
        db.session.commit()

        # Seed Collections
        collections_data = ["Apéritif", "Saveurs d'Italie", "Trésors de France"]
        collections = [Collection(name=name) for name in collections_data]
        db.session.add_all(collections)
        db.session.commit()

        # Seed Products
        products_data = [
            {"name": "Comté 18 Mois", "price": 25.50, "category": "Fromages", "sku": "FR001"},
            {"name": "Jambon de Parme", "price": 15.00, "category": "Charcuteries", "sku": "CH001"},
            {"name": "Bordeaux Supérieur", "price": 18.75, "category": "Vins", "sku": "VN001"},
            {"name": "Huile d'Olive Vierge Extra", "price": 12.00, "category": "Épicerie Fine", "sku": "EP001"},
        ]
        
        for p_data in products_data:
            category = Category.query.filter_by(name=p_data["category"]).first()
            product = Product(
                name=p_data["name"],
                description=f"Description for {p_data['name']}",
                price=p_data["price"],
                sku=p_data["sku"],
                category_id=category.id,
                stock_quantity=random.randint(10, 100)
            )
            db.session.add(product)

        db.session.commit()
        print("Database seeded successfully!")


def seed_roles():
    """Creates predefined roles in the database."""
    roles = ['admin', 'staff', 'b2b_customer', 'b2c_customer']
    for role_name in roles:
        if not Role.query.filter_by(name=role_name).first():
            role = Role(name=role_name)
            db.session.add(role)
    db.session.commit()

def seed_admin():
    """Creates a default admin user."""
    from services.user_service import UserService
    
    email = 'admin@example.com'
    if not User.query.filter_by(email=email).first():
        admin_data = {
            'email': email,
            'password': 'super-secret-password', # Change this in production
            'first_name': 'Admin',
            'last_name': 'User',
            'is_admin': True
        }
        user_service = UserService()
        admin_user = user_service.create_user(admin_data, by_admin=True)
        
        # Assign admin role
        admin_role = Role.query.filter_by(name='admin').first()
        if admin_role:
            admin_user.roles.append(admin_role)
            db.session.commit()
            
if __name__ == "__main__":
    seed_database()
