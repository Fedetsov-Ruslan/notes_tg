from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command, StateFilter, or_f
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from database.orm_query import add_usertg, orm_add_record, orm_current_user, orm_get_records, orm_login_user
from kbds.inline import get_callback_btns

user_private_router = Router()

class current_user(StatesGroup):
    user_id = State()

class Loging(StatesGroup):
    email = State()
    password = State()

class AddRecord(StatesGroup):
    title = State()
    content = State()
    tags = State()

@user_private_router.message(CommandStart())
async def start(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    current_user = await orm_current_user(callback.from_user.id, session)
    if current_user is None:
        await callback.answer("У вас уже есть акаунт?",reply_markup=get_callback_btns(btns={
            'Да, я хочу войти': 'Logining',
            'Нет, я хочу зарегистрироваться': 'Registring',
        }, sizes=(2,)))
    else:
        await callback.answer("Что хотите сделать?",reply_markup=get_callback_btns(btns={
            
            "Мои записи": "MyRecords",
            "Добавить запись": "AddRecord",
            "Поиск по тегам": "SearchByTags",
        }, sizes=(1,)))
        await state.update_data(user_id=current_user)

@user_private_router.callback_query(F.data.startswith('Logining'))
async def loging(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    await callback.message.answer("Введите свою почту")

    await state.set_state(Loging.email)

@user_private_router.message(Loging.email)
async def email(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.answer("Введите свой пароль")
    await state.set_state(Loging.password)

@user_private_router.message(Loging.password)
async def password(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(password=message.text)
    data = await state.get_data()
    email = data.get('email')
    password = message.text
    await message.delete()
    current_user = await orm_login_user(email, password, session)
    if current_user is None:
        await message.answer("Неправильная почта или пароль",reply_markup=get_callback_btns(btns={
            'Да, я хочу войти': 'Logining',
            'Нет, я хочу зарегистрироваться': 'Registring',
        }, sizes=(2,)))
        state.clear()
    else:
        print(current_user, message.from_user.id)
        await add_usertg(current_user, message.from_user.id, session)
        await message.answer("Вы вошли в аккаунт",reply_markup=get_callback_btns(btns={
            
            "Мои записи": "MyRecords",
            "Добавить запись": "AddRecord",
            "Поиск по тегам": "SearchByTags",
        }, sizes=(1,)))
        await state.update_data(user_id=current_user)

@user_private_router.callback_query(F.data.startswith('MyRecords'))
async def get_my_records(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    data = await state.get_data()
    current_user = data.get('user_id')
    records = await orm_get_records(current_user, session)
    if not records:
        await callback.message.answer("У вас нет записей")
    else:
        for record in records:
            await callback.message.answer(f"{record['title']}\n{record['content']}\n #{'# '.join(record['tags'])}\n{record['created_at']}")
        await callback.message.answer("Что хотите сделать?",reply_markup=get_callback_btns(btns={           
                "Мои записи": "MyRecords",
                "Добавить запись": "AddRecord",
                "Поиск по тегам": "SearchByTags",
            }, sizes=(1,)))
    
@user_private_router.callback_query(F.data.startswith('AddRecord'))
async def title(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите название записи")
    await state.set_state(AddRecord.title)

@user_private_router.message(AddRecord.title)
async def content(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введите содержание записи")
    await state.set_state(AddRecord.content)

@user_private_router.message(AddRecord.content)
async def tags(message: Message, state: FSMContext):
    await state.update_data(content=message.text)
    await message.answer("Выберите теги. Через решетку, наприме #программирование#дизайн")
    await state.set_state(AddRecord.tags)

@user_private_router.message(AddRecord.tags)
async def new_record(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(tags=message.text)
    data = await state.get_data()
    await orm_add_record(data, session)
    await message.answer("Запись добавлена", reply_markup=get_callback_btns(btns={           
                "Мои записи": "MyRecords",
                "Добавить запись": "AddRecord",
                "Поиск по тегам": "SearchByTags",
            }, sizes=(1,)))
        