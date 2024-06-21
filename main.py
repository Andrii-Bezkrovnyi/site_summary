import csv
import os
import time

import cloudscraper
import openai
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from loguru import logger

load_dotenv()
logger.add("logs_info.log", level="INFO", format="{time} - {level} - {message}")

# Set the OpenAI API key from the environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')
BASE_URL = 'https://theater.kyiv.ua/'


def fetch_pages(base_url):
    """
        Fetches all pages from the given base URL.

        Args:
            base_url (str): The base URL of the website to fetch pages from.

        Returns:
            list: A list of full URLs of the pages found on the website.
    """
    scraper = cloudscraper.create_scraper()
    response = scraper.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    pages = []
    for link in soup.find_all('a', href=True):
        page_url = link['href']
        if page_url.startswith('/'):
            page_url = base_url + page_url
        if page_url.startswith('http'):
            pages.append(page_url)

    return pages


def split_text(text, max_length):
    """
    Splits the text into chunks of a specified maximum length.

    Args:
        text (str): The text to be split.
        max_length (int): The maximum length of each chunk.

    Returns:
        list: A list of text chunks.
    """
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]


def generate_summary(text, retries=3):
    """
    Generates a summary of the given text using the OpenAI API.

    Args:
        text (str): The text to summarize.
        retries (int): The number of retries in case of rate limiting.

    Returns:
        str: The generated summary.
    """
    summaries = []
    for part in split_text(text, 2000):
        for _ in range(retries):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system",
                         "content": "Generate a summary about the website based on the following text:"},
                        {"role": "user", "content": part}
                    ],
                    max_tokens=500
                )
                summary = response['choices'][0]['message']['content'].strip()
                summaries.append(summary)
                break
            except openai.error.RateLimitError:
                logger.info("Rate limit exceeded, retrying...")
                time.sleep(10)  # Затримка перед повтором запиту
            except openai.error.InvalidRequestError as err:
                logger.info(f"Error: {err}")
                break
    return " ".join(summaries)


def fetch_page_content(url):
    """
    Fetches the content of the page at the given URL.

    Args:
        url (str): The URL of the page to fetch.

    Returns:
        str: The HTML content of the page.
    """
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url)
    return response.text


def extract_meta_tags(html):
    """
    Extracts meta tags from the given HTML content.

    Args:
        html (str): The HTML content to extract meta tags from.

    Returns:
        dict: A dictionary of meta tag names and their content.
    """
    soup = BeautifulSoup(html, 'html.parser')
    meta_tags = {}
    for meta in soup.find_all('meta'):
        if 'name' in meta.attrs:
            meta_tags[meta['name']] = meta.get('content', '')
    return meta_tags


def create_csv(pages, summary):
    """
    Creates a CSV file with advertisement data based on the given pages and summary.

    Args:
        pages (list): A list of page URLs.
        summary (str): The summary text to be used in the ads.
    """
    with open('google_ads.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Campaign', 'Ad Group', 'Headline 1', 'Headline 2', 'Description', 'Final URL'])

        for page in pages:
            html = fetch_page_content(page)
            meta_tags = extract_meta_tags(html)
            campaign = meta_tags.get('og:site_name', 'Theater Kyiv')
            ad_group = campaign
            headline1 = meta_tags.get('og:title', 'Visit our theater')
            headline2 = 'Book your tickets now'
            description = summary
            final_url = page
            writer.writerow([campaign, ad_group, headline1, headline2, description, final_url])


def main():
    """
    Main function to orchestrate fetching pages, generating summary, and creating the CSV file.
    """
    logger.info(f"Fetching pages from {BASE_URL}...")
    pages = fetch_pages(BASE_URL)

    logger.info("Generating summary...")
    example_text = fetch_page_content(BASE_URL)
    summary = generate_summary(example_text)

    logger.info("Creating CSV file...")
    create_csv(pages, summary)

    logger.info("CSV file 'google_ads.csv' created successfully.")


if __name__ == "__main__":
    main()
