from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)

    sources: Mapped[list["Source"]] = relationship(back_populates="category")
    articles: Mapped[list["Article"]] = relationship(back_populates="category")
