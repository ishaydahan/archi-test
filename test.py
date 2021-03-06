from subprocess32 import PIPE, STDOUT, check_output, Popen
from decimal import Decimal
import zipfile,fnmatch,os,shutil
import xlwt
import json
import sys

def checkInput(testFile):
	try:
		return json.load(open(testFile+".json"))
	except:
		print "Wrong input file name!"
		exit(1)

def checkSrc(data, srcPath):
	try:
		if not checkFiles(data["srcFiles"], os.listdir(srcPath)):
			print "Please put required src files in 'src' folder!"
			exit(1)
	except:
		print "Wrong src folder name!"
		exit(1)		

def extractZips(path):
	global student
	for root, dirs, files in os.walk(path):
		for filename in files:
			if student in filename and not filename.endswith(('.zip')):
				writeToFile(filename[0:5], 0, "ERROR! you did not followed the orders! not a zip.\n", "=> not zip error")
	for root, dirs, files in os.walk(path):			
		for filename in fnmatch.filter(files, '*.zip'):
			zipfile.ZipFile(os.path.join(root, filename)).extractall(os.path.join(root, os.path.splitext(filename)[0]))
	return path

def checkZip(rootPath):
	try:
		if "." in rootPath: 
			zipfile.ZipFile(rootPath).extractall("zips")
			return extractZips("zips")
		else:
			return extractZips(rootPath)	
	except:
		if "." in rootPath:
			print "Wrong zip file name!"
			exit(1)
		else:
			print "Wrong zip folder name!"
			exit(1)

#check dir contains dir
def checkDir(location):
	for filename in os.listdir(location): 
		if os.path.isdir(location +'/'+ filename):
			return True
	return False	

#check files exists in location
def checkFiles(data, location):
	for filename in data:
		if filename not in location:
			return False
	for filename in location:
		if filename not in data:
			return False		
	return True

#edit grader notes
def writeNotes(testnum, myinput, expectedOutput, output):
	global notes
	notes = notes + "fail test "
	notes = notes + testnum
	notes = notes + "\nfor input:\n"
	notes = notes + myinput.encode('ascii','ignore').encode('string_escape')
	notes = notes + "\nexpected:\n"
	notes = notes + expectedOutput.encode('ascii','ignore').encode('string_escape')
	notes = notes + "\ngot:\n"
	notes = notes + output.encode('ascii','ignore').encode('string_escape')
	notes = notes + "\n\n"

#write grade to file
def writeToFile (groupNum, grade, graderNotes, debugMsg):
	global i, notes, sumGrades, lastGroupNum, frontalCheck
	if lastGroupNum==groupNum:
		notes = ""
		return
	graderNotes = graderNotes + "YOUR GRADE IS: " + str(grade)
	if frontalCheck:
		print "Group num:",groupNum, "\n\n", str(graderNotes)
	else:	
		worksheet.write(i, 0, int(groupNum))
		worksheet.write(i, 1, int(grade))
		worksheet.write(i, 2, str(graderNotes))
		print "Group num:",groupNum, "Grade:",grade, debugMsg
	i+=1
	notes = ""
	sumGrades += grade
	lastGroupNum = groupNum

#run test case
def case(myinput, expectedOutput, testnum, executable, points):
	try: #try execute
		p = Popen(['./'+executable], stdout=PIPE, stdin=PIPE, stderr=STDOUT, universal_newlines=True)
		stdout = p.communicate(input=myinput, timeout=10)[0]
	except: #execute failed
		writeNotes(testnum, myinput, expectedOutput, "TIMEOUT")
		p.kill()
		return 0
	try: #try get stdout
		out = stdout.decode()
	except: #stdout fail
		writeNotes(testnum, myinput, expectedOutput, "UnicodeDecodeError")
		return 0
	if stdout.decode() != expectedOutput: #wrong stdout
		writeNotes(testnum, myinput, expectedOutput, out)
		return 0
	else: #All Clear
		return points

#main test func
def test (groupNum, data):
	global notes, sumGrades
	try: #try compile
		check_output(["make"])
	except: #compile failed
		writeToFile(groupNum, 0, "ERROR! your files didnt compiled.\n", "=> compilation error")
		return
	grade = 0
	for j in range(len(data)):
		grade += case (data[j]["input"], data[j]["expectedOutput"], str(j+1), data[j]["executable"], data[j]["points"]);
	writeToFile(groupNum,grade,notes,"")

def getGroupNum(string):
	num = string.rindex('A')
	if num > 20:
		num = string[0:20].rindex('A')
	return string[num-5:num]
#-------------------------------------------------------------------------------------------------------------------------
student = ""
frontalCheck = False

if len(sys.argv)== 6:
	frontalCheck = True;
	student = sys.argv[5]
elif len(sys.argv)!= 5:
	print "Please enter: python2 <filename.py> <input-filename> <src-folder> <zip-file/zips-folder> <output-filename>"
	exit (1)
else:
	pass

#args and globals
testFile = sys.argv[1]
srcPath =  sys.argv[2]+"/"
rootPath = sys.argv[3]
outputFile = sys.argv[4]
notes = "" #global grader notes
sumGrades = 0 #var for calc AVG
lastGroupNum = -1
i=1 #student counter

#prepere Excel
workbook = xlwt.Workbook()
worksheet = workbook.add_sheet('grades')
worksheet.write(0, 0, 'submittal_group_id')
worksheet.write(0, 1, 'grade')
worksheet.write(0, 2, 'grade_note')

path = checkZip(rootPath)
data = checkInput(testFile)
checkSrc(data, srcPath)
testCases = open(testFile+".txt","wb")
Popen(["python2", "cases.py", testFile], stdout=testCases)
#main loop
print "-------------------------CALCULATING-------------------------"
for root, dirs, files in os.walk(path):
	cwd = os.getcwd() #save folder location
	if checkDir(os.path.join(root)): #not student folder
		pass
	elif not checkFiles(data["neededFiles"], os.listdir(os.path.join(root))) and student in os.path.join(root): #bad structure of student folder
		writeToFile(getGroupNum(os.path.join(root)), 0, "ERROR! you did not followed the orders! bad file names / not all needed files in zip / too much files in zip.\n", "=> folder structure error")
		shutil.rmtree(os.path.join(root))
	elif student in os.path.join(root):
		for filename in os.listdir(srcPath): #copy src files to student's folder
			shutil.copy( srcPath + filename, os.path.join(root))
		os.chdir(os.path.join(root)) #change folder to student folder
		test(getGroupNum(os.path.join(root)), data["tests"]) #execute
		os.chdir(cwd) #return to previous folder
		shutil.rmtree(os.path.join(root))

if "." in rootPath:
	shutil.rmtree(path)

workbook.save(outputFile+'.xls')
print "-------------------------FINISHED-------------------------"
print "TOTAL:", (i-1)
print "AVG:", "{0:0.5f}".format(sumGrades/float((i-1)))