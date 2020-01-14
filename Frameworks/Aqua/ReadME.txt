  _____                 ___     ___ 
 |  _  |___ _ _ ___ ___|_  |   |   |
 |     | . | | | .'|___|_| |_ _| | |
 |__|__|_  |___|__,|   |_____|_|___|
         |_|     
- Authenticate Query Unification Application

Coded by: Wayne
Date: 10/22/2015

--Feel free to use/integrate into your projects!--

Here's a general framework for utilizing some of the features of the HTTP headers module with simplicity.

Getting Started!

Editing will occur in 'Frame.py'. Currently the framework is configured to Newgrounds.com,

-  Configuration Part 1 (Config Variables):

The configuration task is simple. The purpose of this tool is to enable POST form authentication and data extraction/manipulation with ease. You will notice the pre-declared set of variabales:

	Service = 'Newgrounds - Login'
	login_URL = 'https://www.newgrounds.com/passport/mode/iframe/apps..'
	landing = 'http://www.newgrounds.com/bbs'
	keyword = 'loggedin'

The 'Service' variable is simply used as a display text when a user opens the console. It will elucidate the service being accessed with the framework to the user.

The 'login_URL' is simply the url directed upon POST login. 

The 'landing' variable contains a location on the server you want to direct the user after a successful authentication.

The 'keyword' variable contains a simple keyword used for login detection. After the login is successful, Aqua will only become aware of that success by detecting this keyword in output.

-  Configuration Part 2 (Data Dictionaries):

Next you want to take a look at the dictionaries in 'processReq' function/method. Notice there's two dictionary type objects declared. One is named 'login_data' and the other is 'header_data'; quite self explainatory. 

First open up Google Chrome and use the 'Inspect Element' feature, navigate to the network tab and gather the necessary information by attempting a login.  

Conversion tool:

When you collect the header or login data it will be in this format (example:)

Access-Control-Allow-Origin:http://www.newgrounds.com
CF-RAY:23fc40b4b24221c8-EWR
Connection:keep-alive
Content-Encoding:gzip
Content-Type:text/html

Take that data and copy it to clipboard and paste it into 'header.txt' then run the conversion script,

An output file will be generated with:

			'Content-Type': 'text/html',
			'Content-Encoding': 'gzip',
			'Connection': 'keep-alive',
			'CF-RAY': '23fc40b4b24221c8-EWR',
			'Access-Control-Allow-Origin': 'http': '//www.newgrounds.com',

This is that same data converted into Python dictionary data type format. You can now insert that data into the source code of 'Frame.py'. Do this for both the 'login' and 'headers' dictionary and place the appropriate information.

RUN:

Select 'Main.py' and type 'run' then press enter,

You will be prompted with login. Enter your username and password and if correctly configured you will be logged in.

-  Data extraction:

In 'Frame.py' you will notice the code responsible for the prompt. There's an infinite while loop with an if construct subsequently branched. Configure the commands here. Use the 'find_between' function to gather data between specific tags as demonstrated in the code.

elif cmd == 'who':
	print '\n' + find_between( processReq.page.content,"Online: (<strong>","</strong>)" ) + '\n'

The command is 'who' and the output to console will be the data between "Online: (<strong>" and "</strong>)" within page.content set in the processReq function. Displayed will be how many users are active in the forum.
