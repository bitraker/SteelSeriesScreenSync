# SteelSeries Screen Sync

An unofficial application that sync screen colors with SteelSeries devices.

## Disclaimer

Written in Python3.x on a Windows machine. The application is in a very early alpha release. I have only had access to my own SteelSeries devices, consisting of a Rival 650 Mouse, QtK Large Mouse Pad and a K750 per-key illuminated keyboard. The code works in my setup on those devices. If you experience problems with your device, please open an issue, so the code can be updated.

## How it works

The application divides the lower half of the screen into a matrix of 6x22 boxes, adding up to a total of 132 boxes (this is the number the SteelSeries per-key bitmap API expects). The color of a center pixel in each of the boxes is sampled.
The sampled colors are then applied some logic, so the screen colors can be faded, brightness can be adjusted and a low light setting can be enabled.
The GUI is very simple and should be self explanatory.

## How to use it

There are two ways to get it up and running:
1. Download and review the code, install the required modules `requirements.txt` and run it.
2. Download the zip file containing the executable, unpack it and run the exe file `ss-screensync.exe`. It's compiled from above code using cx-freeze.

When the program runs, you should see this interface:

![GUI Example](gui.png)

At this point the program should have changed your Keyboard colors (provided you own a per-key SteelSeries keyboard). If not, something is wrong.
Check the `application.log`, which is generated in the same folder as the `ss-screensync.exe` executable (or main.py file). The log is regenerated every time the program is opened.

When you close the program, you settings are automatically saved to the file `settings.json`. Those settings will be automatically loaded on startup.

The `config.json` file contains the path to the `coreProps.json` file. If your file is not in the standard location. You should edit this file to point to the correct location of the file.

## Options

### **Low Light**

With Low Light enabled, each key color will be upscaled if lower than the threshold determined by the Low Light setting.

### **Fade Effect**

With Fade Effect enabled, colors will gradually transition as determined by the Speed setting. By default, key colors are matched instantaneously.
### **Enhanced Rendering**

With Enhanced Rendering enabled, each key color is sampled as the average color of the sample area in which it resides. By default, colors are sampled from the center pixel of each region.

### **Keyboard Dimensions**

The predetermined 6x22 grid is applied as a color for each key, starting from the bottom left. Specify the number of rows and columns for your keyboard configuration in order to scale the sampled colors to fit.

### **Sampling Area**

Select the area of the screen that should be used when sampling colors. After clicking *Select Sampling Area*, a second window will appear. By default, the entire screen will be used for sampling, and this screen will appear green. The green area is the sampling area. To change the area, left click the top left of the region to sample and drag to the bottom right corner. To move the sampling area, right click and drag. To resize the sampling area to match the approximate dimensions of your keyboard configuration (to lessen the effect of distortion) middle click or use *Keyboard Resize* in the options window. Return to the options window and *Accept Sampling Area* to apply changes.

## Known issues
1. Compiled code is relatively large. Perhaps the size of it can be reduced.
2. Sometimes the app triggers the SteelSeries built-in DDoS protection. Unfortunately SteelSeries does not document, what makes it trigger other than "too many events". You can find it in the application.log if it happens.

## Release notes
### v0.2
- Added functionality to minimize application to system tray. This setting will be remembered, so the app automatically starts in tray, if setting is enabled.
- Improved stability
- Improved logging

### v0.3
- Fixed an unhandled error, where if, code was unable to sample an image from screen (ie) when switching game resolution. It would crash and stop changing colors.

### v0.4
- Bugfixes and stability improvements.

### v0.5
- Credit to (Carson Wilber)[https://github.com/carsonwilber] for adding several new features to the application.
- Added customizable screen sampling area.
- Added enhanced rendering that samples an average color rather than a single pixel.
- Improved low light feature to upscale colors rather than defaulting to a base color.
- The compiled files is now pretty large and can most likely be improved. Went from 50mb to almost 400mb. This is due to the modules used. There is probably a way to reduce the size. If anyone figure out a way to reduce the compiled footprint. Please share.
