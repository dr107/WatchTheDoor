# WatchTheDoor
A video peephole/face detector for Raspberry Pi written in Python/Flask

# Installation

Since this is just a hobby project for me, I haven't exactly packaged this up in such a way that it's easy to install. It involves compiling and installing a large open-source project from source, installing a bunch of other dependencies, and possibly managing multiple python environments. If you're familiar with everyday Linux/Unix command line use, this should all be pretty straightforward. If not, this might be a little tricky, since there might be potential pitfalls I didn't mention that an experienced Unix user would naturally avoid. The good news is, you'll probably learn a lot from the experience :). If you want to suggest any improvements to this guide, feel free to file an issue. 

## Install OpenCV
Install the **python 3**  bindings for OpenCV by following [these instructions](http://www.pyimagesearch.com/2016/04/18/install-guide-raspberry-pi-3-raspbian-jessie-opencv-3/). Note that if you don't want to use a virtualenv, `sudo apt-get install python3-pip`, and just use the `pip3` command wherever the author uses `pip`, and you won't have to mess with virtualenvs. I'm not a terribly experienced python programmer, and don't have many environments to manage, so I found this much more confortable. The following is a 'bare bones' summary of those instructions for the lazy.

### Make sure your pi is set up properly

1. `ssh` into your Pi. There's plenty of guides on how to do this, it's a waste of space to repeat here.
2. First, you want to make sure your pi is up to date, and has enough space. If you have an 8GB or less SD card, or have less than a few GB of space left on yours, you'll want to see the above instructions for advice on freeing up space. To update, do `sudo apt-get update && sudo apt-get upgrade`. If you had to update any core raspberry pi stuff, you should probably reboot.
3. Install dependencies. `sudo apt-get install build-essential cmake pkg-config libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libffi-dev libxvidcore-dev libx264-dev libgtk2.0-dev libatlas-base-dev gfortran python2.7-dev python3-dev python3-pip wget`
4. When I compile stuff from source, I like to keep the source and binary files in a '.stuff directory' off of my home directory. Wherever you like to put your compiled files, just change your directories appropriately. `cd && mkdir .stuff && cd .stuff`

### Get the code and prepare to build.

1. Download and unzip the openCV source code. I put the links to the 3.1.0 versions here, but feel free to use a different one
2. `wget -O opencv.zip https://github.com/Itseez/opencv/archive/3.1.0.zip && unzip opencv.zip`
3. `wget -O opencv_contrib.zip https://github.com/Itseez/opencv_contrib/archive/3.1.0.zip && unzip opencv_contrib.zip`
4. At this point, you shouldn't need the zip files anymore, feel free to `rm` them.
5. Remember, we're using python 3 here, so your `pip` commands should all be `pip3`. If you want to use `virtualenv`s, that's fine, but if you know how to do that you probably don't need me to explain anything ;).
6. You're going to want `numpy` installed when you compile. `sudo pip3 install numpy`.
7. `cd opencv-3.1.0/`
8. `mkdir build && cd build`
9. Finally, invoke `cmake`. Remember to use the correct path (did you use .stuff like I did?). 
```
cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D INSTALL_PYTHON_EXAMPLES=ON \
    -D OPENCV_EXTRA_MODULES_PATH=~/.stuff/opencv_contrib-3.1.0/modules \
    -D BUILD_EXAMPLES=ON ..
```
**The next step is to compile openCV. This step takes over an hour, so it's worth it to make sure you did everything right up to this point, or you'll wind up having to start over. Look at the instructions linked above (ctrl-F examine the output of CMake) and make sure your Python 3 environment is set up properly**
    
### Build and install openCV.

1. If you've convinced yourself this is going to work, the fastest way to compile this thing is to make use of all four cores. However, it still takes over an hour. (optional) if you want to log out of your pi while this is running, you can use [GNU Screen](https://www.gnu.org/software/screen/). First, install with `sudo apt-get install screen`. You can then make a new screen session with `screen -S compile` (or whatever name you want). You can then run your command, and disconnect by pressing `ctrl-a` then `ctrl-d`, log out of your pi completely if you want, and your command will still be running. To get back to your screen session, do `screen -x compile`. Use `screen -ls` if you forget the name you gave the session.
2. To finally compile do `make -j4`, then get ready to wait 60-90 minutes. I'd walk away if I were you, a watched pot never boils ;)
3. Once that's complete, do `sudo make install && sudo ldconfig` to complete the installation. These shouldn't take more than a few minutes.
4. Now openCV should be installed in python 3. Go to the python3 REPL by doing `python3`, then, from the REPL, do `import cv2`, then `cv2.__version__`. If all went well, it should return `'3.1.0'` (or whatever version you used).
5. If that worked, congrats! You're 90% of the way to installing this code! If not, I'd recommend following the instructions linked above. The author is a much more experienced python developer than yours truly, and I may have forgotten something. If that's the case, please file an issue through GitHub, and I'll update this doc.

## Install the Rest of the Dependencies
### Install Uv4L, the Streaming server we use to access the camera. 
1. `curl http://www.linux-projects.org/listing/uv4l_repo/lrkey.asc | sudo apt-key add -`
2. Add the following line to your /etc/apt/sources.list `deb http://www.linux-projects.org/listing/uv4l_repo/raspbian/ wheezy main`
3. `sudo apt-get update`
4. `sudo apt-get install uv4l uv4l-raspicam uv4l-raspicam-extras uv4l-webrtc`
5. Once that's done, go to your Pi's ip address on port 8080 to make sure it worked. Should be something like http://10.10.10.xxx:8080. 
6. Configure it according to the [documentation](http://www.linux-projects.org/uv4l/) if necessary. I, for example, had to flip the Y axis of the image to get it to appear right-side-up.

### Install the Python dependencies.
  * `sudo pip3 install flask flask_injector yagmail apscheduler`

## Finishing up
### Clone this repo
Choose whatever install location you wish.

`cd <your_chosen_location>`

`git clone https://github.com/dr107/WatchTheDoor.git`

### Setting up config files
In order to finish setting up the server, you need to provide it with some information. In the `WatchTheDoor/config_secret` directory, you'll find files `creds.json.example` and `to.json.example`. `cd` into that directory.

1. Do `cp creds.json.example creds.json && cp to.json.example to.json`
2. `creds.json` specifies the GMail account credentials of the account you want to be **sending** the emails notifying you when someone's at the door. Put the account username and password here. If you're not familiar with the JSON format, the example should make things pretty clear. 
3. `to.json` specifies a list of recipients to be notified when someone's at the door. Feel free to use the same account that's sending the emails, and specify as many as you want in this JSON list.

## You're done!
You should be ready to go. `cd` into the `WatchTheDoor` directory and do `chmod +x run.py`, then you should be able to do `./run.py`, and your server will be running! Go to your pi's IP address on port 5000 in your browser (e.g. http://10.10.10.xxx:5000) and click around! Put your face in front of the camera and see if you get an email.

## Optional extras
If you've taken the time to go this far, you'll probably want to take a few more steps to make this thing a little bit more user-friendly. 

### Supervisor (auto-start the server on boot)
Nobody likes to have to go into the Pi and restart the server in a screen session every time we reboot the Pi. Wouldn't it be nice to have the server auto-start when the Pi boots? [Supervisor](http://supervisord.org/index.html) makes this stupendously easy.

1. `sudo apt-get install supervisor && sudo service supervisor restart`
2.  Have a look at the file (in this repo) `extras/WatchTheDoor.conf`. Specifically, have a look at the line that starts with `command`. If you cloned this repo into the home directory of the `pi` user that comes with Raspbian, it should look something like that, but **make sure that if you run that command, the server starts properly**. Have a look at the [supervisor docs](http://supervisord.org/configuration.html) if you want to edit this further. The logs are currently limited to 50MB worth, which should be more than enough for debugging.
3. `cd` into the root directory of this repo and do `sudo cp extras/WatchTheDoor.conf /etc/supervisor/conf.d/`.
4. Do `sudo supervisorctl reread && sudo supervisorctl update` to let supervisor know you added the file
5. Do `sudo service supervisor restart`. 
6. You should be done. `sudo supervisorctl status` should show the `WatchTheDoor` job as `RUNNING`, and doing `tail -f /var/log/WatchTheDoor.log` should show the logs printing as usual. Try rebooting your pi and it should start right back up.
 
### Avahi-Daemon (Use a hostname instead of an IP)
TBD
