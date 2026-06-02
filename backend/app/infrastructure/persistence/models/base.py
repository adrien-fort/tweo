"""SQLAlchemy declarative base shared by all ORM models."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models.

    All infrastructure models inherit from this class. Domain entities
    are separate; repositories translate between the two.
    """
