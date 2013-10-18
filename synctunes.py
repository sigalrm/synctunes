#!/usr/bin/env python

import os
import os.path
import plistlib
import sys
import codecs
import urlparse
import urllib
import string
import shutil

theITunesDirectory = os.path.expanduser('/cygdrive/c/Users/Eamon Walsh/Music/iTunes/')
theLibraryFile = os.path.join(theITunesDirectory, 'iTunes Music Library.xml')
theLibraryPath = os.path.join(theITunesDirectory, 'iTunes Media/Music/')
thePhonePath = os.path.expanduser('/cygdrive/f/Music/')

theLibraryTracksFile = 'library.out'
thePhoneTracksFile = 'phone.out'
theAddingTracksFile = 'adding.out'
theRemovingTracksFile = 'removing.out'

dryRun = False if '-f' in sys.argv else True

########################################################################

def unquote(source):
	try:
		return urllib.unquote(str(source))
	except:
		return urllib.unquote(source)

########################################################################

def copyFile(thePath):
        theSourcePath = os.path.join(theLibraryPath, thePath)
	theDestinationPath = os.path.join(thePhonePath, thePath)
	theDestinationDirectory = os.path.split(theDestinationPath)[0]

	if not os.path.exists(theDestinationDirectory):
		os.makedirs(theDestinationDirectory)
	if not os.path.exists(theDestinationPath):
		shutil.copyfile(theSourcePath, theDestinationPath)

########################################################################

try:
	from Foundation import (NSDictionary)
	d = NSDictionary.dictionaryWithContentsOfFile_(theLibraryFile)
except:
	d = plistlib.readPlist(theLibraryFile)
theTracks = d['Tracks']

########################################################################

libraryPaths = []
phonePaths = []
addingPaths = []
removingPaths = []
validKinds = ['Matched AAC audio file', 'Purchased AAC audio file', 'AAC audio file', 'MPEG audio file']
count = 0

for theKey in theTracks:
	theTrack = theTracks[theKey]

	theLocation = theTrack['Location']
	theURL = urlparse.urlparse(theLocation)

	if theURL.scheme != 'file':
		print 'Skipping non-file URL', theLocation
		continue

	if not('Rating' in theTrack and int(theTrack['Rating']) > 0):
#		print 'Skipping (no rating)', theLocation
		continue

	if not(theTrack['Kind'] in validKinds):
		print 'Skipping (wrong kind)', theLocation
		continue

	if int(theTrack['Total Time']) > 25 * 60 * 1000:
		print 'Warning (too long)', theLocation
#		continue

	thePath = unquote(theURL.path)
	thePath = string.replace(thePath, '/C:/', '/cygdrive/c/', 1)
	if os.path.exists(thePath) == False:
		print 'Bad path', str(theURL.path)
		sys.exit(1)

        thePath = string.replace(thePath, theLibraryPath, '', 1)
	libraryPaths.append(unicode(thePath, 'utf-8'))
	count = count + 1

libraryPaths = set(libraryPaths)

f = codecs.open(theLibraryTracksFile, 'w', 'utf-8')
for thePath in libraryPaths:
	f.write(thePath + '\r\n')

print 'Found %d tracks in library' % len(libraryPaths)

########################################################################

for root, dirs, files in os.walk(thePhonePath):
	for name in files:
		file = os.path.join(root, name)
		file = unicode(file, 'utf-8')
		if name[0] == '.':
			print 'Skipping', file
			continue

		file = string.replace(file, thePhonePath, '', 1)
                phonePaths.append(file)

f = codecs.open(thePhoneTracksFile, 'w', 'utf-8')
for thePath in phonePaths:
	f.write(thePath + '\r\n')

print 'Found %d tracks on phone' % len(phonePaths)

########################################################################

for thePath in phonePaths:
        if thePath.lower() not in libraryLowerPaths:
                removingPaths.append(thePath)

f = codecs.open(theRemovingTracksFile, 'w', 'utf-8')
for thePath in removingPaths:
	f.write(thePath + '\r\n')
        if dryRun:
                print 'Would remove', thePath, 'from phone'
        else:
                os.remove(os.path.join(thePhonePath, thePath))

########################################################################

libraryLowerPaths = set([thePath.lower() for thePath in libraryPaths])
phoneLowerPaths = set([thePath.lower() for thePath in phonePaths])

for thePath in libraryPaths:
        if thePath.lower() not in phoneLowerPaths:
                addingPaths.append(thePath)

f = codecs.open(theAddingTracksFile, 'w', 'utf-8')
for thePath in addingPaths:
	f.write(thePath + '\r\n')
        if dryRun:
                print 'Would add', thePath, 'to phone'
        else:
                copyFile(thePath)
