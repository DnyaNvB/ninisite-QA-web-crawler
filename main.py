from urllib.error import HTTPError
import requests


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


def QA_links(webpage_URLs):
    return NotImplemented


def get_webpage_URLs():
    page_nom = 1
    webpage_urls = list()
    while page_nom <= 28:
        if page_nom == 1:
            URL = "https://roocket.ir/tag/%D9%BE%D8%A7%DB%8C%D8%AA%D9%88%D9%86?type=questions#tag-page"
        else:
            URL = f'https://roocket.ir/tag/%D9%BE%D8%A7%DB%8C%D8%AA%D9%88%D9%86?type=questions&page={page_nom}#tag-page'
        webpage_urls.append(URL)
        page_nom += 1
    return webpage_urls


if __name__ == "__main__":
    urls = get_webpage_URLs()
    QA_links(urls)
