#Pr0nit

Simple script to set your wallpaper periodically using images from 
reddit. 

Usage:

    $ python pr0nit.py &


##XFCE4

If you're an XFCE4 user, make sure to use the option:
  
    --platform xfce4 

Feh seems to break XFCE4 after it has been run a few times. So, there is
XFCE4 appropriate code now to handle this case.

##Web Interface

pr0nit contains a fully featured web interface including a server
all within one python file. It doesn't even require you to install
any libraries. To start it, use:

    $ python pr0nit.py --use-web-interface

The web interface only listents locally, so it's secure. It will let you
choose from any wallpapers you've ever cached before, and will refresh
the default or specified subreddit's wallpapers on start. All other options,
such as --monitors are still applicable when invoking pr0nit with the web
interface option.

###Screenshot
  
  ![Web Interface](http://i.imgur.com/a5LZYH9.png)


##Contributing

Pull requests are very welcome. 

Wishlist:

  * New platforms: support for other DEs/WMs or operating systems.
      * windows
      * kde
      * gnome3
      * unity

