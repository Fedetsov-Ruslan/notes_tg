from sqlalchemy import distinct, exists, select, update, delete, values
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_users.password import Argon2Hasher

from database.models import Record, Tag, TagsRecord, User, UserTg


async def orm_current_user(user: int, session: AsyncSession):
    query = select(UserTg).where(UserTg.tg_id == user)
    result = await session.execute(query)
    user = result.scalars().first()
    
    if user is None:
        return None
    else:
        return user.user_id
    
async def orm_login_user(email: str, password: str, session: AsyncSession):
    query = select(User).where(User.email == email)
    result = await session.execute(query)
    user = result.scalars().first()
    if user is None:
        return None
    elif Argon2Hasher().verify(password, user.hashed_password):
        return user.id
    else:
        return None
    
async def add_usertg(user: int, tg: int, session: AsyncSession):
    user = UserTg(user_id=user, tg_id=tg)
    session.add(user)
    await session.commit()
    
    