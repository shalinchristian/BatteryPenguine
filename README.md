BatteryPanda - A System Resource Monitor Overlay
BatteryPanda is a lightweight, customizable desktop widget that provides a real-time overlay for monitoring your system's key metrics, including battery status, network speed, and CPU usage. It's designed to be unobtrusive, always on top, and easily collapsible.

<!-- Replace with an actual screenshot URL -->

The project includes two main versions:

BatteryPanda.py: The main, feature-rich version with a graphical CPU usage line, tooltips, and theme support.

BatteryPenguine.py: A simpler, more basic version focusing only on battery and network speed.

Features of BatteryPanda.py
Real-time Monitoring:

Battery: Displays current percentage and charging status. The color changes for low battery and charging states.

Network Speed: Shows the dominant network traffic (either upload or download) in real-time.

CPU Usage: A live graph visualizes CPU load over the last 50 samples.

Customizable UI:

Collapsible: A toggle button allows you to minimize the widget to a compact bar.

Themes: Switch between dark and light modes with a right-click.

Tooltips: Hover over the battery or network display for more detailed statistics.

Always-on-Top: The widget stays on top of all other windows for constant visibility.

Lightweight: Minimal resource consumption.

Requirements
You'll need Python installed, along with a few libraries.

Python 3.x

psutil

tkinter (usually included with Python)

You can install the necessary package using pip:

pip install psutil

How to Use
Download the Files: Get BatteryPanda.py and (optionally) BatteryPenguine.py.

Run the Script: Execute the script from your terminal.

python BatteryPanda.py

Interact with the Widget:

The widget will appear in the top-right corner of your screen.

Click the side toggle button to collapse or expand the view.

Right-click on the widget to open a context menu to switch themes or exit the application.

Hover your mouse over the text to see detailed tooltips.

Drag and drop the widget to move it (Note: This functionality is not yet implemented).

File Descriptions
BatteryPanda.py
This is the recommended script to use. It's a more polished and feature-complete version of the monitor. It includes a Config class for easy customization of colors, refresh rates, and window dimensions.

BatteryPenguine.py
A simpler and earlier version of the application. It lacks the CPU graph, theme options, and tooltips but provides the core functionality of monitoring battery and network speed. It uses the pygetwindow library, which is not required for BatteryPanda.py.

Feel free to modify the code, especially the Config class in BatteryPanda.py, to personalize the widget's appearance and behavior to your liking.