#!/usr/bin/env python

import os
import os.path
import plistlib
import sys
import codecs
import urlparse
import urllib
import string

########################################################################

### This tool reads the iTunes Music Library and produces a list of tracks that are in the iTunes Music directory but NOT in iTunes.

#### Note this script STILL has problems with Unicode file & track names

########################################################################

#### On Windows set the value of theITunesDirectory to "C:\Documents and Settings\<Your username>\My Documents\My Music\iTunes"

theITunesDirectory = os.path.expanduser('/cygdrive/c/Users/Eamon/Music/iTunes/')
theLibraryFile = os.path.join(theITunesDirectory, 'iTunes Music Library.xml')
theMusicPath = os.path.join(theITunesDirectory, 'iTunes Media/Music/')
theOutputTracksFile = os.path.expanduser('/home/ewalsh/tracks.txt')
theExtraTracksFile = os.path.expanduser('/home/ewalsh/extra_tracks.txt')
theOutputFolderPath = os.path.expanduser('/home/ewalsh/Moved Tracks')

########################################################################

def unquote(source):
	try:
		return urllib.unquote(str(source))
	except:
		return urllib.unquote(source)

########################################################################

try:
	from Foundation import (NSDictionary)
	d = NSDictionary.dictionaryWithContentsOfFile_(theLibraryFile)
except:
	d = plistlib.readPlist(theLibraryFile)
theTracks = d['Tracks']

########################################################################

thePaths = []
theMissingFilePaths = []

for theKey in theTracks:
	theTrack = theTracks[theKey]
	theLocation = theTrack['Location']
	theURL = urlparse.urlparse(theLocation)
	if theURL.scheme != 'file':
		print 'Skipping non-file URL', theLocation
		continue
	thePath = unquote(theURL.path)
	thePath = string.replace(thePath, '/C:/', '/cygdrive/c/', 1);
	if os.path.exists(thePath) == False:
		print str(theURL.path)
		sys.exit(1)
		theMissingFilePaths.append(thePath)

	thePaths.append(unicode(thePath, 'utf-8'))

thePaths = set(thePaths)
theLowerPaths = set([thePath.lower() for thePath in thePaths])

f = codecs.open(theOutputTracksFile, 'w', 'utf-8')
for thePath in thePaths:
	f.write(thePath + '\r\n')

print 'Found %d missing tracks' % len(theMissingFilePaths)
for thePath in theMissingFilePaths:
	print thePath

print 'Found %d tracks' % len(thePaths)

########################################################################

print '#' * 80

theExtraPaths = []
for root, dirs, files in os.walk(theMusicPath):
	for name in files:
		file = os.path.join(root, name)
		file = unicode(file, 'utf-8')
		ext = os.path.splitext(name)[1]
		if ext in ('.m4r', '.m4v'):
			print 'Skipping', file
			continue
		if name[0] == '.':
			print 'Skipping', file
			continue
		if string.count(file, 'iTunes LP.itlp'):
#			print 'Skipping LP', file
			continue
		if file.lower() not in theLowerPaths:
			theExtraPaths.append(file)

print 'Found %d unaccounted for files' % len(theExtraPaths)

########################################################################

f = codecs.open(theExtraTracksFile, 'w', 'utf-8')
for thePath in theExtraPaths:
	f.write(thePath + u'\r\n')

########################################################################

for thePath in theExtraPaths:
	print thePath
#	theDestinationPath = os.path.join(theOutputFolderPath, thePath[len(theMusicPath):])
#	theDestinationDirectory = os.path.split(theDestinationPath)[0]
#	if not os.path.exists(theDestinationDirectory):
#		os.makedirs(theDestinationDirectory)
#	os.remove(thePath)
