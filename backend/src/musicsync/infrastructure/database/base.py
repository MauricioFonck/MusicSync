from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base for infrastructure ORM models; never imported by the domain."""
