# Quick-and-Simple
## **Dear fellow lazy people,**  
Let me lay out a scenario for you. Imagine that you had just started up your PC. You now want to watch a Youtube video or go on Google. To do that, you must   
1. Open your browser.
2. Click on the search bar (assuming you don't use Google Chrome or a favorites feature of any browser).
3. Type in "Youtube.com" or "Google.com".
4. Enter your query into the secondary search bar.
5. Press <kbd>Enter</kbd>.   

Now that might not seem like a lot of steps but if you are anything like me, it gets worse if you have to do it many times throughout the day. With this program, you can save your few precious seconds. Your dream of living a slothful life is one step closer to coming true. All you have to do is leave the program open, press two buttons on your keyboard, and you will already be at whichever search bar you want to be using (predictive search not included). All you gotta do is type your query and press <kbd>Enter</kbd>. 
  
## **Specifications**
This program is written in Python 3.7.7 using the win32 api designed for use in Windows only.  

Required Packages:  
* [pywin32](https://pypi.org/project/pywin32/) - Python extensions for Microsoft Windows. Provides access to much of the Win32 API.
* [pynput](https://pypi.org/project/pynput/) - A library for controlling and monitor input devices.
  
This program includes a requirements file for easy installation of the required packages using PyPI.  
It is recommended that you install a virtual environment before installing requirements.   
To do so, feel free to read up on [python virtual environments](https://docs.python.org/3/tutorial/venv.html). 
```
$pip install -r requirements.txt
```
  
## **Usage**  
```
$python main.py
```
To conduct a **Google** search, use hotkey <kbd>Alt</kbd> + <kbd>z</kbd>.  
To conduct a **Youtube** search, use hotkey <kbd>Alt</kbd> + <kbd>x</kbd>.  
These features are also available through the system tray icon.  
To quit the program, right click the system tray icon and select quit.  
  
## **Contributing**
All contributions or feedback are welcomed.