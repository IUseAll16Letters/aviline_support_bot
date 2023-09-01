__all__ = ("Product", )

from sqlalchemy import Integer, Column, String, Boolean, BigInteger, Text, DateTime, func

from .base import Base, TimeStampMixin


class Product(Base, TimeStampMixin):
    """
    Class that implements Product model
    Attributes:
        id: Product unique identifier
        name: Product name, as varchar255
        description: Product description as text

    Inherited Attributes:
        Inherits from Base, TimestampMixin classes, which provide additional attributes and functionality.

    Inherited Methods:
        Inherits methods from Base, TimestampMixin classes, which provide additional functionality.

    """
    __tablename__ = 'aviline_product'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(length=255), nullable=True)
    description = Column(Text(), nullable=True)
