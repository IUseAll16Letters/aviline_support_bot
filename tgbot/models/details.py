# __all__ = ("ProductDetail", )


from sqlalchemy import String, Text, ForeignKey, URL
from sqlalchemy.orm import relationship, mapped_column, Mapped

from .base import Base, TimeStampMixin


class ProductDetail(Base, TimeStampMixin):
    __tablename__ = 'aviline_productdetail'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    attachment: Mapped[str] = mapped_column(String(200), nullable=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("aviline_product.id"))

    product: Mapped["Product"] = relationship(back_populates="details")

    def __repr__(self):
        return F"Prod_Detail(id={self.id!r}, title={self.title[:10]})"
