# Main file that starts the Telegram bot using Telethon.
# Handles events, user interactions, and integrates other modules (keyboards, texts, etc.).
from telethon import events
from telethon.sync import TelegramClient
import re
import asyncio
from colorama import Fore, Back, Style


from keyboards import *
from config import *
from texts import *
from web import *
from sql import *


user_client = TelegramClient('user', API_ID, API_HASH)
bot_client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

user_states = {}


@bot_client.on(events.NewMessage(pattern='/start'))
async def start_handler(msg):
    user = await msg.get_sender()
    user_id = user.id
    username = user.username
    first_name = user.first_name
    if await is_new_user(user_id):
        await add_user(user_id, username, first_name)
        return
    user_states[msg.sender_id] = 'default'
    await msg.respond(MESSAGES['start'], buttons=await generate_menu_keyboard(user_id))


@bot_client.on(events.CallbackQuery(data=b'add_channel'))
async def add_channel_handler(msg):
    await msg.edit(MESSAGES['add_channel'], buttons=await generate_back_keyboard())
    user_states[msg.sender_id] = 'waiting_msg_from_channel'


@bot_client.on(events.CallbackQuery(data=re.compile(b'^add_donor_')))
async def add_donor_handler(msg):
    data = msg.data.decode()
    channel_id = data.split('_')[2]
    await msg.edit(MESSAGES['add_donor'], buttons=await generate_back_keyboard())
    user_states[msg.sender_id] = f'waiting_msg_from_donor_{channel_id}'


@bot_client.on(events.CallbackQuery(data=re.compile(b'^donor_')))
async def donors_handler(msg):
    data = msg.data.decode()
    donor_id = data.split('_')[1]
    channel_id = data.split('_')[2]
    donor_name = await get_donor_name(donor_id)
    await msg.edit(MESSAGES['donors_settings'].format(donor_name, donor_id), buttons=await generate_edit_donor(channel_id, donor_id))


@bot_client.on(events.CallbackQuery(data=re.compile(b'^remove_donor_')))
async def remove_donor_handler(msg):
    data = msg.data.decode()
    donor_id = data.split('_')[2]
    reciever_channel = data.split('_')[3]
    await delete_donor(reciever_channel, donor_id)
    await msg.edit(MESSAGES['donors_channels'], buttons=await generate_donors_keyboard(reciever_channel))


@bot_client.on(events.CallbackQuery(data=re.compile(b'^deactivate_channel_')))
async def remove_donor_handler(msg):
    user = await msg.get_sender()
    user_id = user.id
    data = msg.data.decode()
    channel_id = data.split('_')[2]
    await delete_all_from_channels_by_channel_id(channel_id)
    await delete_all_from_donors_by_channel_id(channel_id)
    await delete_all_from_donors_settings_by_channel_id(channel_id)
    await delete_all_from_signature_by_channel_id(channel_id)
    await delete_all_from_channel_languages_by_channel_id(channel_id)
    await msg.edit(MESSAGES['start'], buttons=await generate_menu_keyboard(user_id))
    

@bot_client.on(events.NewMessage)
async def handler_all_messages(msg):
    user_state = user_states.get(msg.sender_id)
    #Checking the user's status
    if user_state != 'default' and user_state != None:
        try:
            await bot_client.edit_message(msg.sender_id, msg.id-1, buttons=None) # We are trying to remove the button from the last message if it is ours
        except:
            pass
        if user_state == 'waiting_msg_from_channel':
            # If the user is in the desired state, we perform some logic
            channel_id_from_forward, original_channel_name, user_id = await add_new_channel(msg, bot_client, user_client, msg.sender_id)
            if await is_new_channel(channel_id_from_forward):
                if channel_id_from_forward != None:
                    if await can_bot_post(bot_client, channel_id_from_forward):
                        await add_channel(user_id, channel_id_from_forward, original_channel_name)
                        await bot_client.send_message(user_id, MESSAGES['have_access_to_post_on_channel'].format(original_channel_name), parse_mode='HTML')
                        await start_handler(msg)
                    else:
                        await bot_client.send_message(user_id, MESSAGES['dont_have_access_to_post_on_channel'].format(original_channel_name), parse_mode='HTML', buttons=await generate_back_keyboard())
            else:
                await bot_client.send_message(user_id, MESSAGES['channel_already_exist'].format(original_channel_name), parse_mode='HTML', buttons=await generate_back_keyboard())

        elif user_state[:23] == 'waiting_msg_from_donor_':
            reciever_channel_id = user_state[23:]   # Channel ID where it is sent
            reciever_channel_name = await get_channel_name(reciever_channel_id)   # Channel name where it is forwarded   
            channel_id_from_forward, original_channel_name, user_id = await add_new_channel(msg, bot_client, user_client, msg.sender_id)    # Getting information about a channel from a forwarded message
            if channel_id_from_forward != None or original_channel_name != None:    # If information is found from the sent message
                if await is_donor_linked(reciever_channel_id, channel_id_from_forward):   # Checking whether the donor is already connected to this channel
                    await bot_client.send_message(user_id, MESSAGES['donor_already_added'])
                else:
                    await add_donor(reciever_channel_id, reciever_channel_name, channel_id_from_forward, original_channel_name, user_id)   # Adding information about the donor to the database
                    await add_channel_to_settings(reciever_channel_id, user_id, channel_id_from_forward) # Adding information about the donor to the settings
                    await add_channel_language(reciever_channel_id, channel_id_from_forward)
                    await bot_client.send_message(user_id, MESSAGES['success_added_donor'].format(original_channel_name, reciever_channel_name), parse_mode='HTML')
                user_states[msg.sender_id] = 'default'    
                await bot_client.send_message(user_id, MESSAGES['donors_channels'], buttons=await generate_donors_keyboard(reciever_channel_id))
        elif user_state[:18] == 'waiting_signature_':
            reciever_channel_id = user_state[18:]   # Channel ID for whom to create a signature
            try:
                await manage_signatures(reciever_channel_id, msg.message.text)
                await bot_client.send_message(msg.message.sender_id, MESSAGES['signature_success_added'])
                await start_handler(msg)
            except:
                await bot_client.send_message(msg.message.sender_id, MESSAGES['signature_error'], buttons=await generate_back_keyboard())
            pass
        else:
            pass


@bot_client.on(events.CallbackQuery(data=re.compile(b'^channel_')))
async def channels_config_handler(msg):
    _, channel_id = msg.data.split(b'_', 1)
    channel_info = await get_channels_by_channel_id(channel_id.decode())
    await bot_client.edit_message(msg.sender_id, msg.message_id, MESSAGES['channel_info'].format(channel_info[1], channel_info[0]), buttons=await generate_donors_keyboard(channel_id.decode()))


@bot_client.on(events.CallbackQuery(data=re.compile(b'^settings_')))
async def simple_channel_config_handler(msg):
    config_info = msg.data.split(b'_')
    setting = config_info[1].decode()
    channel_id = config_info[2].decode()
    donor_id = config_info[3].decode()
    if setting == 'Translate':
        await bot_client.edit_message(msg.sender_id, msg.message_id, MESSAGES['select_language'], buttons=await generate_language(channel_id, donor_id))
    elif setting == 'delete':
        await delete_donor(channel_id, donor_id)
        await remove_donor_from_settings_by_channel_and_donor_id(channel_id, donor_id)
        await remove_donor_from_language_by_channel_and_donor_id(channel_id, donor_id)
        await bot_client.delete_messages(msg.sender_id, msg.message_id)
        await start_handler(msg)
    elif setting == 'AddSignature':
        user_states[msg.sender_id] = f'waiting_signature_{channel_id}'
        await bot_client.edit_message(msg.sender_id, msg.message_id, MESSAGES['add_signatures'], buttons=await generate_back_keyboard())
    else:
        await toggle_column_value(setting, channel_id, donor_id)
        await bot_client.edit_message(msg.sender_id, msg.message_id, buttons=await generate_edit_donor(channel_id, donor_id))


@bot_client.on(events.CallbackQuery(data=re.compile(b'^language')))
async def channels_config_handler(msg):
    channel_language_settings = msg.data.split(b'_')
    language = channel_language_settings[1].decode()
    channel = channel_language_settings[2].decode()
    donor_id = channel_language_settings[3].decode()
    await set_channel_language(channel, donor_id, language)
    await bot_client.edit_message(msg.sender_id, msg.message_id, MESSAGES['select_language'], buttons= await generate_language(channel, donor_id))



@bot_client.on(events.CallbackQuery(data=b'back'))
async def back_handler(msg):
    user = await msg.get_sender()
    user_id = user.id
    await msg.edit(MESSAGES['start'], buttons=await generate_menu_keyboard(user_id))
    user_states[msg.sender_id] = 'default'


@bot_client.on(events.NewMessage(pattern='/add_keyword'))
async def add_keyword_handler(event):
    # Extracting the text after the command '/add_keyword'
    match = re.match(r'/add_keyword\s+(.+)', event.raw_text)
    if match:
        keyword = match.group(1)
        # Оsend a response with the extracted keyword
        await new_ad_keyword(keyword)
        await event.respond(MESSAGES['ad_keyword_added'].format(keyword))


@user_client.on(events.NewMessage(chats=None))
@user_client.on(events.Album())
async def copy_to_channel(event):
    await user_client.get_dialogs()
    donor_id = int(str(event.chat_id)[4:])
    chat = await user_client.get_entity(donor_id)
    if not chat.broadcast or donor_id not in await get_unique_donor_ids():
        return
    detector = TextSimilarityDetector(threshold=0.6)
    to_channels = await get_channels_with_autoposting(donor_id)
    gallery = getattr(event, 'messages', None)
    for to_channel in to_channels:
        await user_client.get_entity(to_channel)
        if await check_autoposting(to_channel, donor_id):
            settings = await get_channel_settings(to_channel, donor_id)
            if gallery:
                caption = gallery[0].text if gallery[0].text else "" # Extracting original caption text for an album
                print(Fore.RED + f'Notification received:' + Style.RESET_ALL, caption)
                if settings["FilterAds"]:
                    if await is_advertisement(caption):
                        print(f'Recognized by advertising:'  + Style.RESET_ALL, caption)
                        continue
                last_posts_on_my_channel = await get_last_texts(user_client, to_channel, 100)
                if settings["FilterDublicates"]:
                    if detector.is_duplicate(caption, last_posts_on_my_channel):
                        print(Fore.RED + f'Recognized as a duplicate:' + Style.RESET_ALL, caption)
                        continue
                new_msg = await editing_message_text(user_client, caption, to_channel, donor_id, settings)
                if not settings["FilterAlbums"]:
                    if not settings["FilterText"]:
                        await user_client.send_file(to_channel, gallery, caption=new_msg, link_preview=False)
                    else:
                        await user_client.send_file(to_channel, gallery)
                else:
                    if not settings["FilterText"]:
                        await user_client.send_message(to_channel, new_msg, link_preview=False) # Sending the original message text
                
            elif not gallery and event.message.media and not event.grouped_id:
                caption = event.message.text if event.message.text else "" # Extracting original caption text for a media file
                print(Fore.RED + f'Notification received:' + Style.RESET_ALL, caption)
                if settings["FilterAds"]:
                    if await is_advertisement(caption):
                        print(Fore.RED + f'Recognized by advertising:' + Style.RESET_ALL, caption)
                        continue
                last_posts_on_my_channel = await get_last_texts(user_client, to_channel, 100)
                if settings["FilterDublicates"]:
                    if detector.is_duplicate(caption, last_posts_on_my_channel):
                        print(Fore.RED + f'Recognized as a duplicate:' + Style.RESET_ALL, caption)
                        continue
                new_msg = await editing_message_text(user_client, caption, to_channel, donor_id, settings)
                if get_media_type(event) == 'photo':
                    if not settings["FilterPhoto"]:
                        if not settings["FilterText"]:
                            await user_client.send_file(to_channel, event.message.media, caption=new_msg, link_preview=False)
                        else:
                            await user_client.send_file(to_channel, event.message.media, link_preview=False)
                    else:
                        await user_client.send_message(to_channel, new_msg, link_preview=False) # Sending the original message text
                else:
                    if not settings["FilterVideo"]:
                        if not settings["FilterText"]:
                            await user_client.send_file(to_channel, event.message.media, caption=new_msg, link_preview=False)
                        else:
                            await user_client.send_file(to_channel, event.message.media, link_preview=False)
                    else:
                        await user_client.send_message(to_channel, new_msg, link_preview=False) # Sending the original message text

            elif not gallery and not event.message.media and not event.grouped_id:
                print(Fore.RED + f'Notification received:' + Style.RESET_ALL, event.message.text)
                if settings["FilterAds"]:
                    if await is_advertisement(event.message.text):
                        print(Fore.RED + f'Recognized by advertising:' + Style.RESET_ALL, event.message.text)
                        continue
                last_posts_on_my_channel = await get_last_texts(user_client, to_channel, 100)
                if settings["FilterDublicates"]:
                    if detector.is_duplicate(event.message.text, last_posts_on_my_channel):
                        print(Fore.RED + f'Recognized as a duplicate:' + Style.RESET_ALL, event.message.text)
                        continue
                if not settings["FilterText"]:
                    new_msg = await editing_message_text(user_client, event.message.text, to_channel, donor_id, settings)
                    await user_client.send_message(to_channel, new_msg, link_preview=False) # Sending the original message text

async def main():
    await user_client.start()
    await user_client.get_dialogs()
    await bot_client.start()
    await user_client.run_until_disconnected()
    await bot_client.run_until_disconnected()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())