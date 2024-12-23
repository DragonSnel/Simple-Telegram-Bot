# SQL utility file for interacting with the SQLite database.
# Contains functions for user management and database queries.
import aiosqlite

from config import DATABASE_PATH


async def add_user(user_id, username, first_name):
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        c = await conn.cursor()
        query = '''INSERT OR REPLACE INTO users(user_id, username, first_name) 
                   VALUES(?,?,?)'''
        await c.execute(query, (user_id, username, first_name))
        await conn.commit()


async def is_new_user(user_id):
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        c = await conn.cursor()
        query = '''SELECT user_id FROM users WHERE user_id = ?'''
        await c.execute(query, (user_id,))
        if await c.fetchone() is not None:
            return False
        return True


async def is_new_channel(channel_id):
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        cursor = await conn.cursor()
        query = "SELECT * FROM channels WHERE channel_id = ?"
        await cursor.execute(query, (channel_id,))
        if await cursor.fetchone() is None:
            return True
        return False


async def add_channel(owner, channel_id, name):
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        cursor = await conn.cursor()
        query = "INSERT INTO channels (owner, channel_id, name) VALUES (?, ?, ?)"
        values = (owner, channel_id, name)
        await cursor.execute(query, values)
        await conn.commit()


async def add_channel_to_settings(channel_id, owner, donor_id):
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        cursor = await conn.cursor()
        query = "INSERT INTO donors_settings (channel_id, owner_id, donor_id) VALUES (?, ?, ?)"
        values = (channel_id, owner, donor_id)
        await cursor.execute(query, values)
        await conn.commit()


async def get_channels_by_user_id(user_id):
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        cursor = await conn.cursor()
        query = "SELECT channel_id, name FROM channels WHERE owner = ?"
        await cursor.execute(query, (user_id,))
        result = await cursor.fetchall()
        return result
    

async def get_channels_by_channel_id(channel_id):
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        cursor = await conn.cursor()
        query = "SELECT owner, name FROM channels WHERE channel_id = ?"
        await cursor.execute(query, (channel_id,))
        result = await cursor.fetchone()
        return result
    



async def remove_donor_from_settings_by_channel_and_donor_id(channel_id, donor_id):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.cursor()
        await cursor.execute("DELETE FROM donors_settings WHERE channel_id = ? and donor_id = ?", (channel_id, donor_id))
        await db.commit()


async def remove_donor_from_language_by_channel_and_donor_id(channel_id, donor_id):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.cursor()
        await cursor.execute("DELETE FROM сhannel_language WHERE channel_id = ? and donor_id = ?", (channel_id, donor_id))
        await db.commit()


async def get_channel_settings(channel_id: int, donor_id: int) -> dict:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT * FROM donors_settings WHERE channel_id = ? AND donor_id = ?", (channel_id, donor_id))
        row = await cursor.fetchone()
        if row is None:
            return None  # or perhaps you want to return an error or an empty dictionary
        settings = {
            "autoposting": bool(row[3]),
            "FilterDublicates": bool(row[4]),
            "FilterAds": bool(row[5]),
            "FilterSignatures": bool(row[6]),
            "FilterPhoto": bool(row[7]),
            "FilterVideo": bool(row[8]),
            "FilterAlbums": bool(row[9]),
            "FilterText": bool(row[10]),
            "FilterLinks": bool(row[11]),
            "Translate": bool(row[12]),
            "UniqueText": bool(row[13]),
            "UseEmoji": bool(row[14]),
        }
        return settings
    

async def toggle_column_value(column_name: str, channel_id: int, donor_id: int) -> None:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Getting the current value
        cursor = await db.execute(f"SELECT {column_name} FROM donors_settings WHERE channel_id = ? AND donor_id = ?", (channel_id, donor_id))
        row = await cursor.fetchone()
        if row is None:
            print("Channel not found")
            return
        current_value = row[0]
        new_value = 0 if current_value == 1 else 1
        await db.execute(f"UPDATE donors_settings SET {column_name} = ? WHERE channel_id = ? AND donor_id = ?", (new_value, channel_id, donor_id))
        await db.commit()


async def get_donors_by_user_id(channel_reciever_id):
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        cursor = await conn.cursor()
        query = "SELECT channel_id, channel_name, donor_id, donor_name FROM donors WHERE channel_id = ?"
        await cursor.execute(query, (channel_reciever_id,))
        result = await cursor.fetchall()
        return result
    

async def get_channel_name(channel_id):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT name FROM channels WHERE channel_id = ?", (channel_id,))
        result = await cursor.fetchone()
        await cursor.close()

    # Return the result if found, or None if nothing was found
    if result:
        return result[0]
    else:
        return None
    

async def add_donor(channel_id, channel_name, donor_id, donor_name, owner):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO donors (channel_id, channel_name, donor_id, donor_name, owner)
            VALUES (?, ?, ?, ?, ?)
        """, (channel_id, channel_name, donor_id, donor_name, owner))
        
        await db.commit()
        await cursor.close()


async def is_donor_linked(channel_id, donor_id):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            SELECT * FROM donors
            WHERE channel_id = ? AND donor_id = ?
        """, (channel_id, donor_id))
        
        result = await cursor.fetchone()
        await cursor.close()

    return result is not None


async def delete_donor(channel_id, donor_id):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.cursor()
        await cursor.execute('DELETE FROM donors WHERE channel_id = ? AND donor_id = ?', (channel_id, donor_id))
        await db.commit()


async def get_unique_donor_ids():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT DISTINCT donor_id FROM donors")
        unique_donor_ids = await cursor.fetchall()
        await cursor.close()
        return [donor_id[0] for donor_id in unique_donor_ids]
    

async def get_channels_with_autoposting(donor_id):
    query = '''
        SELECT DISTINCT cs.channel_id
        FROM donors_settings cs
        JOIN donors d ON d.channel_id = cs.channel_id
        WHERE cs.autoposting = 1 AND d.donor_id = ?
    '''
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(query, (donor_id, )) as cursor:
            channel_ids = [row[0] for row in await cursor.fetchall()]
    return channel_ids



async def manage_signatures(channel_id, text):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.cursor()

        # If the text is "D", delete the entry with the given channel_id
        if text == "D":
            await cursor.execute('DELETE FROM signatures WHERE channel_id = ?', (channel_id,))
        else:
            # Split the text by ":", write the first part as text and the second as link
            text_part, link_part = text.split(':', 1)
            await cursor.execute('INSERT OR REPLACE INTO signatures (channel_id, link, text) VALUES (?, ?, ?)',
                                 (channel_id, link_part, text_part))

        await db.commit()
        await cursor.close()


async def get_signature(channel_id):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute('SELECT text, link FROM signatures WHERE channel_id = ?', (channel_id,))
        row = await cursor.fetchone()
        await cursor.close()
        if row is None:
            return False
        return row[0], row[1]
    

async def get_channel_languages(channel_id, donor_id):
    query = f'SELECT * FROM сhannel_language WHERE channel_id = {channel_id} AND donor_id = {donor_id}'
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(query) as cursor:
            row = await cursor.fetchone()
            if row:
                return {desc[0]: value for desc, value in zip(cursor.description, row)}
            else:
                return None
            

async def add_channel_language(channel_id, donor_id):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.cursor()
        await cursor.execute("""
        INSERT INTO сhannel_language (channel_id, donor_id)
        VALUES (?, ?)
        """, (channel_id, donor_id))

        await db.commit()
        await cursor.close()


async def set_channel_language(channel_id, donor_id, selected_language):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.cursor()

        try:
            # First we reset all languages for this channel
            await cursor.execute(f"""
            UPDATE сhannel_language
            SET "default" = 0, "Ukranian" = 0, "Russian" = 0, "English" = 0,
                "Indian" = 0, "Italian" = 0, "Brasilian" = 0,
                "Germany" = 0, "Indonesian" = 0
            WHERE channel_id = ? AND donor_id = ?
            """, (channel_id, donor_id))

            # Then set 1 for the selected language
            await cursor.execute(f"""
            UPDATE сhannel_language
            SET "{selected_language}" = 1
            WHERE channel_id = ? AND donor_id = ?
            """, (channel_id, donor_id))

            await db.commit()
        finally:
            await cursor.close()


async def translate_enable(channel_id, donor_id):
    query = f'SELECT "default", "Ukranian", "Russian", "English", "Indian", "Italian", "Brasilian", "Germany", "Indonesian" FROM сhannel_language WHERE channel_id = ? AND donor_id = ?'

    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(query, (channel_id, donor_id)) as cursor:
            row = await cursor.fetchone()
            if row:
                # Check if there is at least one language (except "default") with value 1
                for column, value in zip(cursor.description, row):
                    column_name = column[0]
                    if column_name != 'default' and value == 1:
                        return True
            return False
        

async def get_language_with_value_one(channel_id, donor_id):
    query = f'SELECT "default", "Ukranian", "Russian", "English", "Indian", "Italian", "Brasilian", "Germany", "Indonesian" FROM сhannel_language WHERE channel_id = ?  AND donor_id = ?'

    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(query, (channel_id, donor_id)) as cursor:
            row = await cursor.fetchone()
            if row:
                # Loop through column names and values, returning the column name if its value is 1
                for column, value in zip(cursor.description, row):
                    column_name = column[0]
                    if column_name != 'default' and value == 1:
                        return column_name
            return None  # Return None if no column with value 1 is found


async def new_ad_keyword(keyword):
    # Opening a connection to the database
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Creating a cursor for executing SQL queries
        async with db.cursor() as cursor:
            # Execute an SQL query to insert a keyword
            await cursor.execute("INSERT INTO ads_keywords (keyword) VALUES (?)", (keyword,))
            # Save changes
            await db.commit()


async def get_all_keywords():
    keywords = []

    # Opening a connection to the database
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Creating a cursor for executing SQL queries
        async with db.cursor() as cursor:
            # We execute an SQL query to select all words in the "keyword" column
            await cursor.execute("SELECT keyword FROM ads_keywords")
            # We get all the rows of the query result
            rows = await cursor.fetchall()
            # We go through the lines and extract keywords
            for row in rows:
                keyword = row[0]
                keywords.append(keyword)

    return keywords


async def get_donor_name(donor_id):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT donor_name FROM donors WHERE donor_id = ?", (donor_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return row["donor_name"]
            else:
                return None
            

async def check_autoposting(channel_id, donor_id):
    query = '''
        SELECT autoposting
        FROM donors_settings
        WHERE channel_id = ? AND donor_id = ?
    '''
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(query, (channel_id, donor_id)) as cursor:
            row = await cursor.fetchone()
            if row and row['autoposting'] == 1:
                return True
            else:
                return False
            

async def delete_all_from_channels_by_channel_id(channel_id):
    query = '''
        DELETE FROM channels
        WHERE channel_id = ?
    '''
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(query, (channel_id,))
        await db.commit()


async def delete_all_from_donors_by_channel_id(channel_id):
    query = '''
        DELETE FROM donors
        WHERE channel_id = ?
    '''
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(query, (channel_id,))
        await db.commit()


async def delete_all_from_donors_settings_by_channel_id(channel_id):
    query = '''
        DELETE FROM donors_settings
        WHERE channel_id = ?
    '''
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(query, (channel_id,))
        await db.commit()


async def delete_all_from_signature_by_channel_id(channel_id):
    query = '''
        DELETE FROM signatures
        WHERE channel_id = ?
    '''
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(query, (channel_id,))
        await db.commit()


async def delete_all_from_channel_languages_by_channel_id(channel_id):
    query = '''
        DELETE FROM сhannel_language
        WHERE channel_id = ?
    '''
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(query, (channel_id,))
        await db.commit()