import re

import requests
from bs4 import BeautifulSoup
from langchain_core.language_models import BaseChatModel
from pydantic import Field, BaseModel


class NewsScore(BaseModel):
    exaggerate: int = Field(ge=0, le=10, description="Between 0~10")  # 誇大性
    clickbait: int = Field(ge=0, le=10, description="Between 0~10")  # 誘餌式標題
    misleading: int = Field(ge=0, le=10, description="Between 0~10")  # 標題誤導性
    controversy: int = Field(ge=0, le=10, description="Between 0~10")  # 爭議性
    piggyback: int = Field(ge=0, le=10, description="Between 0~10")  # 蹭熱度
    inflammatory: int = Field(ge=0, le=10, description="Between 0~10")  # 煽動性
    reason: str = Field(description="The reason why the news title got this score in Traditional Chinese under 100 characters.")  # 理由


def get_news_score(model: BaseChatModel, title: str) -> NewsScore:
    structured_model = model.with_structured_output(NewsScore)

    result = structured_model.invoke(title)

    print(result)

    return NewsScore.model_validate(result)


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
