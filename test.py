from subprocess32 import PIPE, STDOUT, check_output, Popen
import zipfile,fnmatch,os,shutil
import xlsxwriter
import json

#edit grader notes
def writeNotes(testnum, expectedOutput, output):
	global notes
	notes = notes + "fail test "
	notes = notes + testnum
	notes = notes + "\nexpected:\n"
	notes = notes + repr(expectedOutput)
	notes = notes + "\ngot:\n"
	notes = notes + repr(output)
	notes = notes + "\n"

#write grade to file
def writeToFile (i, groupNum, grade, notes):
	worksheet.write(i, 0, groupNum)
	worksheet.write(i, 1, grade)
	worksheet.write(i, 2, notes)

#run test case
def case(myinput, expectedOutput, testnum, task, points):
	try: #try execute
		stdout = Popen(['./task'+task+'.bin', 'f'], stdout=PIPE, stdin=PIPE, stderr=STDOUT).communicate(input=myinput, timeout=10)[0]
	
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
		check_output(['bash','-c', "make"])

	except: #compile failed
		writeToFile(i, groupNum, 0, "error compiling. you did not followed the orders! bad file names / bad syntax / including makefile / not a zip. YOUR GRADE IS 0")
		return 0;

	grade = 0
	for j in range(len(data)):
		grade += case (data[j]["input"], data[j]["expectedOutput"], data[j]["testNum"], data[j]["task"], data[j]["points"]);

	#write to Excel
	writeToFile(i,groupNum,grade,notes)
	notes = ""
	sumGrades += grade
	return grade;

print "Please put student's Zips in 'zip' folder"
print "Please put src files in 'src' folder"
#get args
arg1 = raw_input("Please enter JSON test file name: ")
arg2 = raw_input("Please enter full uniqe file name that should be in student folder: ")

#prepere Excel
workbook = xlsxwriter.Workbook('grades.xlsx')
worksheet = workbook.add_worksheet()
worksheet.write('A1', 'Group ID')
worksheet.write('B1', 'Grade')
worksheet.write('C1', 'Grader Notes')

#extract zips in "zip" folder
rootPath = "zip"
srcPath = "src/"
pattern = '*.zip'
for root, dirs, files in os.walk(rootPath):
    for filename in fnmatch.filter(files, pattern):
        zipfile.ZipFile(os.path.join(root, filename)).extractall(os.path.join(root, os.path.splitext(filename)[0]))

#open tests file
with open(arg1+".json") as data_file:    
	data = json.load(data_file)["tests"]

#main loop
print "-------------------------CALCULATING-------------------------"
i=1
notes = "" #global grader notes
sumGrades = 0
pattern = arg2 #uniqe file name that should be in student folder
for root, dirs, files in os.walk(rootPath):
    for filename in fnmatch.filter(files, pattern):
    	groupNum = os.path.join(root)[4:9] #get groupNum
    	for filename in os.listdir(srcPath): #copy needed files to student's folder
			shutil.copy( srcPath + filename, os.path.join(root))
    	cwd = os.getcwd() #save folder location
    	os.chdir(os.path.join(root)) #change folder to student folder
    	print "Group num:",groupNum, "Grade:", test(groupNum, i, data) #execute
    	os.chdir(cwd) #return to previous folder
    	i=i+1	
workbook.close()
print "-------------------------EXCEL FILE READY-------------------------"
print "AVG:", sumGrades/(i-1)