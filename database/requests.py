from database.models import async_session
from database.models import User
from sqlalchemy import select


async def set_user(tg_id, username):
    try:
        async with async_session() as session:
            user = await session.scalar(select(User).where(User.tg_id == tg_id))

            if not user:
                user = User(tg_id=tg_id, username=username, current_command='start')
                session.add(user)
                await session.commit()
    except Exception as e:
        print(f"Ошибка при добавлении пользователя: {e}")

async def update_last_command(tg_id, command):
    try:
        async with async_session() as session:
            user = await session.scalar(select(User).where(User.tg_id == tg_id))
            if user:
                user.current_command = command
                await session.commit()
    except Exception as e:
        print(f"Ошибка при обновлении последней команды: {e}")


async def update_city(tg_id, city):
    try:
        async with async_session() as session:
            user = await session.scalar(select(User).where(User.tg_id == tg_id))
            if user:
                user.city = city
                await session.commit()
    except Exception as e:
        print(f"Ошибка при добавлении города: {e}")


async def update_coord(tg_id, lat, lon):
    try:
        async with async_session() as session:
            user = await session.scalar(select(User).where(User.tg_id == tg_id))
            if user:
                user.coord = f"{lat},{lon}"
                await session.commit()
    except Exception as e:
        print(f"Ошибка при добавлении координат: {e}")


async def check_location(tg_id):
    try:
        async with async_session() as session:
            user = await session.scalar(select(User).where(User.tg_id == tg_id))
            if user.coord:
                return ["coords", user.coord]
            elif user.city:
                return["city", user.city]
            else:
                return 0
    except Exception as e:
        print(f"Ошибка при запросе локации: {e}")


async def delete_location(tg_id):
    try:
        async with async_session() as session:
            user = await session.scalar(select(User).where(User.tg_id == tg_id))
            if user:
                user.city = None
                user.coord = None
                await session.commit() 
            else:
                print("Пользователь не найден.")
    except Exception as e:
        print(f"Ошибка при удалении локации пользователя: {e}")
