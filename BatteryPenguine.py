import psutil
import tkinter as tk
import pygetwindow as gw
import random
import time

stars = []
star_count = 10
canvas_width = 100
canvas_height = 30
last_net_io = psutil.net_io_counters()
last_time = time.time()
speed_text = "0▲|0▼"

# Cached values to reduce unnecessary calculations
_cached_battery = None
_battery_cache_time = 0
_cached_windows = []
_windows_cache_time = 0

def get_battery_info():
    global _cached_battery, _battery_cache_time
    
    current_time = time.time()
    # Cache battery info for 2 seconds to reduce psutil calls
    if current_time - _battery_cache_time > 2:
        battery = psutil.sensors_battery()
        if battery:
            _cached_battery = (battery.percent, battery.power_plugged)
        else:
            _cached_battery = ("N/A", False)
        _battery_cache_time = current_time
    
    return _cached_battery

def get_network_speed():
    global last_net_io, last_time
    
    current_net_io = psutil.net_io_counters()
    current_time = time.time()
    
    time_elapsed = current_time - last_time
    
    # Only calculate if enough time has passed
    if time_elapsed < 0.1:
        return speed_text
    
    # Calculate speeds in Kbps (1 byte = 8 bits, so we multiply by 8)
    upload_speed_kbps = (current_net_io.bytes_sent - last_net_io.bytes_sent) * 8 / 1024 / time_elapsed
    download_speed_kbps = (current_net_io.bytes_recv - last_net_io.bytes_recv) * 8 / 1024 / time_elapsed
    
    # Convert to Mbps if speed is > 1000 Kbps
    def format_speed(speed):
        if speed >= 1000:
            return f"{speed/1000:.1f}M"
        return f"{speed:.1f}K"
    
    # Only show the more significant speed
    if upload_speed_kbps > download_speed_kbps:
        result = f"{format_speed(upload_speed_kbps)}▲"
    else:
        result = f"{format_speed(download_speed_kbps)}▼"
    
    # Update for next call
    last_net_io = current_net_io
    last_time = current_time
    
    return result

def create_star():
    """Add a new star (white dot) at random height, starting from the left."""
    y = random.randint(5, canvas_height - 5)
    return {"x": 0, "y": y}

def update_stars():
    global stars, speed_text

    _, charging = get_battery_info()
    
    # Only clear and redraw if charging status or network changed
    new_speed = get_network_speed()
    if new_speed != speed_text or charging:
        canvas.delete("star")
        canvas.delete("speed")
        speed_text = new_speed
        
        speed_x = canvas_width - 5
        
        # Draw network speed indicator (small font)
        canvas.create_text(
            speed_x, canvas_height//2,
            text=speed_text,
            fill="white",
            font=("Segoe UI", 7),
            anchor="e",
            tag="speed"
        )

        if charging:
            # Move existing stars to the right
            for star in stars:
                star["x"] += 2
                canvas.create_oval(
                    star["x"], star["y"], star["x"] + 2, star["y"] + 2,
                    fill="white", outline="", tag="star"
                )

            # Remove stars that go off screen (use list comprehension more efficiently)
            stars[:] = [s for s in stars if s["x"] < canvas_width]

            # Randomly add new stars
            if len(stars) < star_count and random.random() < 0.3:
                stars.append(create_star())

    canvas.after(1000, update_stars)  # Reduced frequency from 500ms to 1000ms

def update_label():
    percentage, charging = get_battery_info()

    if percentage == "N/A":
        if label.cget("text") != "N/A":  # Only update if changed
            label.config(text="N/A", fg="gray")
    else:
        new_text = f"{percentage}%"
        if label.cget("text") != new_text:  # Only update if changed
            label.config(text=new_text)
            label.place(x=10, rely=0.5, anchor="w")

        # Determine color based on status
        if charging:
            new_color = "white"
        elif percentage <= 20:
            new_color = "red"
        elif percentage == 100:
            new_color = "lime"
        else:
            new_color = "white"
        
        if label.cget("fg") != new_color:  # Only update if color changed
            label.config(fg=new_color)

    root.after(2000, update_label)  # Reduced frequency from 1000ms to 2000ms

def check_fullscreen():
    global _cached_windows, _windows_cache_time
    
    current_time = time.time()
    # Cache window list for 1 second to reduce expensive window enumeration
    if current_time - _windows_cache_time > 1:
        try:
            _cached_windows = gw.getWindowsWithTitle('')
        except:
            _cached_windows = []  # Handle potential errors
        _windows_cache_time = current_time
    
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    fullscreen_active = False
    try:
        fullscreen_active = any(
            hasattr(window, 'isMaximized') and window.isMaximized and 
            window.width >= screen_width and window.height >= screen_height
            for window in _cached_windows
        )
    except:
        pass  # Handle potential attribute errors

    if fullscreen_active:
        if root.state() != "withdrawn":
            root.withdraw()
    else:
        if root.state() == "withdrawn":
            root.deiconify()
            root.attributes("-topmost", True)

    root.after(500, check_fullscreen)  # Keep this responsive for fullscreen detection

def prevent_minimize():
    if root.state() == "iconic":
        root.after(1, root.deiconify)
        root.attributes("-topmost", True)
    root.after(100, prevent_minimize)  # Reduced frequency from 1ms to 100ms

def keep_on_top():
    root.lift()
    root.attributes("-topmost", True)
    root.after(2000, keep_on_top)  # Reduced frequency from 500ms to 2000ms

def close_app():
    root.quit()
    root.destroy()

# --- Tkinter Setup ---
root = tk.Tk()
root.title("Battery+Network")
root.geometry(f"{canvas_width}x{canvas_height}")
root.configure(bg='black')
root.wm_attributes('-alpha', 0.5)
root.overrideredirect(True)
root.attributes("-topmost", True)

# Position window
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"+{screen_width - 350}+0")

# Canvas with label on top
canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="black", highlightthickness=0)
canvas.pack(fill="both", expand=True)

label = tk.Label(canvas, text="", font=("Segoe UI", 12, "bold"), fg="white", bg="black")
label.place(x=10, rely=0.5, anchor="w")

# Right-click menu
menu = tk.Menu(root, tearoff=0)
menu.add_command(label="Close", command=close_app)
label.bind("<Button-3>", lambda event: menu.post(event.x_root, event.y_root))

root.protocol("WM_DELETE_WINDOW", lambda: root.deiconify())

# --- Start Everything ---
update_label()
update_stars()
check_fullscreen()
prevent_minimize()
keep_on_top()
root.mainloop()
