from subprocess32 import PIPE, STDOUT, check_output, Popen
import zipfile,fnmatch,os,shutil
import xlwt
import json
import sys

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
def writeNotes(testnum, expectedOutput, output):
	global notes
	notes = notes + "fail test "
	notes = notes + testnum
	notes = notes + "\nexpected:\n"
	notes = notes + expectedOutput.encode('ascii','ignore').encode('string_escape')
	notes = notes + "\ngot:\n"
	notes = notes + output.encode('ascii','ignore').encode('string_escape')
	notes = notes + "\n"

#write grade to file
def writeToFile (i, groupNum, grade, notes):
	worksheet.write(i, 0, groupNum)
	worksheet.write(i, 1, grade)
	worksheet.write(i, 2, notes)

#run test case
def case(myinput, expectedOutput, testnum, executable, points):
	try: #try execute
		stdout = Popen(['./'+executable], stdout=PIPE, stdin=PIPE, stderr=STDOUT, universal_newlines=True).communicate(input=myinput, timeout=10)[0]
	
	except: #execute failed
		writeNotes(testnum, expectedOutput, "TIMEOUT")
		return 0

	try: #try get stdout
		out = stdout.decode()

	except: #stdout fail
		writeNotes(testnum, expectedOutput, "UnicodeDecodeError")
		return 0

	if stdout.decode() != expectedOutput: #wrong stdout
		writeNotes(testnum, expectedOutput, out)
		return 0

	else: #All Clear
		return points

#main test func
def test (groupNum, i, data):
	global notes, sumGrades

	try: #try compile
		check_output(["make"])

	except: #compile failed
		writeToFile(i, groupNum, 0, "error compiling. YOUR GRADE IS 0")
		return "0 => compilation error";

	grade = 0
	for j in range(len(data)):
		grade += case (data[j]["input"], data[j]["expectedOutput"], str(j+1), data[j]["executable"], data[j]["points"]);

	#write to Excel
	writeToFile(i,groupNum,grade,notes)
	notes = ""
	sumGrades += grade
	return grade;

#args
testFile = sys.argv[1]
outputFile = sys.argv[2]
rootPath = "zip"
srcPath = "src/"

#open tests file
with open(testFile+".json") as data_file:    
	data = json.load(data_file)

#check src files
if not checkFiles(data["srcFiles"], os.listdir(srcPath)):
	print "Please put required src files in 'src' folder!"
	exit(1)

#prepere Excel
workbook = xlwt.Workbook()
worksheet = workbook.add_sheet('grades')
worksheet.write(0, 0, 'submittal_group_id')
worksheet.write(0, 1, 'grade')
worksheet.write(0, 2, 'grade_note')

i=1 #student counter

#give 0 to non zip files
for root, dirs, files in os.walk(rootPath):
    for filename in files:
        if not filename.endswith(('.zip')):
			writeToFile(i, filename[0:5], 0, "ERROR! you did not followed the orders! not a zip! YOUR GRADE IS 0")
			print "Group num:",filename[0:5], "Grade: 0 => not zip"
			i+=1

#extract zips in "zip" folder
for root, dirs, files in os.walk(rootPath):			
	for filename in fnmatch.filter(files, '*.zip'):
		zipfile.ZipFile(os.path.join(root, filename)).extractall(os.path.join(root, os.path.splitext(filename)[0]))

#main loop
print "-------------------------CALCULATING-------------------------"
notes = "" #global grader notes
sumGrades = 0 #var for calc AVG
for root, dirs, files in os.walk(rootPath):
	cwd = os.getcwd() #save folder location
	groupNum = os.path.join(root)[4:9] #get groupNum
	if os.path.join(root)=="zip" or checkDir(os.path.join(root)): #not student folder
		pass
	elif not checkFiles(data["neededFiles"], os.listdir(os.path.join(root))): #bad structure of student folder
		writeToFile(i, groupNum, 0, "ERROR! you did not followed the orders! bad file names / not all needed files in zip / too much files in zip. YOUR GRADE IS 0")
		print "Group num:",groupNum, "Grade: 0 => bad files"
		i+=1
	else:
		for filename in os.listdir(srcPath): #copy src files to student's folder
			shutil.copy( srcPath + filename, os.path.join(root))
		os.chdir(os.path.join(root)) #change folder to student folder
		print "Group num:",groupNum, "Grade:", test(groupNum, i, data["tests"]) #execute
		os.chdir(cwd) #return to previous folder
		i+=1

#delete all created folders
for root, dirs, files in os.walk(rootPath):
	if not os.path.join(root)=="zip":
		shutil.rmtree(os.path.join(root))

workbook.save(outputFile+'.xls')
print "-------------------------EXCEL FILE READY-------------------------"
print "TOTAL:", (i-1)
print "AVG:", sumGrades/(i-1)