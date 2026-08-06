"""
Database Schema Initialization and Superuser Seeder.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logging import logger
from app.core.security import get_password_hash
from app.db.session import Base, engine
from app.models.user import User


async def init_db_tables() -> None:
    """Creates database tables if they do not exist."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schema initialized successfully.")
    except Exception as e:
        logger.error("Failed to initialize database tables", error=str(e))


async def create_initial_superuser(db: AsyncSession) -> None:
    """Seeds a default administrator account if database is empty."""
    try:
        stmt = select(User).where(User.email == "admin@jarvis.ai")
        res = await db.execute(stmt)
        user = res.scalars().first()

        if not user:
            admin_user = User(
                email="admin@jarvis.ai",
                full_name="JARVIS Administrator",
                hashed_password=get_password_hash("admin12345"),
                is_active=True,
                is_superuser=True
            )
            db.add(admin_user)
            await db.commit()
            logger.info("Default superuser created: admin@jarvis.ai")
    except Exception as e:
        logger.error("Error creating initial superuser", error=str(e))
