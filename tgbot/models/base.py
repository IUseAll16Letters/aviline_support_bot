__all__ = ("Base", "TimeStampMixin")

from sqlalchemy import Column, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    ...


class TimeStampMixin:

    created_at = Column(DateTime(), default=func.current_timestamp())
    updated_at = Column(DateTime(), default=func.current_timestamp(), onupdate=func.current_timestamp())
