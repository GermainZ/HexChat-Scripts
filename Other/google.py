# -*- coding: utf-8 -*-
 
# Google.py Copyright (c) 2010 by Jochen Blacha <jochen.blacha@gmail.com>
# Requirements: X-Chat or HexChat for Linux
#               Python 2.6 or 2.7
#               python-simplejson
#
# This script is published under the terms of the GNU GPL v2.0 license.
# See http://www.gnu.org/licenses/gpl-2.0.html
#
# Google AJAX API Documentation
# http://code.google.com/apis/ajaxlanguage/documentation/#Examples
#
# The Google wordmark is a registered trademark of Google Inc.
 
__module_name__ = 'Google'
__module_version__ = '1.0.12'
__module_description__ = 'Google Web Search for XChat and HexChat'
 
import simplejson
import urllib
import urllib2
import time
import xchat
from threading import Thread

color = {'white': "\00300", 'black': "\00301", 'blue': "\00302", 'green': "\00303", 'lred': "\00304", 'brown': "\00305", 'purple': "\00306", 'orange':"\00307", 'yellow': "\00308", 'lgreen': "\00309", 'cyan': "\00310", 'lcyan': "\00311", 'lblue': "\00312", 'pink': "\00313", 'grey': "\00314", 'lgrey': "\00315", 'bold': "\002", 'nobold': "\002", 'nocolor': "\017"}
users = {}

class channels:
    allowed = [ "#gingerdx", "#xda-devs", "#atest" ]

def google( word, word_eol, userdata ):
    channel = xchat.get_info( 'channel' )
    if channel.lower() in channels.allowed and word[1].startswith( '#google' ):
        if len( word[1] ) == 7:
            xchat.command( 'msg ' + channel + ' ' + color["purple"] + 'Usage  : #google <your search query>' + color["nocolor"] )
            xchat.command( 'msg ' + channel + ' ' + color["purple"] + 'Example:' + color["nocolor"] + ' #google Rocket Science' )
            return xchat.EAT_NONE 
        if len( word[1] ) > 7:
            mySearch = ''
            argument = [ s.strip() for s in word[1].split( ' ' ) if s.strip() ]
            mySearch = ' '.join( argument[1:] )
        if len( mySearch ) < 2 or mySearch == '':
                xchat.command( 'msg ' + channel + ' ' + color["lred"] + 'Your search must at least consist out of a word with two or more letters.' + color["nocolor"] )
                return xchat.EAT_NONE
        gthread = Thread ( target=google_query, args=( mySearch, channel) )
        gthread.start()
        return xchat.EAT_NONE

def google_query(mySearch, channel):
    try:
        baseurl  = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&rsz=large&'
        query    = urllib.urlencode( { 'q': mySearch.rstrip(' ') } )
        fullurl  = baseurl + query.encode( 'utf8' )
        response = urllib2.urlopen( fullurl )
        json     = simplejson.loads( response.read() )
        if json ['responseStatus'] == 200 and len( json ['responseData'] ['results'] ) > 1:
            results = json [ 'responseData' ] [ 'results' ]
            xchat.command( 'msg ' + channel + ' ' + color["purple"] + '=== Searching for ' + mySearch)
            for item in results[0:3]:
                title = item[ 'title' ].encode( 'utf8' ).replace ( '<b>', '' ).replace ( '</b>', '' ).replace ( '&lt;', '<' ).replace ( '&gt;', '>' ).replace ( '&amp;', '&' ).replace ( '&quot;', '"' ).replace ( '&#39;', '\'' )
                url   = item[ 'url' ].encode( 'utf8' ).replace ( '%3B', ';' ).replace ( '%3F', '?' ).replace ( '%2F', '/' ).replace ( '%3A', ':' ).replace ( '%23', '#' ).replace ( '%26', '&' ).replace ( '%3D', '=' ).replace ( '%2B', '+' ).replace ( '%24', '$' ).replace ( '%2C', ',' ).replace ( '%20', ' ' ).replace ( '%25', '%' ).replace ( '%3C', '<' ).replace ( '%3E', '>' ).replace ( '%7E', '~' ).replace ( '%7B', '{' ).replace ( '%7D', '}' ).replace ( '%7C', '|' ).replace ( '%5C', '\\' ).replace ( '%5E', '^' ).replace ( '%5B', '[' ).replace ( '%5D', ']' ).replace ( '%60', '`' ).replace ( '%40', '@' )
                xchat.command( 'msg ' + channel + ' ' + title + color["blue"] + ' ' + url + color["nocolor"] )
            xchat.command( 'msg ' + channel + ' ' + color["purple"] + '=== Powered by ' + color["blue"] + 'G' + color["lred"] + 'o' + color["yellow"] + 'o' + color["blue"] + 'g' + color["lcyan"] + 'l' + color["lred"] + 'e' + color["purple"] + ' Web Search' + color["nocolor"] )
        else:
            xchat.command( 'msg ' + channel + ' ' + color["purple"] + 'Your search returned no results.' + color["nocolor"] ) 
    except Exception, args:
        xchat.command ( 'msg ' + channel + ' ' + str( Exception ) + ' ' + str( args ) )
        return xchat.EAT_NONE
    except HTTPError, e:
        xchat.command ( 'msg ' + channel + ' HTTP Error: ' + str( e.code ) )
        return xchat.EAT_NONE
    except URLError, e:
        xchat.command ( 'msg ' + channel + ' URL Error: ' + str( e.reason ) )
        return xchat.EAT_NONE
    return xchat.EAT_NONE

xchat.hook_print( 'Channel Msg Hilight', google )
xchat.hook_print( 'Channel Message', google )
xchat.hook_print( 'Your Message', google )

print "\00304", __module_name__, "successfully loaded.\003"
