#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import threading, Queue
import sys, os
from HTMLParser import HTMLParser

url_queue = Queue.Queue()
rlock = threading.RLock()

save_dir = '.'

opener = urllib2.build_opener()

class ImgDownloader(threading.Thread):
    def run(self):
        def get_filename(url):
            val = url.rsplit('/')
            return val[len(val)-1]

        while True:
            try:
                url = url_queue.get_nowait()
            except:
                break

            save_file = os.path.join(save_dir, get_filename(url))
            try:
                req = urllib2.Request(url)
                file = open(save_file, 'wb')
                file.write(opener.open(req).read())
                file.close()
            except:
                print('error: %s' % get_filename(url))

            with rlock: print(url)

class ImgParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)

    def handle_starttag(self, tagname, attribute):
        if tagname.lower() == "img":
            for i in attribute:
                if i[0].lower() == "src":
                    url_queue.put(i[1])
                    print i[1]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print 'Usage: python %s <urlname> [<save_dir>]' % sys.argv[0]
        quit()

    url = sys.argv[1]
    if len(sys.argv) == 3:
        save_dir = sys.argv[2]

    if os.path.exists(save_dir) == False:
        os.makedirs(save_dir)

    htmldata = urllib2.urlopen(url)

    parser = ImgParser()
    parser.feed(htmldata.read())

    parser.close()
    htmldata.close()

    MAX_THREAD = 2
    threads = []
    for n in range(MAX_THREAD):
        threads.append(ImgDownloader())

    for thd in threads:
        thd.start()

    for thd in threads:
        thd.join()
