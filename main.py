import requests
from bs4 import BeautifulSoup
import re
import csv
from concurrent.futures import ThreadPoolExecutor

session = requests.Session()


def to_csv(fields, rows, file_name):
    """
    Writes the provided data into a CSV file.

    Args:
        fields (list): The column headers of the CSV.
        rows (list): A list of lists, where each sublist is a row.
        file_name (str): The name of the file to write to.
    """
    with open(file_name, 'w', encoding="UTF-8") as f:
        writer = csv.writer(f)
        writer.writerow(fields)
        for row in rows:
            writer.writerow(row)


def make_soup(html_content):
    """
    Parses the HTML content into a BeautifulSoup object.

    Args:
        html_content (str): The HTML content to parse.

    Returns:
        BeautifulSoup: A BeautifulSoup object parsed from the HTML content.
    """
    return BeautifulSoup(html_content, "html.parser")


def scrape(url):
    """
    Sends a GET request to the given URL and returns its content.

    Args:
        url (str): The URL to send the request to.

    Returns:
        str: The content of the response.

    Raises:
        requests.exceptions.RequestException: If an error occurs during the request.
    """
    try:
        response = session.get(url)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(e)


def extract_text(element, class_name, string_to_replace1, string_to_replace2):
    """
    Extracts and returns the text from an HTML element with the given class name.

    Args:
        element (bs4.element.Tag): The HTML element to extract text from.
        class_name (str): The class name of the HTML element.

    Returns:
        str: The extracted text.
    """
    try:
        return element.find(class_=class_name).text.strip().replace(string_to_replace1, '').replace(string_to_replace2,
                                                                                                    '')
    except AttributeError:
        return None


def extract_data(url):
    """
    Extracts and yields data from the given URL.

    Args:
        url (str): The URL to extract data from.
    """
    html_content = scrape(url)
    soup = make_soup(html_content)
    topic = extract_text(soup, "title", " | تبادل نظر نی نی سایت", '')
    topic_data = soup.find(class_="col-xs-12 date-time p-x-0")
    visits_count = extract_text(topic_data, "pull-xs-right", " بازدید", '')
    article = soup.find_all(class_="topic-post m-b-1 p-b-0 clearfix")
    data = list()
    for user in article:
        nickname = extract_text(user, "col-xs-9 col-md-12 text-md-center text-xs-right nickname", '', '')
        post_count = extract_text(user, "text-xs-right pull-sm-right pull-md-none text-md-center post-count",
                                  "تعداد پست: ", '')
        message = extract_text(user, "post-message topic-post__message col-xs-12 fr-view m-b-1 p-x-1", '', '')
        data.append([topic, visits_count, nickname, post_count, message])
    return data


def qa_urls(url, max_pages=2):
    """
    Creates and returns a list of URLs from the base URL and the number of pages.

    Args:
        url (str): The base URL.
        max_pages (int): The number of pages to create URLs from.

    Returns:
        list: A list of created URLs.
    """
    qa_url_list = []
    for page_num in range(1, max_pages + 1):
        complete_url = f"{url}{page_num}"
        html_content = scrape(complete_url)
        soup = make_soup(html_content)
        for link in soup.findAll('a', href=re.compile("/discussion/topic/")):
            link = "https://www.ninisite.com" + link.get("href")
            qa_url_list.append([link])

    return qa_url_list


if __name__ == "__main__":
    URL = "https://www.ninisite.com/discussion/forum/109/%d8%a7%d9%93%d8%b1%d8%a7%db%8c%d8%b4-%d9%88-%d8%b2%db%8c%d8%a8%d8%a7%d9%8a%d9%94%db%8c?page="
    urls = qa_urls(URL)  # Obtain all QA urls
    to_csv(['QA links'], urls, 'QA_links.csv')  # Save the QA urls to CSV
    columns = ["topic", "visits count for article", "post count", "username", "visit count for A", "message"]
    results = None
    # Extract data concurrently from all urls
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(extract_data, (url[0] for url in urls))

    # data = [item for sublist in results for item in sublist]
    to_csv(columns, results, 'crawling_metadata.csv')  # Save the extracted data to CSV
