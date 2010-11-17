#!/usr/bin/env python
"""
apod.py

written by Kyle Isom <coder@kyleisom.net>

fetched NASA APOD. Usage:
    apod.py [optional directory]

unless specified, the script downloads images to ~/Pictures/apod; the
storage directory may be specified on the command line.
"""

import argparse
import datetime
import os
import re
import sys
import urllib2

########################
# function definitions #
########################
def url_open(url_str):
    """
    Open the given URL with error handling.
    """

    try:
        url	= urllib2.urlopen(url_str)

    # something went wrong with the webserver
    except urllib2.HTTPError, e:
        err = sys.stderr.write
        err('APOD download failed with HTTP error ', e.code, '\n')
        sys.exit(2)

    else:
        page 	= url.read()

    return page

def set_background(image_path):
    platform = sys.platform

    print 'using platform: ' + platform

    if "darwin" == platform:
        try:
            from appscript import app, mactypes
            app('Finder').desktop_picture.set(mactypes.File(image_path))
        except ImportError:
            sys.stderr.write('could not import appscript. please ensure')
            sys.stderr.write('appscript is installed.\n')
            return False
        except:
            sys.stderr.write('error setting wallpaper!')
            return False
        else:
            return True
    else:
        sys.stderr.write(platform + ' is unsupported.\n')
        return False

############
# URL vars #
############
# base_url: the URL to the APOD page
# image_url: used to store the URL to the large version of the APOD
base_url    = 'http://antwrp.gsfc.nasa.gov/apod/'
image_url   = None

###########
# regexes #
###########
# apod_img: used to pull the large image from the APOD page
# base_img: grabs the base image name, i.e. from image/date/todays_apod.jpg
#           this will return $1 = todays_apod and $2 = jpg - note the 
#           separation of extension from basename.
apod_img    = 'href.+"(image/[\\w+\\./]+\\_big.[a-z]{3,4})"'
base_img    = '.+/(\\w+)\\.([a-z]{3,4})'

######################
# path and file vars #
######################
# store_dir: where file should be saved
# image_name: the name of the image; taken from the base_img regex in the
#             form $1 + '_date' + $2 where date is in the form yyyymmdd.
# temp_f: file descriptor for the temporary file the image is download as
#         the file is later moved to store_dir/image_name
store_dir = os.environ['HOME'] + '/Pictures/apod/'      # default save dir
image_name  = None                                      # image name
temp_f      = os.tmpfile()                              # temp file

######################
# miscellaneous vars #
######################
today       = '_' + str(datetime.date.today()).replace('-', '')


########################
# begin main code body #
########################

# check to see if both a directory to store files in was specified and
# that the script has write access to that directory.
if len(sys.argv) > 1:
    if os.access(sys.argv[1], os.W_OK):
        store_dir = sys.argv[1]
    else:
        sys.stderr.write('could not access ' + sys.argv[1])
        sys.stderr.write(' - falling back to ' + store_dir + '\n')

if not os.access(store_dir, os.F_OK):
    sys.stderr.write('no write permissions on ' + store_dir + '!\n')
    sys.exit(-1)

# fetch page
page    = url_open(base_url).split('\n')

# hunt down the APOD
for line in page:
    match 	    = re.search(apod_img, line, re.I)
    if match:
        image_url   = base_url + match.group(1)
        match2      = re.match(base_img, match.group(1), re.I)
        image_name  = match2.group(1) + today + '.' + match2.group(2)
        break

# is broeked?
if not image_url:
    sys.stderr.write('error retrieving APOD filename!\n')
    sys.exit(3)

print 'fetching ' + image_url
temp_f.write(url_open(image_url))
temp_f.seek(0)

store_file  = store_dir + image_name

# diagnostic information
print 'will store as ' + store_dir + image_name

if os.access(store_file, os.F_OK):
    print 'file already exists!'
    sys.exit(4)
    

# save the file
with open(store_file, 'wb+') as image_f:
    image_f.write(temp_f.read())

# wew survived the gauntlet!
print 'finished!'