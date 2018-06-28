# Facial-recognition
Facial recognition with a Raspberry Pi and camera using OpenCV. Implementation in Python.

*******************************************
* SECURITY CAMERA WITH FACIAL RECOGNITION 
*******************************************

 (yyyy/mm/dd)
→ 2017/10/14

• First boot of the Raspberry Pi 3

• Changed password (sudo raspi-config)

• Connect to local WiFi

• Update software (sudo apt-get update)

• Install software (sudo apt-get upgrade)


→ 2017/10/15

• Making the camera work (https://projects.raspberrypi.org/en/projects/getting-started-with-picamera)

• Attempt to install openCV on Raspberry Pi 3 (jessie)

	♦ Guide: https://raspberrypi.stackexchange.com/questions/69169/how-to-install-opencv-on-raspberry-pi-3-in-raspbian-jessie
	
	sudo apt-get install build-essential git cmake pkg-config
	sudo apt-get install libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev
	sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
	sudo apt-get install libxvidcore-dev libx264-dev
	sudo apt-get install libgtk2.0-dev
	sudo apt-get install libatlas-base-dev gfortran
	
	git clone https://github.com/Itseez/opencv.git
	
	♦ If this gives errors use SSH to clone the repository from github.
	♦ Install PuTTY on Windows to use SSH (https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html)
	♦ Connect to the local IP address of the raspberry pi (in my case this only worked when the pi was connected to the same LAN via ethernet)
	♦ Find pi's IP-address: hostname -I
	♦ Connect with pi's username and password
	♦ Try again:
	
	git clone https://github.com/Itseez/opencv.git
	
	♦ Continue
	
	cd opencv
	git checkout 3.3.0
	cd ~
	git clone https://github.com/Itseez/opencv_contrib.git
	cd opencv_contrib
	git checkout 3.1.0
	cd ~
	
	♦ Setup OpenCV for Python 3
	sudo apt-get install python3-dev				(not necessary if you already have it)
	wget https://bootstrap.pypa.io/get-pip.py
	sudo python3 get-pip.py
	pip install numpy
	cd ~/opencv
	mkdir build
	cd build
	cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D INSTALL_C_EXAMPLES=OFF \
    -D INSTALL_PYTHON_EXAMPLES=ON \
    -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules \
    -D BUILD_EXAMPLES=ON ..
	make -j4
	sudo make install
	sudo ldconfig
	

→ 2017/10/22
 ------------
| VNC VIEWER |
 ------------
 (https://www.raspberrypi.org/documentation/remote-access/vnc/)
 
 Very short version
	• Make sure VNC Viewer is installed on the controlling device and VNC Server is installed on the raspberry pi
	• Check if VNC is enabled on raspberry pi (Menu > Preferences > Raspberry Pi Configuration > Interfaces)
	• Create a VNC account (needed for cloud connect)
	• LAN: connect directly via local IP
	• Cloud connect: right click the vnc symbol at the system tray, select licensing and add the raspberry pi as 1/5 free cloud connections
	

 ----------------------------
| Connect to WPA2 Enterprise |
 ----------------------------
 (https://www.bunver.com/connecting-raspberry-pi-to-wpa2-enterprise-wireless-network/)

 --------------
| WPA settings |
 --------------
 sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
 
 
