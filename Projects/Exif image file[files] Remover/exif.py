from PIL import Image
import glob
import os, os.path

tpcheck = 0
y = 'a'

def main():
	global z
	global y
	p = "L"
	z = glob.glob("C:/testdir/*.png")

	print "Directory selected is (A to continue or B to change directory)"
	u = raw_input("")
	if u == "B":
		y = raw_input ("Enter Directory: ")
		tpcheck = 1
		process2()
	elif u == "A":
		process1()
		pass
	else:
		print "invalid command"
		main()

def process1():
	global p
	global z
	global y
	for i in glob.glob(str(y)):
		image = Image.open(str(i))
		# next 3 lines strip exif
		data = list(image.getdata())
		image_without_exif = Image.new(image.mode, image.size)
		image_without_exif.putdata(data)

		image_without_exif.save((str(i)))
		print "Image exif removed from file " + str(i)

def process2():
	global p
	global z
	global y
	for i in z:
		image = Image.open(str(i))
		# next 3 lines strip exif
		data = list(image.getdata())
		image_without_exif = Image.new(image.mode, image.size)
		image_without_exif.putdata(data)

		image_without_exif.save((str(i)))
		print "Image exif removed from file " + str(i)


def Process():
	global tpcheck
	global image
	global data
	global image_without_exif

	if tpcheck == 0:

		for i in z:
			image = Image.open(str(i))
			# next 3 lines strip exif
			data = list(image.getdata())
			image_without_exif = Image.new(image.mode, image.size)
			image_without_exif.putdata(data)

			image_without_exif.save((str(i)))
			print "Image exif removed from file " + str(i)

	elif tpcheck == 1:
			for i in z:
				image = Image.open(str(y))
		# next 3 lines strip exif
				data = list(image.getdata())
				image_without_exif = Image.new(image.mode, image.size)
				image_without_exif.putdata(data)

				image_without_exif.save((str(i)))
				print "Image exif removed from file " + str(i)


main()
Process()