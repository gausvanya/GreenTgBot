from aiogram.types import Message
from aiogram import Router, F

from tortoise.functions import Max

from ..Filters import Command #, IsAdminFilter
from ..DataBase.Models import Notes

rt = Router()


@rt.message(Command(
    commands=['+заметка'],
    html_parse_mode=True),
    F.chat.type != 'private',
)
async def add_chat_note_handler(message: Message, args=None) -> None | Message:
    #check_admin = IsAdminFilter(args[1])
    #if not await check_admin(message):
    #    return

    split = args[0].split('\n', 1)

    if len(split[0].split()) < 1 or len(split) < 2:
        return await message.answer(
            '❗️ Используйте команду правильно\n'
            '<code>+заметка [название]\nТекст с новой строки</>'
        )

    note_name = ' '.join(split[0].split()[1:]).lower()
    note_text = ' '.join(split[1:])

    result = await Notes.filter(
        chat_id=message.chat.id,
        name=note_name
    ).first()

    if result:
        return await message.answer('🛑 Заметка с таким названием уже существует.')

    result = await Notes.filter(chat_id=message.chat.id).annotate(max_note=Max('number')).first()
    max_note_number = result.max_note or 0

    await Notes.create(
        chat_id=message.chat.id,
        name=note_name,
        text=note_text,
        number=max_note_number + 1
    )

    await message.answer(f'✅ Заметка <b>{note_name} (#{max_note_number + 1})</> создана')


@rt.message(Command(
    commands=['-заметка'],
    html_parse_mode=True),
    F.chat.type != 'private'
)
async def remove_chat_note_handler(message: Message, args=None) -> None | Message:
    #check_admin = IsAdminFilter(args[1])
    #if not await check_admin(message):
    #    return

    split = args[0].split('\n', 1)

    if len(split[0].split()) < 1:
        return await message.answer(
            '❗️ Используйте команду правильно\n'
            '<code>-заметка [название]</>'
        )

    note_name = ' '.join(split[0].split()[1:]).lower()

    if note_name.isdigit():
        result = await Notes.filter(
            chat_id=message.chat.id,
            number=note_name
        ).first()
    else:
        result = await Notes.filter(
            chat_id=message.chat.id,
            name=note_name
        ).first()

    if not result:
        if note_name.isdigit():
            return await message.answer(f'❎ Заметка №<b>{note_name}</> не найдена')
        else:
            return await message.answer(f'❎ Заметка <b>«{note_name}»</> не найдена')

    await result.delete()

    await message.answer(f'✅ Заметка <b>{result.name}</> удалена')


@rt.message(Command(
    commands=['заметки']),
    F.chat.type != 'private'
)
async def get_notes_list_handler(message: Message, args=None) -> None | Message:
    #check_admin = IsAdminFilter(args[1])
    #if not await check_admin(message):
    #    return

    if len(args[0].split('\n', 1)[0].split()) > 1:
        return

    result = await Notes.filter(chat_id=message.chat.id).all()

    if not result:
        return await message.answer(
            '❌ Заметок пока нету\n\n'
            '💬 Для создания заметки пропишите:\n'
            '<code>+заметка [название]\nтекст с новой строки</>'
        )

    note_text = '📝 <b>Заметки чата:</>\n'
    for note in result:
        note_text += f'#{note.number}. <code>{note.name}</>\n'

    await message.answer(note_text + '\n\n💬 Чтобы открыть заметку пропишите: <code>!заметка [название | номер]</>')


@rt.message(Command(
    commands=['заметка']),
    F.chat.type != 'private'
)
async def get_note(message: Message, args=None) -> None | Message:
    #check_admin = IsAdminFilter(args[1])
    #if not await check_admin(message):
    #    return

    split = args[0].split('\n', 1)

    if len(split[0].split()) < 2:
        return await message.answer(
            '❗️ Используйте команду правильно\n'
            '<code>!заметка [название]</>'
        )

    note_name = ' '.join(split[0].split()[1:]).lower()

    if note_name.isdigit():
        result = await Notes.filter(
            chat_id=message.chat.id,
            number=note_name
        ).first()
    else:
        result = await Notes.filter(
            chat_id=message.chat.id,
            name=note_name
        ).first()

    if not result:
        if note_name.isdigit():
            return await message.answer(f'❎ Заметка №<b>{note_name}</> не найдена')
        else:
            return await message.answer(f'❎ Заметка <b>«{note_name}»</> не найдена')

    await message.answer(f'📝 <b>Заметка «{result.name}»:</>\n {result.text}')


@rt.message(Command(
    commands=['~заметка']),
    F.chat.type != 'private'
)
async def edit_note_handler(message: Message, args=None) -> None | Message:
    #check_admin = IsAdminFilter(args[1])
    #if not await check_admin(message):
    #    return

    split = args[0].split('\n', 1)

    if len(split[0].split()) < 1 or len(split) < 2:
        return await message.answer(
            '❗️ Используйте команду правильно\n'
            '<code>~заметка [название]\nТекст с новой строки</>'
        )

    note_name = ' '.join(split[0].split()[1:]).lower()
    note_text = ' '.join(split[1:])

    if note_name.isdigit():
        result = await Notes.filter(
            chat_id=message.chat.id,
            number=note_name
        ).first()
    else:
        result = await Notes.filter(
            chat_id=message.chat.id,
            name=note_name
        ).first()

    if not result:
        if note_name.isdigit():
            return await message.answer(f'❎ Заметка №<b>{note_name}</> не найдена')
        else:
            return await message.answer(f'❎ Заметка <b>«{note_name}»</> не найдена')


    await Notes.update_or_create(
        defaults={'text': note_text},
        chat_id=message.chat.id,
        name=result.name
    )

    if note_name.isdigit():
        await message.answer(f'✅ Заметка №<b>{note_name}</> обновлена')
    else:
        await message.answer(f'✅ Заметка <b>«{note_name}»</> обновлена')
