import re

def hp( st ):
	if type( st ) == list:
		for y in range( len( st ) ):
			st[y] = hp( st[y] )
		return st
	else:
		return re.sub( "<(.*?)>", "", st )

def rec( st, x ):
	if type( st ) == list:
		for y in range( len( st ) ):
			st[y] = rec( st[y], x )
		return st
	else:
		return re.findall( re.compile( x ), st )
			

def extract( st, *xp ):
	for x in xp:
		st = rec( st, x )
	return st

