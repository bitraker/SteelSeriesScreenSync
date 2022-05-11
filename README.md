# SteelSeries Screen Sync

An unofficial application that sync screen colors with SteelSeries devices.

## Disclaimer

Written in Python3.x on a Windows machine. The application is in a very early alpha release. I have only had access to my own SteelSeries devices, consisting of a Rival 650 Mouse, QtK Large Mouse Pad and a K750 per-key illuminated keyboard. The code works in my setup on those devices. If you experience problems with your device, please open an issue, so the code can be updated.

## How it works

The application divides the lower half of the screen into a matrix of 6x22 boxes, adding up to a total of 132 boxes (this is the number the SteelSeries per-key bitmap API expects). The color of a center pixel in each of the boxes is sampled. 
The sampled colors are then applied some logic, so the screen colors can be faded, brightness can be adjusted and a low light setting can be enabled. 
The GUI is very simple and should be self explanatory.

## How to use it

There are two ways:
1. Download and review the code, install the required modules `requirements.txt` and run it.
2. Download the executable compiled from above code and run it.