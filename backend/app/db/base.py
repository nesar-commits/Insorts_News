from app.db.base_class import Base

# Import all models here so Alembic autogenerate can discover them via Base.metadata
from app.models.user import User  # noqa: E402,F401
from app.models.category import Category  # noqa: E402,F401
from app.models.source import Source  # noqa: E402,F401
from app.models.article import Article  # noqa: E402,F401
from app.models.bookmark import Bookmark  # noqa: E402,F401
