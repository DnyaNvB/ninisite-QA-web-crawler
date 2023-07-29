import requests
from bs4 import BeautifulSoup
import re
import csv

session = requests.Session()


def to_csv(fields, rows, file_name):
    with open(file_name, 'w', encoding="UTF-8") as f:
        writer = csv.writer(f)
        writer.writerow(fields)
        for row in rows:
            writer.writerow(row)


def scrape(url):
    try:
        response = session.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.content, "html.parser")
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")


def extract_text(element, class_name, replacements):
    try:
        text = element.find(class_=class_name).text.strip()
        for old, new in replacements:
            text = text.replace(old, new)
        return text
    except AttributeError:
        return None


def QA_data(QA_URL_list):
    for url in QA_URL_list:
        soup = scrape(url[0])
        topic = soup.find("title").text.replace(" | تبادل نظر نی نی سایت", '').strip()
        topic_data = soup.find(class_="col-xs-12 date-time p-x-0")
        visit_count = extract_text(topic_data, "pull-xs-right", [(" بازدید", '')])
        article = soup.find_all(class_="topic-post m-b-1 p-b-0 clearfix")
        data = list()
        for user in article:
            nickname = extract_text(user, "col-xs-9 col-md-12 text-md-center text-xs-right nickname", [])
            posts_count = extract_text(user, "text-xs-right pull-sm-right pull-md-none text-md-center post-count",
                                            [("تعداد پست: ", '')])
            message = extract_text(user, "post-message topic-post__message col-xs-12 fr-view m-b-1 p-x-1", [])
            data.append([topic, visit_count, nickname, posts_count, message])
        return data


def QA_URLs(url):
    QA_URL_list = []
    for page_num in range(1, 3):
        complete_url = url + str(page_num)
        soup = scrape(complete_url)
        for link in soup.findAll('a', href=re.compile("/discussion/topic/")):
            QA_URL_list.append(["https://www.ninisite.com" + link.get("href")])
    return QA_URL_list


if __name__ == "__main__":
    URL = "https://www.ninisite.com/discussion/forum/109/%d8%a7%d9%93%d8%b1%d8%a7%db%8c%d8%b4-%d9%88-%d8%b2%db%8c%d8%a8%d8%a7%d9%8a%d9%94%db%8c?page="
    urls = QA_URLs(URL)
    to_csv(['QA links'], urls, 'QA_links.csv')
    columns = ["topic", "visits count for article", "username", "visit count", "message"]
    datas = QA_data(urls)
    to_csv(columns, datas, 'crawling_metadata.csv')
