# This file generates dynamic keyboards for Telegram using Telethon's Button module.
# Includes logic to retrieve data from the database for keyboard creation.
from telethon.tl.custom import Button

from sql import *
from functions import *

async def generate_menu_keyboard(user_id):
    channels_data = await get_channels_by_user_id(user_id)
    buttons = []
    for channel_id, channel_name in channels_data:
        button_text = channel_name
        callback_data = f"channel_{channel_id}"
        button = Button.inline(button_text, data=callback_data)
        button_delete = Button.inline('◀️ Delete', data=f"deactivate_channel_{channel_id}")

        buttons.append([button, button_delete])

    buttons.append([Button.inline('➕ Add new channel', b'add_channel')])
    return buttons


async def generate_back_keyboard():
    return [
            [Button.inline('⬅️ Return', b'back')],
        ]


async def generate_edit_donor(channel_id, donor_id):
    buttons = []
    status = await get_channel_settings(channel_id, donor_id)
    status = replace_boolean_with_symbols(status)
    translate = await translate_enable(channel_id, donor_id)
    if translate:
        translate_emoji = '✅'
    else:
        translate_emoji = '❌'

    button_1 = Button.inline(f'{status["autoposting"]}  Auto-posting', data=f'settings_autoposting_{channel_id}_{donor_id}')
    button_2 = Button.inline(f'{status["FilterDublicates"]}  Duplicate filter', data=f'settings_FilterDublicates_{channel_id}_{donor_id}')
    button_3 = Button.inline(f'{status["FilterAds"]}  Ad filter', data=f'settings_FilterAds_{channel_id}_{donor_id}')
    button_4 = Button.inline(f'{status["FilterSignatures"]}  Signature filter', data=f'settings_FilterSignatures_{channel_id}_{donor_id}')
    button_5 = Button.inline(f'{status["FilterPhoto"]}  Photo filter', data=f'settings_FilterPhoto_{channel_id}_{donor_id}')
    button_6 = Button.inline(f'{status["FilterVideo"]}  Video filter', data=f'settings_FilterVideo_{channel_id}_{donor_id}')
    button_7 = Button.inline(f'{status["FilterAlbums"]}  Album filter', data=f'settings_FilterAlbums_{channel_id}_{donor_id}')
    button_8 = Button.inline(f'{status["FilterText"]}  Text filter', data=f'settings_FilterText_{channel_id}_{donor_id}')
    button_9 = Button.inline(f'{status["FilterLinks"]}  Link filter', data=f'settings_FilterLinks_{channel_id}_{donor_id}')
    button_10 = Button.inline(f'{status["UniqueText"]}  Text uniqueness', data=f'settings_UniqueText_{channel_id}_{donor_id}')
    button_11 = Button.inline(f'{status["UseEmoji"]}  Uniqueness + emoji', data=f'settings_UseEmoji_{channel_id}_{donor_id}')
    button_12 = Button.inline(f'{translate_emoji}  text translation', data=f'settings_Translate_{channel_id}_{donor_id}')
    button_13 = Button.inline(f'Add signature for donor', data=f'settings_AddSignature_{channel_id}_{donor_id}')
    button_14 = Button.inline('🚫 Remove donor', data=f'settings_delete_{channel_id}_{donor_id}')
    button_15 = Button.inline('⬅️ Return', data='back')
    buttons.extend([[button_1], [button_2], [button_3], [button_4], [button_5], [button_6], [button_7], [button_8], [button_9], [button_10], [button_11], [button_12], [button_13], [button_14], [button_15]])
    return buttons


async def generate_donors_keyboard(channel_id):
    channels_data = await get_donors_by_user_id(channel_id)
    buttons = []
    for channel_id, channel_name, donor_id, donor_name in channels_data:
        donor_callback_data = f"donor_{donor_id}_{channel_id}"
        donor_button = Button.inline(donor_name, data=donor_callback_data)
        buttons.append([donor_button]) # Both buttons on one line

    add_button_data = f'add_donor_{channel_id}'.encode()
    buttons.append([Button.inline('➕ Add a new donor', add_button_data)])
    buttons.append([Button.inline('⬅️ Return', b'back')])
    return buttons


async def generate_language(channel_id, donor_id):
    buttons = []
    status = await get_channel_languages(channel_id, donor_id)
    status = replace_boolean_with_symbols_language(status)

    button_1 = Button.inline(f'{status["default"]} Dont translate', data=f'language_default_{channel_id}_{donor_id}')
    button_2 = Button.inline(f'{status["Ukranian"]} Ukrainian', data=f'language_Ukranian_{channel_id}_{donor_id}')
    button_3 = Button.inline(f'{status["Russian"]} Russian', data=f'language_Russian_{channel_id}_{donor_id}')
    button_4 = Button.inline(f'{status["English"]} English', data=f'language_English_{channel_id}_{donor_id}')
    button_5 = Button.inline(f'{status["Indian"]} Indian', data=f'language_Indian_{channel_id}_{donor_id}')
    button_6 = Button.inline(f'{status["Italian"]} Italian', data=f'language_Italian_{channel_id}_{donor_id}')
    button_7 = Button.inline(f'{status["Brasilian"]} Brazilian', data=f'language_Brasilian_{channel_id}_{donor_id}')
    button_8 = Button.inline(f'{status["Germany"]} German', data=f'language_Germany_{channel_id}_{donor_id}')
    button_9 = Button.inline(f'{status["Indonesian"]} Indonesian', data=f'language_Indonesian_{channel_id}_{donor_id}')
    button_10 = Button.inline('⬅️ Return', data='back')
    buttons.extend([[button_1], [button_2], [button_3], [button_4], [button_5], [button_6], [button_7], [button_8], [button_9], [button_10]])
    return buttons