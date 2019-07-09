
#Webcam Screenshot

import cv2

def webcam_Capture():
	cap = cv2.VideoCapture(0)

	ret, frame = cap.read()
	rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)

	cv2.imshow('frame', rgb)
	out = cv2.imwrite('capture.jpg', frame)

	cap.release()
	cv2.destroyAllWindows()

try:
	webcam_Capture()
except:
	print "Webcam not found"