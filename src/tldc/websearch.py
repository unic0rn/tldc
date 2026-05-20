from ddgs import DDGS
from fetchmd import fetchmd
from .logger import logger


class WebSearch:
    def search(self, query):
        logger(f"Web search query: {query}")
        with DDGS() as ddgs:
            results = []
            for page in ddgs.text(query, region='us-en', safesearch='off', max_results=3):
                href = page.get('href')
                title = page.get('title')
                body = page.get('body')
                results.append({'url': href, 'title': title, 'snippet': body})
                logger(f"Found result: {title}")
            return results

    def fetch_content(self, url):
        logger(f"Fetching content from: {url}")
        try:
            content = fetchmd(url)
            logger(f"Fetched content from: {url}")
            return content
        except Exception as e:
            logger(f"Error fetching content from {url}: {e}")
            return f"Error fetching content from {url}"
