import requests
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
import os

def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def get_all_website_links(url):
    urls = set()
    domain_name = urlparse(url).netloc
    rp = RobotFileParser()
    rp.set_url(f"{url}/robots.txt")
    rp.read()
    if rp.can_fetch("*", url):
        urls = set()
        soup = BeautifulSoup(requests.get(url).content, "html.parser")

        for a_tag in soup.findAll("a"):
            href = a_tag.attrs.get("href")
            if href == "" or href is None:
                continue
            href = urljoin(url, href)
            parsed_href = urlparse(href)
            href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
            if not is_valid(href):
                continue
            if href in urls:
                continue
            if domain_name not in href:
                continue
            urls.add(href)

        return urls
    else:
        return None

def print_and_save_directories(dir_map, output_file):
    with open(output_file, "w") as f:
        for directory in dir_map:
            f.write(directory + "\n")
    print("Directories mapped and saved to file!")
    print(f"All directories saved to {output_file}")

def main():
    user_input = input("Enter the web server URL: ")
    dir_map = set()
    visited_set = set()

    def recursive(directory):
        nonlocal dir_map
        nonlocal visited_set
        visited_set.add(directory)

        for link in get_all_website_links(directory):
            if link not in visited_set:
                recursive(link)
            if link[-1] == "/":
                dir_map.add(link)
            else:
                dir_map.add(link + "/")

    recursive(user_input)
    print_and_save_directories(dir_map, "directories.txt")

if __name__ == "__main__":
    main()
