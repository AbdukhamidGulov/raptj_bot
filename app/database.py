from typing import List, Optional
from sqlalchemy import String, ForeignKey, select
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import SQLALCHEMY_DATABASE_URI


engine = create_async_engine(SQLALCHEMY_DATABASE_URI, echo=True)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


class Base(DeclarativeBase):
    pass


class Raper(Base):
    __tablename__ = "rapers"

    id: Mapped[int] = mapped_column(primary_key=True)
    nick: Mapped[str] = mapped_column(String(30))
    bio: Mapped[Optional[str]]
    links: Mapped[str] = mapped_column(String(120))

    tracks: Mapped[List["Track"]] = relationship("Track", back_populates="raper", cascade="all, delete-orphan")


class Track(Base):
    __tablename__ = "tracks"

    id: Mapped[int] = mapped_column(primary_key=True)
    track_name: Mapped[str] = mapped_column(String)
    links: Mapped[str] = mapped_column(String)
    raper_id: Mapped[int] = mapped_column(ForeignKey("rapers.id"))

    raper: Mapped["Raper"] = relationship("Raper", back_populates="tracks")


async def select_nick(name: str):
    async with AsyncSessionLocal() as session:
        stmt = select(Raper).where(Raper.nick.ilike(f"%{name}%"))
        result = await session.execute(stmt)
        return result.fetchone()


async def get_all_rapers():
    async with AsyncSessionLocal() as session:
        stmt = select(Raper.nick)
        result = await session.execute(stmt)
        return [row[0] for row in result.fetchall()]


async def add_raper_info(nick: str, bio: Optional[str], links: str):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            new_raper = Raper(nick=nick, bio=bio, links=links)
            session.add(new_raper)


async def add_track_info(nick: str, track_name: str, links: str):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            result = await session.execute(select(Raper.id).where(Raper.nick == nick))
            raper_id = result.scalar()

            new_track = Track(track_name=track_name, links=links, raper_id=raper_id)
            session.add(new_track)


async def select_track(name: str):
    async with AsyncSessionLocal() as session:
        stmt = select(Track).where(Track.track_name.ilike(f"%{name}%"))
        result = await session.execute(stmt)
        return result.fetchone()


async def get_tracks_by_raper_name(nick: str):
    async with AsyncSessionLocal() as session:
        raper_id = (select(Raper.id).where(Raper.nick == nick).scalar_subquery())
        stmt = select(Track).where(Track.raper_id == raper_id)
        result = await session.execute(stmt)
        return result.scalars().all()


async def get_raper_info(nick: str):
    async with AsyncSessionLocal() as session:
        stmt = select(Raper.bio, Raper.links).where(Raper.nick.ilike(f"%{nick}%"))
        result = await session.execute(stmt)
        return result.fetchone()


# Функция для удаления всех таблиц и их повторного создания
async def reset_database():
    async with engine.begin() as conn:
        # Удаляем все таблицы
        await conn.run_sync(Base.metadata.drop_all)
        # Создаем заново
        await conn.run_sync(Base.metadata.create_all)
