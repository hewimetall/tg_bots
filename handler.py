import os
import json
from settings import Setting
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.dispatcher import FSMContext
from helper import MenuState
import pika

settings = Setting()


class FixQ:
    def __init__(self, message):
        self.message = message


def send_data(data: dict):
    with pika.BlockingConnection(pika.URLParameters(os.getenv('RABBITMQ_URL', ""))) as connection:
        with connection.channel() as channel:
            # отправка данных в очередь
            queue = os.getenv('QNAME', "form_push")
            channel.queue_declare(queue=queue,
                                  auto_delete=False,
                                  exclusive=False)
            channel.basic_publish(
                exchange='',
                body=json.dumps(data).encode(),
                routing_key=queue
            )


async def start_handler(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['link'] = message.from_user.url
        data['username'] = '{} {}'.format(message.from_user.first_name, message.from_user.last_name)

    await message.answer(settings.commands.text['message'])
    if message.text.lower() == settings.commands.text['cmd_start']:
        await text_handler(FixQ(message), state)
    else:
        await state.set_state(MenuState.START)
        await info_handler(message)


async def info_handler(message: Message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(settings.commands.info['cmd_start'],
                                    callback_data='cmd_start'))

    await message.answer(
        settings.commands.info['message'],
        reply_markup=markup
    )


async def text_handler(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer(
        settings.commands.text['message_1'],
    )
    await state.set_state(MenuState.TEXT)


async def swith_handler(callback_query: CallbackQuery, state: FSMContext):
    cmd = callback_query.data
    message = callback_query.message
    if cmd == 'send':
        await state.set_state(MenuState.FINISH)
        return await finish_handler(FixQ(message), state)
    if cmd == 'add_photo':
        await message.answer(
            settings.commands.swith['add_photo'],
        )
        await message.answer("Тип расширения: bmp, jpg, jpeg, png.")
        await state.set_state(MenuState.MEDIA)
    elif cmd == 'text_change':
        return await text_handler(callback_query, state)
    elif cmd == 'undo':
        await state.reset_data()
        await state.set_state(MenuState.START)
        await message.answer(settings.commands.swith['undo'])
        return await info_handler(message)


async def add_text_handler(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text
    inline_kb_full = InlineKeyboardMarkup(row_width=2)
    inline_kb_full.add(InlineKeyboardButton(settings.keyboard.text_swith['send'], callback_data="send"))
    inline_kb_full.add(InlineKeyboardButton(settings.keyboard.text_swith['add_photo'], callback_data="add_photo"))
    inline_kb_full.add(InlineKeyboardButton(settings.keyboard.text_swith['text_change'], callback_data="text_change"))
    inline_kb_full.add(InlineKeyboardButton(settings.keyboard.text_swith['undo'], callback_data="undo"))

    await message.answer(
        settings.commands.text['message_2'],
        reply_markup=inline_kb_full
    )


async def media_handler(message: Message, state: FSMContext):
    try:
        if getattr(message.document, 'mime_base', '') == 'image':
            url = await message.document.get_url()
        elif message.photo:
            url = await message.photo[0].get_url()
        else:
            raise TypeError("Not media")

        async with state.proxy() as data:
            if data.get('media'):
                data['media'].append(url)
            else:
                data['media'] = [url, ]
        await message.answer(settings.commands.media['message_1'])
        keyboard = InlineKeyboardMarkup()

        keyboard.add(InlineKeyboardButton(settings.keyboard.media['send'], callback_data="send"))
        keyboard.add(InlineKeyboardButton(settings.keyboard.media['upload'], callback_data="upload"))
        keyboard.add(InlineKeyboardButton(settings.keyboard.media['undo'], callback_data="undo"))

        await message.answer(settings.commands.media['message_2'],
                             reply_markup=keyboard
                             )
        await state.set_state(MenuState.FINISH)
    except TypeError:
        await message.answer(settings.commands.media['message_3'])
        await message.answer("Тип расширения: bmp, jpg, jpeg, png.")
    except AttributeError:
        await message.answer(settings.commands.media['message_3'])
        await message.answer("Тип расширения: bmp, jpg, jpeg, png.")


async def finish_handler(callback_query: CallbackQuery, state: FSMContext):
    cmd = callback_query.data
    message = callback_query.message

    if cmd == 'upload':
        await state.set_state(MenuState.MEDIA)
        await message.answer(settings.commands.finish['message_1'])
        return

    if cmd == 'send':
        send_data(await state.get_data())
        text = settings.commands.finish['message_2']
    else:
        text = settings.commands.finish['message_3']
    await message.answer(text)
    await state.reset_data()
    await state.set_state(MenuState.START)
    await info_handler(message)
