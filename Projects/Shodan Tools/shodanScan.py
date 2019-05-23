import sys
import requests
from time import sleep

# Find between page tags on page.
def find_between( s, tag1, tag2 ):
    #print "n is " + n
    try:
        start = s.index( tag1 ) + len( tag1 )
        end = s.index( tag2, start )
        return s[start:end]
    except ValueError:
        return ""

def main():
	n = 0

	while(True):
	    # Enter the command 'go' to start
		cmd = raw_input("Enter Command: ")
		if cmd == "go":
			print "go!"
	        	# Go to this page for page item gathering.
			response = requests.get("https://www.shodan.io/search?query=Server%3A+SQ-WEBCAM")

			# Response anchor [1]
			text_to_search = response.content
			while(True):
				# Find between value of 'x' sources between two tags
				x = find_between(text_to_search, '/></a><a href="/host/', '</a>')
				if not x:
					break

			    # Wait one second before continuing...
				sleep(1)

			    # Increment 'n' for index value of item on page
				n = n + 1

			    # Display find_between data in 'x'
				print "\nindex: %s\n\n%s\n" % (n, x)

			    # Remove text already searched [2]
				found_text_pos = text_to_search.index(x) + len(x)
				text_to_search = text_to_search[found_text_pos:]
		else:
			print "\nInvalid command...\n"

main()