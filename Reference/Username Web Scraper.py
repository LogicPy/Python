import requests
from bs4 import BeautifulSoup

# Make a request to the website
url = 'https://writing.com/browse.php?type=categories&catid=71&offset=30'
response = requests.get(url)

def remove_duplicates(arr):
    # Convert the list into a set
    unique_set = set(arr)
    # Convert the set back into a list
    unique_list = list(unique_set)
    return unique_list

def main():
	# Check if the request was successful
	if response.status_code == 200:
	    # Parsing the HTML content
	    soup = BeautifulSoup(response.content, 'html.parser')

	    # Find all the 'a' tags with specific strings in the href attribute
	    keywords = [a.text for a in soup.find_all('a', href=lambda href: 'uid' in href)]
	    u1 = remove_duplicates(keywords)
	    # Print the keywords
	    for u2 in u1:
	    	print u2
	    #print(keywords)
	else:
	    print('Failed to retrieve data')


main()