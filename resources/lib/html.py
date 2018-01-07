# -*- coding: utf-8 -*-

# version 3.1.3 - Par CB
# version 3.0.0 - By CB
# version 2.0.2 - By SlySen
# version 0.2.6 - By CB

import re
import socket
import urllib2

def get_url_txt(the_url):
    """ function docstring """
    req = urllib2.Request(the_url)
    req.add_header(\
                   'User-Agent', \
                   'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:19.0) Gecko/20100101 Firefox/19.0'\
                   )
    req.add_header('Accept-Charset', 'utf-8')
    response = urllib2.urlopen(req)
    link = response.read()
    link = urllib2.quote(link)
    link = urllib2.unquote(link)
    response.close()
    return link


def is_network_available(url):
    """ function docstring """
    try:
        # see if we can resolve the host name -- tells us if there is a DNS listening
        host = socket.gethostbyname(url)
        # connect to the host -- tells us if the host is actually reachable
        srvcon = socket.create_connection((host, 80), 2)
        srvcon.close()
        return True
    except socket.error:
        return False



