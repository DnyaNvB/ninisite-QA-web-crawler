import csv
import re
from bs4 import BeautifulSoup
import requests

TITLE_SUFFIX = " | تبادل نظر نی نی سایت"
NICKNAME_CLASS = "col-xs-9 col-md-12 text-md-center text-xs-right nickname"
POST_COUNT_CLASS = "text-xs-right pull-sm-right pull-md-none text-md-center post-count"
MESSAGE_CLASS = "post-message topic-post__message col-xs-12 fr-view m-b-1 p-x-1"
TOPIC_CLASS = "col-xs-12 date-time p-x-0"
TOPIC_POST_CLASS = "topic-post m-b-1 p-b-0 clearfix"
CSV_HEADERS = ["topic", "visits count for article", "username", "visit count", "message"]
URL = "https://www.ninisite.com/discussion/forum/109/%d8%a7%d9%93%d8%b1%d8%a7%db%8c%d8%b4-%d9%88-%d8%b2%db%8c%d8%a8%d8%a7%d9%8a%d9%94%db%8c?page="
SESSION = requests.Session()


def extract_text(element, class_name, replacements):
    try:
        text = element.find(class_=class_name).text.strip()
        for old, new in replacements:
            text = text.replace(old, new)
        return text
    except AttributeError:
        return None


def scrape(url):
    try:
        response = SESSION.get(url, timeout=5)
        response.raise_for_status()
        return BeautifulSoup(response.content, "html.parser")
    except (requests.exceptions.RequestException, Exception) as e:
        print(f"Failed to scrape {url}: {e}")
        return None


def to_csv(fields, rows, file_name):
    with open(file_name, 'w', encoding="UTF-8", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(fields)
        writer.writerows(rows)


def extract_data(soup):
    topic = soup.find("title").text.replace(TITLE_SUFFIX, '').strip()
    topic_data = soup.find(class_=TOPIC_CLASS)
    visit_count = extract_text(topic_data, "pull-xs-right", [(" بازدید", '')])
    articles = soup.find_all(class_=TOPIC_POST_CLASS)
    return [(topic, visit_count,
            extract_text(user, NICKNAME_CLASS, []),
            extract_text(user, POST_COUNT_CLASS, [("تعداد پست: ", '')]),
            extract_text(user, MESSAGE_CLASS, [])) for user in articles]


def scrape_qa_data(qa_urls):
    return [data for url in qa_urls for data in extract_data(scrape(url))]


def get_qa_urls(base_url):
    return [f"https://www.ninisite.com{link.get('href')}"
            for page_num in range(1, 3)
            for link in scrape(f"{base_url}{page_num}").findAll('a', href=re.compile("/discussion/topic/"))]


if __name__ == "__main__":
    urls = get_qa_urls(URL)
    to_csv(['QA links'], [[url] for url in urls], 'QA_links.csv')
    datas = scrape_qa_data(urls)
    to_csv(CSV_HEADERS, datas, 'crawling_metadata.csv')
