import os
from dotenv import load_dotenv
import requests
import time
import telegram
import logging


DEVMAN_REVIEWS_URL = 'https://dvmn.org/api/user_reviews/'
DEVMAN_REVIEWS_LONGPOLLING_URL = 'https://dvmn.org/api/long_polling/'


logger = logging.getLogger('bot')

class TelegramLogHandler(logging.Handler):

    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.tg_bot = tg_bot
        self.chat_id = chat_id

    def emit(self, record):
        log_entry = self.format(record=record)
        self.tg_bot.send_message(
            chat_id=self.chat_id,
            text=log_entry,
        )

def get_user_reviews(devman_token, timestamp=None, timeout=None):
    headers = {
        'Authorization': f'Token {devman_token}',
    }
    params = {
        'timestamp': timestamp,
    }
    response = requests.get(
        url=DEVMAN_REVIEWS_LONGPOLLING_URL,
        headers=headers,
        params=params,
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()


def parse_work_result(work_result):
    if work_result['is_negative']:
        return (f'Переделайте работу {work_result["lesson_title"]}'
                f' ссылка - {work_result["lesson_url"]}')
    return (f'Вы сдали работу {work_result["lesson_title"]} '
            f'ссылка - {work_result["lesson_url"]}')


def main():
    load_dotenv()
    devman_token = os.getenv('DEVMAN_TOKEN')
    tg_bot_token = os.getenv('TG_BOT_TOKEN')
    tg_chat_id = os.getenv('TG_CHAT_ID')
    bot = telegram.Bot(token=tg_bot_token)
    logger.setLevel(logging.WARNING)
    logger.addHandler(TelegramLogHandler(
        tg_bot=bot,
        chat_id=tg_chat_id,
    ))
    current_timestamp = time.time()
    seconds_to_sleep = 2

    while True:
        try:
            result = get_user_reviews(
                devman_token=devman_token,
                timestamp=current_timestamp,
                timeout=seconds_to_sleep,
            )
        except requests.exceptions.ReadTimeout:
            logger.debug('time out, try again')
            continue
        except requests.ConnectionError:
            logger.error('Connection error, try again')
            time.sleep(seconds_to_sleep)
            continue
        except Exception as e:
            logger.error(e)
            time.sleep(seconds_to_sleep)
            continue
        if result['status'] == 'timeout':
            current_timestamp=result['timestamp_to_request']
            continue
        result = parse_work_result(work_result=result['new_attempts'][0])
        bot.send_message(
            text=result,
            chat_id=tg_chat_id,
        )
        current_timestamp = time.time()


if __name__ == '__main__':
    main()
