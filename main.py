import csv
import re
from bs4 import BeautifulSoup
import requests

# Constants to use in script
TITLE_SUFFIX = " | تبادل نظر نی نی سایت"
NICKNAME_CLASS = "col-xs-9 col-md-12 text-md-center text-xs-right nickname"
POST_COUNT_CLASS = "text-xs-right pull-sm-right pull-md-none text-md-center post-count"
MESSAGE_CLASS = "post-message topic-post__message col-xs-12 fr-view m-b-1 p-x-1"
TOPIC_CLASS = "col-xs-12 date-time p-x-0"
TOPIC_POST_CLASS = "topic-post m-b-1 p-b-0 clearfix"
EXTRA_INF = r"https?://?[^/]*ninisite[^/]*/[^/]+/[^/]+/|https?://?[^/]*/ninisite[^/]*/[^/]+/[^/]+/[^/]+/"
CSV_HEADERS = ["Discussion Topic", "Visits count for the discussion", "Username", "User's post count", "User's message"]
URL = "https://www.ninisite.com/discussion/forum/109/%d8%a7%d9%93%d8%b1%d8%a7%db%8c%d8%b4-%d9%88-%d8%b2%db%8c%d8%a8%d8%a7%d9%8a%d9%94%db%8c?page="
SESSION = requests.Session()


def extract_text(element, class_name, replacements):
    """
       Extracts the text from an HTML element and performs any specified replacements.

       Args:
           element (bs4.element.Tag): The HTML element to extract text from.
           class_name (str): The CSS class of the element.
           replacements (List[Tuple[str, str]]): A list of tuples where each tuple
               contains a string to find and a string to replace it with.

       Returns:
           str: The cleaned text, or None if the element does not exist.
       """
    try:
        text = element.find(class_=class_name).text.strip()
        for old, new in replacements:
            text = text.replace(old, new)
        return text
    except AttributeError:
        return None


def scrape(url):
    """
       Sends a GET request to the specified URL and parses the content as HTML.

       Args:
           url (str): The URL to scrape.

       Returns:
           bs4.BeautifulSoup: The parsed HTML, or None if the request fails.
       """
    try:
        response = SESSION.get(url, timeout=5)
        response.raise_for_status()
        return BeautifulSoup(response.content, "html.parser")
    except (requests.exceptions.RequestException, Exception) as e:
        print(f"Failed to scrape {url}: {e}")
        return None


def to_csv(fields, rows, file_name):
    """
        Writes the specified rows of data to a new CSV file.

        Args:
            fields (List[str]): The header row of the CSV file.
            rows (List[List[any]]): The data to write to the CSV file.
            file_name (str): The name of the file to write.
        """
    with open(file_name, 'w', encoding="UTF-8", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(fields)
        writer.writerows(rows)


def extract_data(soup):
    """
        Extracts relevant data from a BeautifulSoup object representing a page of articles.

        Args:
            soup (bs4.BeautifulSoup): The parsed HTML.

        Returns:
            List[Tuple[str, str, str, str, str]]: A list of tuples where each tuple contains
                the topic, visit count, username, visit count, and message.
        """
    topic = None
    title = soup.find("title")
    if title:
        topic = re.sub(r"صفحه \d+", '', title.text.replace(TITLE_SUFFIX, '').strip())
    topic_data = soup.find(class_=TOPIC_CLASS)
    visit_count = extract_text(topic_data, "pull-xs-right", [(" بازدید", '')])
    articles = soup.find_all(class_=TOPIC_POST_CLASS)
    return [(topic, visit_count,
             extract_text(user, NICKNAME_CLASS, []),
             extract_text(user, POST_COUNT_CLASS, [("تعداد پست: ", '')]),
             re.sub(EXTRA_INF, '', extract_text(user, MESSAGE_CLASS, [])))
            for user in articles]


def scrape_qa_data(qa_urls):
    """
        Scrapes data from all QA pages.

        Args:
            qa_urls (List[str]): A list of URLs to QA pages.

        Returns:
            List[Tuple[str, str, str, str, str]]: A list of tuples where each tuple contains
                the topic, visit count, username, visit count, and message.
        """
    return [data for url in qa_urls for data in extract_data(scrape(url))]


def get_qa_urls(base_url, max_pages=2):
    """
        Builds a list of QA URLs by iterating through the pages of a base URL.

        Args:
            base_url (str): The base URL to start from.
            max_pages (int, optional): The maximum number of pages to process. Defaults to 2.

        Returns:
            List[str]: A list of QA URLs.
        """
    return [f"https://www.ninisite.com{link.get('href')}"
            for page_num in range(1, max_pages + 1)
            for link in scrape(f"{base_url}{page_num}").findAll('a', href=re.compile("/discussion/topic/"))]


if __name__ == "__main__":
    # Entry point of the script
    urls = get_qa_urls(URL)
    to_csv(['QA links'], [[url] for url in urls], 'QA_links.csv')
    datas = scrape_qa_data(urls)
    to_csv(CSV_HEADERS, datas, 'crawling_metadata.csv')
