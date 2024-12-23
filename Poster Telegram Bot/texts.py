# This file contains text templates for the bot's messages.
# Templates use placeholders for dynamic content insertion.
start = "👋🏼 Greetings!\n\n\
🔻Use the buttons below to manage channels:"

add_channel = '📢 Send me a message from a channel where the bot is an administrator:'

have_access_to_post_on_channel = '✅ Channel <b>{}</b> successfully added to auto-posting!'

dont_have_access_to_post_on_channel = '❗️ The bot cannot post to <b>{}</b>!'

reply_is_not_from_channel = '📢 Please forward the message only from the channel!'

autoposting_message_to_channel = '✅ Auto-posting enabled!'


channel_already_exist = '❗️ This channel is already used for auto-posting!'

channel_info = '📢 Channel: {}\n\
👤 Owner: {}\n\n\
⚙️ Donors of the channel: '

donors_channels = '🔍 Donor channels for publications:'

add_donor = '📢 Send me a message from the donor channel: '

channel_private_error = '⛔️ This is a private channel and the bot does not have access to create posts!'

donor_already_added = '❗️ This donor is already connected to this channel!'

success_added_donor = '✅ Donor <b>{}</b> successfully added for the channel <b>{}</b>.'

add_signatures = 'Enter the text and link of the new signature:\n\n\
Example:\n\
Subscribe to our channel:https://t.me/your_channel\n\n\
Enter "**D**" to delete the signature completely.'

signature_success_added = 'The signature for this channel has been successfully updated!'

signature_error = 'This format is not suitable!'

select_language = 'Select the language into which all posts will be translated:'

ad_keyword_added = '"**{}**" - now in the list of advertising filters.'

donors_settings = 'Donor settings:\n\n\
Donor name: **{}**\n\n\
ID: **{}**'


MESSAGES = {
    'start': start,
    'add_channel' : add_channel,
    'have_access_to_post_on_channel': have_access_to_post_on_channel,
    'dont_have_access_to_post_on_channel': dont_have_access_to_post_on_channel,
    'reply_is_not_from_channel': reply_is_not_from_channel,
    'autoposting_message_to_channel': autoposting_message_to_channel,
    'channel_already_exist': channel_already_exist,
    'channel_info': channel_info,
    'donors_channels': donors_channels,
    'add_donor': add_donor,
    'channel_private_error': channel_private_error,
    'donor_already_added': donor_already_added,
    'success_added_donor': success_added_donor,
    'add_signatures': add_signatures,
    'signature_success_added': signature_success_added,
    'signature_error': signature_error,
    'select_language': select_language,
    'ad_keyword_added': ad_keyword_added,
    'donors_settings': donors_settings
}