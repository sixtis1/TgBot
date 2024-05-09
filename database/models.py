from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy import BigInteger, Text, String

DATABASE_URL = "postgresql+asyncpg://postgres:1234@localhost:5432/bot_db"

engine = create_async_engine(DATABASE_URL)

async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    username: Mapped[str] = mapped_column(String(32))
    current_command: Mapped[str] = mapped_column(String(32), nullable=True)
    city = mapped_column(String(15))
    coord = mapped_column(String(22))
    settings = mapped_column(Text, nullable=True)
    

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)