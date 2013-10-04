#!/usr/bin/env python
"""
Sets the wallpaper via reddit. Requires 'feh' on Linux, or you to edit the
WALLPAPER_CMD variable to suit your configuration.

Suggested subreddits: /r/earthporn, /r/usaporn, /r/cityporn. Works on any
subreddit with links directly to jpg files.

Author: Tom Dignan <tom@tomdignan.com>
Contributors: James Clarke 
"""

import argparse
import uuid
import os
import json
import urllib2
import time
import sys

if sys.platform == 'darwin':
    from Foundation import NSAppleScript
    from Cocoa import NSApplication


WALLPAPER_CACHE_DIR = "%s/.wallpaper" % os.getenv("HOME")
DEFAULT_SUBREDDIT = "r/earthporn" # try also, r/usaporn
DEFAULT_WALLPAPER_CMD = "feh --bg-scale"
DEFAULT_FRAME_SPEED = 60


class RedditWallpaperSetter(object):

    def __init__(self, subreddit, cache_dir, frame_speed, monitors=1,
                 **kwargs):
        """ 
        Called every time the program is started. Ensures that the directory
        structure is intact. 
        """
        self.subreddit = subreddit
        self.cache_dir = cache_dir
        self.frame_speed = frame_speed
        self.monitors = monitors

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
            self._set_wallpaper(path)
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


    def _set_wallpaper(self, path):
        raise Exception("Not implemented")


class RedditWallpaperSetterLinux(RedditWallpaperSetter):

    def _set_wallpaper(self, path):
        os.system("%s %s" % (DEFAULT_WALLPAPER_CMD, path))


class RedditWallpaperSetterXFCE4(RedditWallpaperSetter):
    
    def _set_wallpaper(self, path):
        for i in range(self.monitors):
            os.system("xfconf-query -c xfce4-desktop -p "  
               " /backdrop/screen0/monitor%d/image-path -s %s" % (i, path))
                

class RedditWallpaperSetterOSX(RedditWallpaperSetter):
    
    def _set_wallpaper(self, path):
        script = NSAppleScript.alloc().initWithSource_("""
            tell app "Finder" to set desktop picture to POSIX file "%s"
        """ % path)
        script.executeAndReturnError_(None)


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="""Set the wallpaper from
 reddit""")


    parser.add_argument("--monitors", metavar="<number>", type=int, nargs=1,
        default=1, help="Number of monitors in your setup (XFCE4 only)")

    parser.add_argument("--frame-speed", metavar="<seconds>", type=int,
        default=DEFAULT_FRAME_SPEED, nargs=1, 
        help="Number of seconds to elapse between switching wallpapers.")
        
    parser.add_argument("--platform", metavar="<string>", type=str, nargs=1,
        default=sys.platform, help="Target platform, defaults to %r." %
        sys.platform)

    args = parser.parse_args()
    
    get_arg = lambda x : x[0] if not x is None and not isinstance(x, int) else x
    monitors = get_arg(args.monitors)
    platform = get_arg(args.platform)
    frame_speed = get_arg(args.frame_speed)


    if platform == "darwin":
        # Set the activation policy to NSApplicationActivationPolicyAccessory
        # so we don't show the Python dock icon when using PyObjC.
        NSApplication.sharedApplication().setActivationPolicy_(2)
        wallpaper_setter = RedditWallpaperSetterOSX(DEFAULT_SUBREDDIT,
                                                    WALLPAPER_CACHE_DIR,
                                                    frame_speed,
                                                    monitors=monitors)
    elif platform == "xfce4":
        wallpaper_setter = RedditWallpaperSetterXFCE4(DEFAULT_SUBREDDIT,
                                                      WALLPAPER_CACHE_DIR,
                                                      frame_speed,
                                                      monitors=monitors)
    else:
        wallpaper_setter = RedditWallpaperSetterLinux(DEFAULT_SUBREDDIT,
                                                      WALLPAPER_CACHE_DIR,
                                                      frame_speed,
                                                      monitors=monitors)
    wallpaper_setter.run()
