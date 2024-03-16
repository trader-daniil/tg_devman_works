import os
from dotenv import load_dotenv
import requests
import time
import telegram
import logging


DEVMAN_REVIEWS_URL = 'https://dvmn.org/api/user_reviews/'
DEVMAN_REVIEWS_LONGPOLLING_URL = 'https://dvmn.org/api/long_polling/'


def send_message(bot_token, chat_id, message):
    bot = telegram.Bot(token=bot_token)
    bot.send_message(
        text=message,
        chat_id=chat_id,
    )

def get_user_reviews(devman_token, timestamp=''):
    headers={
        'Authorization': f'Token {devman_token}',
    }
    params = {
        'timestamp': timestamp,
    }
    response = requests.get(
        url=DEVMAN_REVIEWS_LONGPOLLING_URL,
        headers=headers,
        params=params,
    )
    response.raise_for_status()
    return response.json()
    
def parse_work_result(work_result):
    if work_result['is_negative']:
        return (f'Переделайте работу {work_result["lesson_title"]}'
                f' ссылка - {work_result["lesson_url"]}')
    return f'Вы сдали работу {work_result["lesson_title"]} ссылка - {work_result["lesson_url"]}'

def main():
    load_dotenv()
    devman_token = os.getenv('DEVMAN_TOKEN')
    tg_bot_token = os.getenv('TG_BOT_TOKEN')
    tg_chat_id = os.getenv('TG_CHAT_ID')
    current_timestamp = time.time()
    while True:
        try:
            result = get_user_reviews(
                devman_token=devman_token,
                timestamp=current_timestamp,
            )
        except requests.exceptions.ReadTimeout:
            logging.error('time out, try again')
            continue
        except requests.ConnectionError:
            logging.error('connection error try again')
            continue
        if result['status'] == 'timeout':
            current_timestamp=result['timestamp_to_request']
            continue
        result = parse_work_result(work_result=result['new_attempts'][0])
        send_message(
            bot_token=tg_bot_token,
            chat_id=tg_chat_id,
            message=result,
        )
        current_timestamp = time.time()

if __name__ == '__main__':
    main()