# This file contains utility functions for text processing and integration with OpenAI API
# Libraries include TF-IDF vectorization, word counting, and handling Telegram media.
import emoji
import re
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument, DocumentAttributeVideo
import openai
from colorama import Fore, Back, Style
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from sql import *
from config import OPEN_AI_KEY, language_codes


def format_with_markdown(input_text):
    symbols_to_remove = ['\*\*', '__', '\*', '_']
    for symbol in symbols_to_remove:
        text = re.sub(symbol, '', text)
    print(Fore.RED +f'Removed extra characters Markdown: '  + Style.RESET_ALL, text)
    return text


def replace_boolean_with_symbols(settings: dict) -> dict:
    for key, value in settings.items():
        if value is True:
            settings[key] = "✅"
        else:
            settings[key] = "❌"
    return settings


def replace_boolean_with_symbols_language(settings: dict) -> dict:
    for key, value in settings.items():
        if value == 1:
            settings[key] = "✔️"
        else:
            settings[key] = ""
    return settings


async def get_last_texts(client, channel, amount):
    messages = await client.get_messages(channel, limit=amount)
    texts = []
    for message in messages:
        if message.text:
            texts.append(message.text)
        elif hasattr(message, 'media') and hasattr(message.media, 'caption'):
            texts.append(message.media.caption)
    return texts


def remove_emoji(text):
  characters = list(text)
  for character in characters:
    if emoji.is_emoji(character):
      characters.remove(character)
  return ''.join(characters)


def delete_signature(text, texts):
    signatures = []
    all_lines = '\n'.join(texts)
    all_lines = all_lines.split('\n')
    line_count = {}
    for line in all_lines:
        line = line.strip()
        if line and line != "**" and line != "," and line != "__" and line != "\n":
            if line in line_count:
                line_count[line] += 1
            else:
                line_count[line] = 1
    total_lines = len(texts)
    sorted_lines = sorted(line_count.items(), key=lambda x: x[1], reverse=True)
    for line, count in sorted_lines:
        if count > 0.2 * total_lines:
            signatures.append(line)
    print(Fore.RED + 'Found signatures:' + Style.RESET_ALL, signatures)
    
    # Create a copy of the source text for processing
    text_to_check = text
    for signature in signatures:
        text_to_check = text_to_check.replace(signature, '')
    print(Fore.RED + 'Removed signature:' + Style.RESET_ALL, text_to_check)
    
    return text_to_check


def remove_markdown_inside_hyperlinks(input_text):
    # Replace bold text (symbols **)
    input_text = re.sub(r'\*\*(.*?)\*\*', r'\1', input_text)
    
    def remove_markdown(match):
        markdown_text = match.group(1)
        # Removing all Markdown markup
        markdown_removed = re.sub(r'[*_`~]', '', markdown_text)
        return markdown_removed

    # Removing hyperlinks and Markdown markup inside them
    pattern = r'\[([^\]]+)\]\([^)]+\)'
    result = re.sub(pattern, remove_markdown, input_text)
    result = re.sub(r'[\[\]()]', '', result)
    
    print(Fore.RED + 'Removed hyperlinks' + Style.RESET_ALL, result)
    return result


def get_media_type(event):
    media = event.message.media
    if media is None:
        return None
    if isinstance(media, MessageMediaPhoto):
        return "photo"
    if isinstance(media, MessageMediaDocument):
        for attribute in media.document.attributes:
            if isinstance(attribute, DocumentAttributeVideo):
                return "video"
    return None


def unique_text(input_text, is_emoji_need):
    print(f'I will uniqueize this text: {input_text}')
    if len(input_text) > 5:
        openai.api_key = OPEN_AI_KEY

        if is_emoji_need:
            content_text = "Rephrase the text and add emojis: "
        else:
            content_text = "Paraphrase the text:"
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": content_text},
                {"role": "user", "content": input_text}
            ],
        )
        unique_text = response.choices[0].message['content']
        token_count = response['usage']['total_tokens']
        return unique_text
    else:
        return input_text



def gpt_translate(input_text, language):
    print(f'Translating this text: {input_text}')
    if len(input_text) > 10:
        openai.api_key = OPEN_AI_KEY
        language = language_codes[language]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"When you receive a text you must translate it into {language}."},
                {"role": "user", "content": input_text}
            ],
        )
        unique_text = response.choices[0].message['content']
        return unique_text
    else:
        return input_text
    

async def editing_message_text(user_client, msg, to_channel, from_channel, settings):
    if settings["FilterSignatures"]:
        last_texts_in_channel = await get_last_texts(user_client, from_channel, 50)
        msg = delete_signature(msg, last_texts_in_channel)
        #msg = remove_emoji(msg)
        msg = limit_consecutive_newlines(msg)
    if settings["FilterLinks"]:
        msg = remove_markdown_inside_hyperlinks(msg)
        msg = remove_links(msg)
    if await translate_enable(to_channel, from_channel):
        language = await get_language_with_value_one(to_channel, from_channel)
        msg = gpt_translate(msg, language)
    if settings["UniqueText"]:
        msg = unique_text(msg, settings["UseEmoji"])
        msg = format_with_markdown(msg)
    if  await get_signature(to_channel):
        text, link = await get_signature(to_channel)
        signature = f'[{text}]({link})'
        msg = str(msg) + f'\n\n{signature}'

    return msg


class TextSimilarityDetector:
    def __init__(self, threshold=0.5):
        self.threshold = threshold
        self.vectorizer = TfidfVectorizer(stop_words='english')

    def preprocess_text(self, text):
        # Text preprocessing, for example: removing punctuation, converting to lowercase
        # You can add additional preprocessing steps at your discretion
        return text.lower()

    def calculate_similarity(self, vectors):
        # Calculation of cosine distance between vectors
        similarity_matrix = cosine_similarity(vectors)
        return similarity_matrix[0, 1]

    def is_duplicate(self, text, text_list):
        processed_text = self.preprocess_text(text)
        text_list = [self.preprocess_text(item) for item in text_list]
        
        # Vectorization of all texts using TF-IDF
        all_texts = [processed_text] + text_list
        vectors = self.vectorizer.fit_transform(all_texts)
        
        # Calculate cosine distance for new text only
        similarity_scores = cosine_similarity(vectors[0], vectors[1:])
        
        if np.any(similarity_scores >= self.threshold):
            return True
        return False


async def is_advertisement(text):
    keywords_list = await get_all_keywords()
    for keyword in keywords_list:
        if keyword in text.lower():
            print(keyword)
            return True
    return False


def limit_consecutive_newlines(text):
    lines = text.strip().split('\n')
    new_lines = []
    consecutive_newlines = 0
    
    for line in lines:
        if line.strip():  # Non-empty line
            new_lines.append(line)
            consecutive_newlines = 0
        else:  # Empty line
            consecutive_newlines += 1
            if consecutive_newlines <= 2:
                new_lines.append(line)
    
    modified_text = "\n".join(new_lines)
    print(Fore.RED + f'Removed extra empty lines: ' + Style.RESET_ALL, modified_text)
    return modified_text


def remove_links(text):
    link_pattern = r'https?://[^\s]+'
    result = re.sub(link_pattern, '', text)
    return result