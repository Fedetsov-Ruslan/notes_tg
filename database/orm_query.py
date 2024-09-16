from sqlalchemy import distinct, exists, select, update, delete, values
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_users.password import Argon2Hasher

from database.models import Record, Tag, TagsRecord, User, UserTg

# проверка связан ли ТГ с какой либо записью пользователя
async def orm_current_user(user: int, session: AsyncSession):
    query = select(UserTg).where(UserTg.tg_id == user)
    result = await session.execute(query)
    user = result.scalars().first()
    
    if user is None:
        return None
    else:
        return user.user_id

# Авторизация пользователя. Возвращает ID пользователя если введины верные логин и пароль.  
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

# Связь пользователя с ТГ
async def add_usertg(user: int, tg: int, session: AsyncSession):
    user = UserTg(user_id=user, tg_id=tg)
    session.add(user)
    await session.commit()

# Возвращает все записи пользователя
async def orm_get_records(current_user: int, session: AsyncSession):
    query_records = select(Record).where(Record.auther == current_user)
    result = await session.execute(query_records)
    recodrds =  result.scalars().all()
    record_id_list = [rec.id for rec in recodrds]
    query_tags = (select(Tag.tag_name, TagsRecord.record_id)
                  .join(TagsRecord, TagsRecord.tag_id == Tag.id)
                  .where(TagsRecord.record_id.in_(record_id_list)))
    result = await session.execute(query_tags)
    tags =  result.all()  
    tags_by_record = {}
    for tag in tags:
        if tag[1] not in tags_by_record:
            tags_by_record[tag[1]] = []
        tags_by_record[tag[1]].append(tag[0])
    return [{
        "id": rec.id,
        "auther": rec.auther,
        "title": rec.title,
        "content": rec.content,
        "tags": tags_by_record[rec.id],
        "created_at": rec.created_at
    } for rec in recodrds]

# Добавление записи
async def orm_add_record(data: dict, session: AsyncSession):
    current_user = data['user_id']
    new_tags = data["tags"].lstrip('#').strip().split('#')
    new_record = Record(
        auther = current_user,
        title = data["title"],
        content = data["content"]
    )
    session.add(new_record)
    session.flush()
    tags_query = select(Tag)
    all_tags = (await session.execute(tags_query)).scalars().all()
    tags = {tag.tag_name : tag.id  for tag in all_tags}
    for tag in new_tags:
        if tag not in tags:
            new_tag = Tag(tag_name=tag)
            session.add(new_tag)
    tags_id_query = select(Tag.id).where(Tag.tag_name.in_(new_tags))
    tags_id = (await session.execute(tags_id_query)).scalars().all()
    for tag_id in tags_id:
        session.add(TagsRecord(tag_id=tag_id, record_id=new_record.id))
    await session.commit()

# Поиск записей по тегам
async def orm_search_by_tags(tags:list, session: AsyncSession):
    query = select(Record).join(TagsRecord).join(Tag).where(Tag.tag_name.in_(tags))
    result = await session.execute(query)
    records = result.scalars().all()
    record_id_list = [rec.id for rec in records]
    query_tags = (select(Tag.tag_name, TagsRecord.record_id)
                  .join(TagsRecord, TagsRecord.tag_id == Tag.id)
                  .where(TagsRecord.record_id.in_(record_id_list)))
    result = await session.execute(query_tags)
    tags =  result.all()  
    tags_by_record = {}
    for tag in tags:
        if tag[1] not in tags_by_record:
            tags_by_record[tag[1]] = []
        tags_by_record[tag[1]].append(tag[0])
    return [{
        "id": rec.id,
        "auther": rec.auther,
        "title": rec.title,
        "content": rec.content,
        "tags": tags_by_record[rec.id],
        "created_at": rec.created_at
    } for rec in records]

async def orm_register_user(data: dict, session: AsyncSession):
    new_user = User(email=data['reg_email'], hashed_password=Argon2Hasher().hash(data['reg_password']), username=data['reg_username'])
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user.id