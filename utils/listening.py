import random

from database.query import Query
from database.connection import Connection


def randomize_query_result(cursor):
    if len(cursor) == 1:
        return cursor[0][0]

    last_cursor = len(cursor) - 1
    random_cursor = random.randint(0, last_cursor)
    return cursor[random_cursor][0]


async def get_audio_from_speech(speech, query_table, query_col):
    conn = Connection()
    query = Query(conn)

    if speech:
        transcription = speech.split(' ')

        for idx, word in enumerate(transcription):
            # Not enough words to sentence
            if len(transcription) - idx < 3:
                break

            sentence = word + ' ' + transcription[idx + 1] + ' ' + transcription[idx + 2]
            query_result = query.query_all(
                table=query_table,
                column=query_col,
                where_col='validation',
                value=sentence
            )
            if query_result:
                conn.close()
                return randomize_query_result(query_result)

    conn.close()
    # Nothing found in database or speech not recognized
    return False


async def get_audio_from_tag(query_table, query_col, tag):
    conn = Connection()
    query = Query(conn)

    query_result = query.query_all(
        table=query_table,
        column=query_col,
        where_col='tag',
        value=tag
    )

    if query_result:
        conn.close()
        return randomize_query_result(query_result)

    conn.close()
    return False
