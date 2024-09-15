from sqlalchemy import distinct, exists, select, update, delete, values
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_users.password import Argon2Hasher

from database.models import Record, Tag, TagsRecord, User, UserTg


async def orm_current_user(user: int, session: AsyncSession):
    query = select(UserTg).where(UserTg.tg_id == user)
    result = await session.execute(query)
    if result is None:
        return False
    else:
        return UserTg.user_id
    
async def orm_login_user(email: str, password: str, session: AsyncSession):
    query = select(User).where(User.email == email)
    result = await session.execute(query)
    if result is None:
        return None
    elif Argon2Hasher().verify(password, result.scalars().first().password):
        return User.id
    else:
        return None
    
    