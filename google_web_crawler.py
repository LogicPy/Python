import requests
from bs4 import BeautifulSoup
import requests
from googlesearch import search
import re

def fetch_website_content(url):
   try:
       response = requests.get(url)
       if response.status_code == 200:
           return response.text
   except requests.exceptions.RequestException:
       pass
   return None

def analyze_content(content, directory_pattern):
   # Find all links that match the directory pattern
   links = re.findall(f'href="(?P<url>{directory_pattern})"', content)
   for url in links:
       print(f"Found matching directory: {url}")

import re

def fetch_website_content(url):
  try:
      response = requests.get(url)
      if response.status_code == 200:
          return response.text
  except requests.exceptions.RequestException:
      pass
  return None

def search_and_crawl(keyword, directory_pattern, search_by_keyword):
  if search_by_keyword:
      search_query = keyword
  else:
      search_query = directory_pattern

  for url in search(search_query, num_results=100):
      content = fetch_website_content(url)
      if content:
          print(f"Website content found at: {url}")
          # Analyze the content based on the directory pattern
          # ...

if __name__ == "__main__":
  keyword = "Powered by WordPress & Login"
  directory_pattern = "wp-content/uploads/"
  search_by_keyword = False  # Set to False to search by directory pattern
  search_and_crawl(keyword, directory_pattern, search_by_keyword)



#if __name__ == "__main__":
 #  keyword = "login"
 #  directory_pattern = "wp-login.php"
 #  search_and_crawl(keyword, directory_pattern)
