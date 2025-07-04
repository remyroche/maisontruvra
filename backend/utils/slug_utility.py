import re
from sqlalchemy.orm.session import Session


def generate_unique_slug(name: str, model_class, session: Session) -> str:
    """
    Generates a URL-friendly, unique slug for a given name and SQLAlchemy model.

    Args:
        name: The string to convert into a slug.
        model_class: The SQLAlchemy model class to check for uniqueness (e.g., Product, Category).
        session: The database session to use for the query.

    Returns:
        A unique slug string.
    """
    if not name:
        raise ValueError("Name cannot be empty for slug generation.")

    # 1. Create a base slug
    slug = name.lower()
    slug = re.sub(r"[^\w\s-]", "", slug).strip()
    slug = re.sub(r"[-\s]+", "-", slug)

    if not slug:
        import uuid

        return str(uuid.uuid4())[:8]

    # 2. Check for uniqueness and append a counter if necessary
    base_slug = slug
    counter = 1
    while session.query(model_class).filter(model_class.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug
