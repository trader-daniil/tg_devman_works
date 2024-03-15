import os
from dotenv import load_dotenv
import requests


DEVMAN_REVIEWS_URL = 'https://dvmn.org/api/user_reviews/'


def get_user_reviews(devman_token):
    headers={
        'Authorization': f'Token {devman_token}',
    }
    response = requests.get(
        url=DEVMAN_REVIEWS_URL,
        headers={'Authorization': f'Token {devman_token}'},
    )
    response.raise_for_status()
    return response.json()

def main():
    load_dotenv()
    devman_token = os.getenv('DEVMAN_TOKEN')
    print(get_user_reviews(devman_token=devman_token))

if __name__ == '__main__':
    main()