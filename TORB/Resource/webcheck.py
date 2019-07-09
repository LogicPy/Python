import requests

def RCIDDoSCheck():
	RCIStatus = 0
	RCIConfirm = 0
	urlDDoS = "http://127.0.0.1/ddos.py"

	try:
		requestChecker = requests.get(urlDDoS)
	except:
		RCIStatus = 1

	if RCIStatus == 0:
		RCIConfirm = 'Online'
		return RCIConfirm
	elif RCIStatus == 1:
		RCIConfirm = 'Offline'
		return RCIConfirm


print RCIDDoSCheck()