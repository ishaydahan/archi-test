import json, sys

def checkInput(testFile):
	try:
		return json.load(open(testFile+".json"))
	except:
		print "Wrong input file name!"
		exit(1)

if len(sys.argv)!= 2:
	print "Please enter: python2 <filename.py> <input-filename>"
	exit (1)

#args and globals
testFile = sys.argv[1]
data = checkInput(testFile)
data = data["tests"]

for j in range(len(data)):
	print "Test case", j+1, "\r\n"
	print "testing:", data[j]["note"], "\r\n"
	print "input:", data[j]["input"].encode('ascii','ignore').encode('string_escape'), "\r\n"
	print "expectedOutput:", data[j]["expectedOutput"].encode('ascii','ignore').encode('string_escape'), "\r\n"
	print "points:", data[j]["points"], "\r\n"
	print "\r\n"