__all__ = ("ProductProblem", )


from sqlalchemy import Integer, Column, String, Boolean, BigInteger, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship, mapped_column

from .base import Base, TimeStampMixin


class ProductProblem(Base, TimeStampMixin):
    """
    Class that implements Problem of Product model
    Attributes:
        id: Problem unique identifier
        title: Problem statement
        solution: Problem solution

        product_id: Relation to Product by FK

    Inherited Attributes:
        Inherits from Base, TimestampMixin classes, which provide additional attributes and functionality.

    Inherited Methods:
        Inherits methods from Base, TimestampMixin classes, which provide additional functionality.

    """
    __tablename__ = 'aviline_productproblem'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(length=255), nullable=True)
    solution = Column(Text(length=255), nullable=True)

    product_id = mapped_column(ForeignKey("aviline_product.id"))

