#!/usr/bin/python3

import os
import sys
import time as t
import platform as pf
try:
	from requests import Session
except ImportError:
	os.system( "pip install requests" )
import getpass as gt
from tools import *
import re

platf = pf.system()
welcome_in = """\n\
Welcome to PUP SIS Terminal/CMD version, """
welcome_out = """\n\
What would you like to do?
	1	-	View all your grades
	2	-	View your current schedule
	3	-	Find a subject offering
	0	-	Logout
Choice: """

s = Session()

def cont():
	input( "Press enter to continue ..." )
	clear()

def sl():
	t.sleep( 3 )

def clear():
	if platf == "Linux":
		return os.system( "clear" )
	else:
		return os.system( "cls" )

def goodbye():
	input( "\nThank you. Have a good day. Oh almost forgot, press enter to exit ..." )
	sys.exit()

def server_env():
	try:
		res = s.get( "http://sisstudents.pup.edu.ph" )
	except TimeoutError:
		print( "failed. Reconnecting ...")
		sl()
		return init()
	except ConnectionError:
		print( "failed. Check your internet connection ..." )
		sl()
		return goodbye()
	except:
		print( "failed. No internet connection ..." )
		sl()
		return goodbye()
	burl = "/".join( re.findall( r'href = " (.*?) "', res.content.decode( "utf-8" ) )[0].split( "/" )[:3] )
	return burl

def login( burl ):
	print( """\n\
Login to PUP SIS Server: """ + burl )
	stud_num = input( """\
	Student Number:	""" )
	print( """\
	Birthdate:""" )
	stud_bdm = input( """\
		Month[ 01-12 ]:		""" )
	stud_bdd = input( """\
		Day[ 1-28/30/31 ]:	""" )
	stud_bdy = input( """\
		Year[ 19* - 20* ]:	""" )
	stud_pw = gt.getpass( """\
	Password:	""" )

	login_data = {
		"txtUser": stud_num,
		"cboMonth": stud_bdm,
		"cboDay": stud_bdd,
		"cboYear": stud_bdy,
		"txtPwd": stud_pw
	}
	return login_data

def init():
	clear()
	print( "Connecting to PUP SIS server ...", end="", flush=True )
	burl = server_env()
	print( "OK")
	url = burl + "/aimss/process/validate.php?userType=1"
	login_data = login( burl )
	print( "Logging you in ...", end="", flush=True )
	try:
		res = s.post( url, login_data )
		res = s.get( burl + "/aimss/students/grades.php?mainID=106&menuDesc=Grades" )
		restext = res.content.decode( "utf-8" )
		name = re.search( r'Welcome, <b>(.*?)</b>', re.sub( "\n", " ", res.content.decode( "utf-8" ) ) ).group(1)
		if name == ' ()':
			print( "failed. Try again." )
			sl()
			return init()
		else:
			print( "OK" )
			sl()
			return home( burl, name )
	except TimeoutError:
		print( "server failed. Reconnecting to server ...")
		sl()
		return init()
	
def search( url, code ):
	count = 0
	cc = 0
	try:
		courses = re.sub( "\n", " ", s.get( url ).content.decode( "utf-8" ) )
		courses = hp( re.findall( r'<option groupid=\'[0-9].*?\' value=\'(.*?)\'>', courses ) )
		l = len( courses )
		ret = []
		print( "Searching in", l, "courses ..." )
		for x in courses:
			out = ""
			tmp = ""
			cur = re.sub( "\n", " ", s.post( url, { "cboCourse": x } ).content.decode( "utf-8" ) )
			ccur = re.search( r'<option groupid=\'[0-9].*?\' value=\'.*?\' selected>.*?- (.*?)</option>', cur ).group(1)
			cur = hp( extract( cur,
				'<table width=\'100%\' class=\'dbtable\'>(.*?)</table>',
				'<tr bgcolor=\'white\'>(.*?)</tr>',
				'<td class=\'regu\'.*?>(.*?)</td>'
			) )
			for x in cur:
				for y in x:
					try:
						if y[0] == code:
							count += 1
							tmp += y[0]
							tmp += ( 16 - len( tmp ) ) * " "
							tmp += y[1]
							tmp += ( 64 - len( tmp ) ) * " "
							tmp += y[2]
							tmp += ( 80 - len( tmp ) ) * " "
							tmp += y[3]
							tmp += ( 88 - len( tmp ) ) * " "
							tmp += y[4]
							tmp += ( 96 - len( tmp ) ) * " "
							tmp += y[5]
							tmp += ( 104 - len( tmp ) ) * " "
							tmp += y[6]
							tmp += ( 120 - len( tmp ) ) * " "
							tmp += y[7] + "\n"
							out += tmp
							tmp = ""
							ret.append( y )
					except ValueError:
						continue
			if len( out ) != 0:
				print( "\rCourse Name: " + ccur )	
				print( "Subject Code\tDescription\t\t\t\t\tSection Code\tLec\tLab\tUnits\tRoom No.\tSchedule" )
				print( out )
			cc += 1
			print( "\rCourses searched: " + str( cc ), end="/" + str( l ) + " ...", flush=True )
	except KeyboardInterrupt:
		print( "\nNumber of results:", count, "\n" )
		cont()
		return ret
	print( "\nNumber of results:", count, "\n" )
	cont()
	return ret
		 

def home( burl, name ):
	clear()
	url = burl + "/aimss/students/"
	section_url = url + "sections.php?mainID=102&menuDesc=Section%20Offering"
	sched_url = url + "schedule.php?mainID=105&menuDesc=Schedule"
	grades_url = url + "grades.php?mainID=106&menuDesc=Grades"

	grades = s.get( grades_url ).content.decode( "utf-8" )
	grades = hp( extract( re.sub( "\n", " ", grades ),
		'<table width=\'100%\' bgcolor=\'lightblue\' class=\'regu\'>(.*?)</table>',
		'<tr bgcolor=\'white\'>(.*?)</tr>',
		'<td>(.*?)</td>'
	) )
	sched = s.get( sched_url ).content.decode( "utf-8" )
	sched = hp( extract( re.sub( "\n", " ", sched ),
		'<table width=\'100%\' class=\'dbtable\'>(.*?)</table>',
		'<tr bgcolor=\'white\'>(.*?)/tr>',
		'<td class=\'regu\'.*?>(.*?)<'
	) ) 

	ch = input( welcome_in + name + welcome_out )
	if ch.isnumeric():
		ch = int( ch )
	while( ch != 0 ):
		if ch == 1:
			for x in grades:	
				print( "\n\n# Subject Code\tDescription\t\t\t\t\t\t\t\tFaculty Name\t\t\tUnits\tSect Code\tF. Grade\tGrade Status" )
				for y in x:
					out = y[0] + " " + y[1]
					out += ( 16 - len( out ) ) * " "
					out += y[2]
					out += ( 88 - len( out ) ) * " "
					out += y[3]
					out += ( 120 - len( out ) ) * " "
					out += y[4]
					out += ( 128 - len( out ) ) * " "
					out += y[5]
					out += ( 144 - len( out ) ) * " "
					out += y[6]
					out += ( 160 - len( out ) ) * " "
					out += y[7]
					print( out )
				print( "\n" )
			cont()
		elif ch == 2:
			for x in sched:
				print( "\n\n# Subject Code\tDescription\t\t\t\t\t\t\t\tLec\tLab\tUnits\tSchedule" )
				for y in x:
					out = y[0] + " " + y[1]
					out += ( 16 - len( out ) ) * " "
					out += y[2]
					out += ( 88 - len( out ) ) * " "
					out += y[3]
					out += ( 96 - len( out ) ) * " "
					out += y[4]
					out += ( 104 - len( out ) ) * " "
					out += y[5]
					out += ( 112 - len( out ) ) * " "
					out += y[6]
					print( out )
				print( "\n" )
			cont()
		elif ch == 3:
			code = input( "Enter subject code: " )
			if code.isupper() == False:
				code = code.upper()
			if re.match( r'[A-Z]+-[0-9]+', code ) != None or re.match( r'[A-Z]+ [0-9]+', code ) != None:
				print( "Searching now for results, please wait ...\n" )
				results = search( section_url, code )
			else:
				print( "Invalid subject code, try again" )
		else:
			print( "Choose only between 1-3 and 0" )
		ch = input( welcome_in + name + welcome_out )
		if ch.isnumeric():
			ch = int( ch )
	goodbye()

try:
	init()
except KeyboardInterrupt:
	goodbye()
