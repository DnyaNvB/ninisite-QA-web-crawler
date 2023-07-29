from urllib.error import HTTPError
import requests
from bs4 import BeautifulSoup
import re
import csv


def handle_error(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except ConnectionError as conn_err:
        print(f'Connection error occurred: {conn_err}')
    except TimeoutError as timeout_err:
        print(f'Timeout error occurred: {timeout_err}')
    except requests.exceptions.RequestException as req_err:
        print(req_err)


def to_csv(fields, rows, file_name):
    with open(file_name, 'w', encoding="UTF-8") as f:
        writer = csv.writer(f)
        writer.writerow(fields)
        for row in rows:
            writer.writerow(row)


def scrape(url):
    handle_error(url)
    html = requests.get(url)
    bs = BeautifulSoup(html.content, "html.parser")
    return bs


def extract_text(element, class_name, string_to_replace1, string_to_replace2):
    try:
        return element.find(class_=class_name).text.strip().replace(string_to_replace1, '').replace(string_to_replace2, '')
    except AttributeError:
        return None


def qa_data(qa_url_list):
    for url in qa_url_list:
        soup = scrape(url[0])
        topic = extract_text(soup, "title", " | تبادل نظر نی نی سایت", '')
        topic_data = soup.find(class_="col-xs-12 date-time p-x-0")
        visits_count = extract_text(topic_data, "pull-xs-right", " بازدید", '')
        posts_count = extract_text(topic_data, "pull-xs-right", " پست", '|')
        articles = soup.find_all(class_="topic-post m-b-1 p-b-0 clearfix")

        for article in articles:
            nickname = extract_text(article, "col-xs-9 col-md-12 text-md-center text-xs-right nickname", '', '')
            posts_count_user = extract_text(article, "text-xs-right pull-sm-right pull-md-none text-md-center post-count", "تعداد پست: ", '')
            message = extract_text(article, "post-message topic-post__message col-xs-12 fr-view m-b-1 p-x-1", '', '')
            yield [topic, visits_count, posts_count, nickname, posts_count_user, message]


def qa_urls(url):
    page_num = 1
    qa_url_list = list()
    while page_num <= 2:
        complete_url = url + str(page_num)
        soup = scrape(complete_url)
        for link in soup.findAll('a', href=re.compile("/discussion/topic/")):
            link = "https://www.ninisite.com" + link.get("href")
            qa_url_list.append([link])
        page_num += 1

    return qa_url_list


if __name__ == "__main__":
    URL = "https://www.ninisite.com/discussion/forum/109/%d8%a7%d9%93%d8%b1%d8%a7%db%8c%d8%b4-%d9%88-%d8%b2%db%8c%d8%a8%d8%a7%d9%8a%d9%94%db%8c?page="
    urls = qa_urls(URL)
    to_csv(['QA links'], urls, 'QA_links.csv')
    columns = ["topic", "visits count for article", "post count", "username", "visit count for A", "message"]
    data = list(qa_data(urls))  # Convert generator to list
    to_csv(columns, data, 'crawling_metadata.csv')
