# NiniSite Beauty & Makeup QA Web Crawler

NiniSite Beauty & Makeup QA Web Crawler is a Python script that crawls the beauty and makeup discussions on the NiniSite forum.

## Description

The crawler navigates through multiple pages of the beauty and makeup section, extracting key information from each discussion. The data extracted includes:
- Discussion Topic
- Visits count for the discussion
- Username
- User's post count
- User's message

All extracted URLs are saved into a file named `QA_links.csv`, and the extracted data is stored in a file named `crawling_metadata.csv`.

## Installation and Setup

To run this script, you need to have Python installed on your machine. If not, you can download it [here](https://www.python.org/downloads/).

You will also need the following Python libraries:
- BeautifulSoup4
- requests

You can install them using pip:

```bash
pip install beautifulsoup4 requests
```
# Usage

You can run the script from the command line as follows:

```bash
python main.py
```
## Contributing

We appreciate your contributions! Please fork this repository and make your changes in a separate branch. Once you're done, open a pull request.

## Bugs and Issues

If you encounter any bugs or issues, please [create an issue](https://github.com/DnyaNvB/ninisite-QA-web-crawler/issues/new) on GitHub.

## Contact

For any questions or concerns, please contact the author at: dnya.nvb@gmail.com
