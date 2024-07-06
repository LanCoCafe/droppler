import re

import requests
from bs4 import BeautifulSoup


def extract_links(text: str) -> list[str]:
    pattern = r'https?://[^\s]+'
    links = re.findall(pattern, text)
    return links


def get_social_titles(url: str) -> str:
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            og_title = soup.find('meta', property='og:title')['content'] if soup.find(
                'meta', property='og:title'
            ) else None
            twitter_title = soup.find('meta', property='twitter:title')['content'] if soup.find(
                'meta', property='twitter:title'
            ) else None
            title_tag = soup.title.string if soup.title else None

            # Prioritize the titles: Open Graph, Twitter Card, HTML title tag
            title = og_title or twitter_title or title_tag or 'No title found'
            return title
        else:
            raise Exception(f'Failed to retrieve URL. Status code: {response.status_code}')
    except Exception as e:
        raise Exception(f'Error retrieving or parsing URL: {str(e)}')
