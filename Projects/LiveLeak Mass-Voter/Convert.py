
# Authenticate Query Unification Application
# Wayne Kenney - 2015                                   
#  _____                 ___     ___ 
# |  _  |___ _ _ ___ ___|_  |   |   |
# |     | . | | | .'|___|_| |_ _| | |
# |__|__|_  |___|__,|   |_____|_|___|
#         |_|                        
# By Pythogen

# Convert.py:

print '\nPyHeader_2_Dict\n\n-By Pythogen\n'

print 'Generating dictionary...\n'

f = open('header.txt','r')
fw = open('output.txt','w')
data = f.read().split('\n')


counts = len(data) + 1
for i in range(1,counts):
	b = data[len(data)-i]
	b = b.replace(':', "': '")
	fw.writelines("			'" + b + "',\n")
	print "'" + b + "',"

print '\nComplete.\n'

x = raw_input("OK")