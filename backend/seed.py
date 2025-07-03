from backend.models import User, Role, Product, Category, Collection, ReferralTier
from backend.extensions import db
from werkzeug.security import generate_password_hash
from backend.database import db, SessionLocal

def seed_database():
    """
    Seeds the database with initial data for roles, users, products, etc.
    """
    session = SessionLocal()
    try:
        print("Seeding database...")

        # Seed Roles
        roles = ['admin', 'user', 'b2b_user', 'editor']
        for role_name in roles:
            if not session.query(Role).filter_by(name=role_name).first():
                session.add(Role(name=role_name))
        
        session.commit()
        print("Roles seeded.")

        # Seed Admin User
        if not session.query(User).filter_by(email='admin@maisontruvra.com').first():
            admin_user = User(
                email='admin@maisontruvra.com',
                password_hash=generate_password_hash('AdminPassword123!'),
                first_name='Admin',
                last_name='User',
                is_active=True
            )
            admin_role = session.query(Role).filter_by(name='admin').first()
            admin_user.roles.append(admin_role)
            session.add(admin_user)
            session.commit()
            print("Admin user created.")

        # Seed Categories and Collections
        categories = ['Truffles', 'Oils', 'Salts', 'Honeys']
        for cat_name in categories:
            if not session.query(Category).filter_by(name=cat_name).first():
                session.add(Category(name=cat_name, slug=cat_name.lower()))
        
        collections = ['Summer Collection', 'Holiday Gifts']
        for col_name in collections:
            if not session.query(Collection).filter_by(name=col_name).first():
                session.add(Collection(name=col_name, slug=col_name.lower().replace(' ', '-')))
        
        session.commit()
        print("Categories and Collections seeded.")

        # Seed Products
        if session.query(Product).count() == 0:
            truffle_cat = session.query(Category).filter_by(slug='truffles').first()
            products_to_add = [
                Product(name='Black Summer Truffle', price=50.00, description='Fresh black summer truffles.', category_id=truffle_cat.id, sku='P001'),
                Product(name='White Alba Truffle', price=200.00, description='Exquisite white alba truffles.', category_id=truffle_cat.id, sku='P002')
            ]
            session.bulk_save_objects(products_to_add)
            session.commit()
            print("Products seeded.")

        # Seed Referral Tiers
        referral_tiers = [
            {'name': 'Bronze', 'min_referrals': 1, 'points_multiplier': 1.0},
            {'name': 'Silver', 'min_referrals': 5, 'points_multiplier': 1.2},
            {'name': 'Gold', 'min_referrals': 15, 'points_multiplier': 1.5},
            {'name': 'Platinum', 'min_referrals': 30, 'points_multiplier': 2.0}
        ]
        for tier_data in referral_tiers:
            if not session.query(ReferralTier).filter_by(name=tier_data['name']).first():
                session.add(ReferralTier(**tier_data))
        session.commit()
        print("Referral tiers seeded.")

        print("Database seeding complete.")
    finally:
        session.close()
    
if __name__ == "__main__":
    seed_database()
