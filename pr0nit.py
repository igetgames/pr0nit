#!/usr/bin/env python
"""
Sets the wallpaper on Linux via reddit. Requires 'feh' or you to edit the
WALLPAPER_CMD variable to suit your configuration.

Suggested subreddits: /r/earthporn, /r/usaporn, /r/cityporn. Works on any
subreddit with links directly to jpg files.

Author: Tom Dignan <tom@tomdignan.com>
"""

import uuid
import os
import json
import urllib2
import time 

WALLPAPER_CACHE_DIR = "%s/.wallpaper" % os.getenv("HOME")
DEFAULT_SUBREDDIT = "r/earthporn" # try also, r/usaporn
WALLPAPER_CMD = "feh --bg-scale"
FRAME_SPEED = 60


class RedditWallpaperSetter(object):

    def __init__(self, subreddit, cache_dir, wallpaper_cmd, frame_speed):
        """ 
        Called every time the program is started. Ensures that the directory
        structure is intact. 
        """
        self.subreddit = subreddit
        self.cache_dir = cache_dir
        self.wallpaper_cmd = wallpaper_cmd
        self.frame_speed = frame_speed

        if not os.path.isdir(cache_dir):
            os.mkdir(cache_dir) 


    def run(self):
        """
        Runs here until terminated. Sets wallpapers at time intervals.
        """
        try:
            wallpaper_urls = self._get_wallpaper_urls()
        except urllib2.HTTPError, e:
            print "Retrying in 10 seconds: %r" % e
            time.sleep(10)
            self.run()
            return

        for url in wallpaper_urls:
            path = self._download_wallpaper(url)            
            os.system("%s %s" % (self.wallpaper_cmd, path))
            time.sleep(self.frame_speed)


    def _get_wallpaper_urls(self):
        """
        Downloads the current URLs from the first page of results for
        the target subreddit.
        """
        url = "http://www.reddit.com/%s/.json" % self.subreddit
        f = urllib2.urlopen(url)
        data = json.loads(f.read())['data']

        wallpaper_urls = []
        for child in data['children']:
            url = child['data']['url']

            # If it doesn't end in jpg, it probably goes to another HTML page.
            # Easiest to just exclude them.
            if url.lower().endswith(".jpg"):
                wallpaper_urls.append(url)

        return wallpaper_urls


    def _download_wallpaper(self, url):
        """ 
        Saves the wallpaper at the target `url` in `cache_dir`
        """ 
        file_in = urllib2.urlopen(url)
        path = self.cache_dir + os.path.sep + str(uuid.uuid4()) + ".jpg"
        file_out = open(path, "w")
        file_out.write(file_in.read())
        file_out.close()
        file_in.close()

        return path


if __name__ == "__main__":
    wallpaper_setter = RedditWallpaperSetter(DEFAULT_SUBREDDIT, WALLPAPER_CACHE_DIR,
                                            WALLPAPER_CMD, FRAME_SPEED)
    wallpaper_setter.run()
