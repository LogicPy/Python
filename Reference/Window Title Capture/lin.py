
# Window Title Logger
# View Active Window Names
# Wayne Kenney - 2017


# This agent detects the user's current activity and it makes decisions based on that information.
# For example: If the agent detects that the user is browsing YouTube, the agent may react by 
# sending YouTube requests.

# For experimental purposes


import gtk
import wnck
import glib

class WindowTitle(object):
    def __init__(self):
        self.title = None
        glib.timeout_add(100, self.get_title)

    def get_title(self):
        # Globalize title variable
        global title
        try:
            title = wnck.screen_get_default().get_active_window().get_name()
            if self.title != title:
                self.title  = title
                
                # Detects YouTube browsing
                keyw = "YouTube"
                keyw2 = "Twitch"
                keyw3 = "gmail"

                # Keyword Finder ----
                # Detect Specific Web Server
                if title.find(keyw) != -1:
                    print "----------------------------"
                    print " - YouTube Detected! -"
                    print "----------------------------"
                elif title.find(keyw2) != -1:
                    print "----------------------------"
                    print " - Twitch Detected! -"
                    print "----------------------------"
                elif title.find(keyw3) != -1:
                    print "----------------------------"
                    print " - Gmail Detected! -"
                    print "----------------------------" 
                # -------------------

                print "\n%s\n" % (title)
        except AttributeError:
            pass
        return True

# Main function. Other functions are called here..
def Main():
    WindowTitle()
    gtk.main()

# Initial call main
Main()