from urllib.error import HTTPError
import requests
from bs4 import BeautifulSoup
import re
import csv


def handle_error(url):
    """Handles errors that may occur when scraping the website.

    Args:
        url (str): The URL of the website to scrape.

    Raises:
        HTTPError: If an HTTP error occurs.
        ConnectionError: If a connection error occurs.
        TimeoutError: If a timeout error occurs.
        requests.exceptions.RequestException: If any other error occurs.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
    except HTTPError as http_err:
        print('HTTP error occurred:  {}'.format(http_err))
    except ConnectionError as conn_err:
        print('Connection error occurred:  {}'.format(conn_err))
    except TimeoutError as timeout_err:
        print('Timeout error occurred:  {}'.format(timeout_err))
    except requests.exceptions.RequestException as req_err:
        print(req_err)


def to_csv(fields, rows, file_name):
    with open(file_name, 'w', encoding="UTF-8") as f:
        writer = csv.writer(f)
        writer.writerow(fields)
        for row in rows:
            writer.writerow(row)


def scrape(url):
    """Scrape the website.

    Args:
        url (str): The URL of the website to scrape.
    """
    handle_error(url)
    html = requests.get(url)
    bs = BeautifulSoup(html.content, "html.parser")
    return bs


def QA_datas(QA_URL_list):
    for url in QA_URL_list:
        soup = scrape(url[0])
        topic = soup.find("title").text.replace(" | تبادل نظر نی نی سایت", '').strip()
        topic_data = soup.find(class_="col-xs-12 date-time p-x-0")
        visits_count = topic_data.find(class_="pull-xs-right").text.strip().replace(" بازدید", '')
        posts_count = topic_data.find_all(class_="pull-xs-right")[1].text.strip().replace(" پست", '').replace('|', '')
        article = soup.find_all(class_="topic-post m-b-1 p-b-0 clearfix")

        data = []
        for user in article:
            # find all columns in each row
            try:
                nickname = user.find(class_="col-xs-9 col-md-12 text-md-center text-xs-right nickname").text.strip()
            except:
                continue
            try:
                posts_count_user = user.find(
                    class_="text-xs-right pull-sm-right pull-md-none text-md-center post-count").text.strip().replace(
                    "تعداد پست: ", '')
            except:
                posts_count_user = None
            try:
                message = user.find(
                    class_="post-message topic-post__message col-xs-12 fr-view m-b-1 p-x-1").text.strip()
            except:
                message = None
            data.append([topic, visits_count, posts_count, nickname, posts_count_user, message])

        return data


def QA_URLs(URL):
    page_num = 1
    QA_URL_list = list()
    while page_num <= 5320:
        URL = URL + str(page_num)
        soup = scrape(URL)
        for link in soup.findAll('a', href=re.compile("/discussion/topic/")):
            link = "https://www.ninisite.com" + link.get("href")
            QA_URL_list.append([link])
        page_num += 1

    return QA_URL_list


if __name__ == "__main__":
    URL = "https://www.ninisite.com/discussion/forum/109/%d8%a7%d9%93%d8%b1%d8%a7%db%8c%d8%b4-%d9%88-%d8%b2%db%8c%d8%a8%d8%a7%d9%8a%d9%94%db%8c?page="
    urls = QA_URLs(URL)
    to_csv(['QA links'], urls, 'QA_links.csv')
    columns = ["topic", "visits count for article", "post count", "username", "visit count for A", "message"]
    datas = QA_datas(urls)
    to_csv(columns, datas, 'crawling_metadatas.csv')
