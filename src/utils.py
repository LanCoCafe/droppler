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
    
def parse_news_url(url: str) -> dict[str, str]:
    """
    Parses a URL to extract Open Graph (OG) title and description.

    This function attempts to retrieve the OG title and description from a given URL. 
    It does this by making an HTTP GET request and parsing the HTML content using BeautifulSoup.

    Args:
        url (str): The URL to parse.

    Returns:
        dict[str, str]: A dictionary containing the following keys:
            * 'og_title': The Open Graph title of the URL (if found).
            * 'og_description': The Open Graph description of the URL (if found).

    Raises:
        Exception: If there is an error retrieving or parsing the URL. The exception message 
            will include the original exception and the status code (if applicable).
    """
    try:    
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            og_description = soup.find('meta', property='og:description')['content'] if soup.find(
                'meta', property='og:description'
            ) else None
            return og_description
        else:
            raise Exception(f'Failed to retrieve URL. Status code: {response.status_code}')
    except Exception as e:
        raise Exception(f'Error retrieving or parsing URL: {str(e)}')
        
