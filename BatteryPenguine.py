import psutil
import tkinter as tk
import pygetwindow as gw
import random
import time

stars = []
star_count = 10
canvas_width = 100  # Adjusted width
canvas_height = 30
last_net_io = psutil.net_io_counters()
last_time = time.time()
speed_text = "0▲|0▼"

def get_battery_info():
    battery = psutil.sensors_battery()
    if battery:
        return battery.percent, battery.power_plugged
    return "N/A", False

def get_network_speed():
    global last_net_io, last_time
    
    current_net_io = psutil.net_io_counters()
    current_time = time.time()
    
    time_elapsed = current_time - last_time
    
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
        return f"{format_speed(upload_speed_kbps)}▲"
    else:
        return f"{format_speed(download_speed_kbps)}▼"
    
    # Update for next call
    last_net_io = current_net_io
    last_time = current_time

def create_star():
    """Add a new star (white dot) at random height, starting from the left."""
    y = random.randint(5, canvas_height - 5)
    return {"x": 0, "y": y}

def update_stars():
    global stars, speed_text

    _, charging = get_battery_info()
    canvas.delete("star")
    canvas.delete("speed")

    # Always show network speed
    speed_text = get_network_speed()
    speed_x = canvas_width - 5  # Position on right side
    
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

        # Remove stars that go off screen
        stars = [s for s in stars if s["x"] < canvas_width]

        # Randomly add new stars
        if len(stars) < star_count:
            if random.random() < 0.3:
                stars.append(create_star())

    canvas.after(500, update_stars)  # Update twice per second for smoother network speed

def update_label():
    percentage, charging = get_battery_info()

    if percentage == "N/A":
        label.config(text="N/A", fg="gray")
    else:
        # Position battery percentage on the left
        label.config(text=f"{percentage}%")
        label.place(x=10, rely=0.5, anchor="w")  # Left-aligned at x=10

        if charging:
            label.config(fg="white")
        else:
            if percentage <= 20:
                label.config(fg="red")
            elif percentage == 100:
                label.config(fg="lime")
            else:
                label.config(fg="white")

    root.after(1000, update_label)

def check_fullscreen():
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    fullscreen_active = any(
        window.isMaximized and window.width >= screen_width and window.height >= screen_height
        for window in gw.getWindowsWithTitle('')
    )

    if fullscreen_active:
        if root.state() != "withdrawn":
            root.withdraw()
    else:
        if root.state() == "withdrawn":
            root.deiconify()
            root.attributes("-topmost", True)

    root.after(1, check_fullscreen)

def prevent_minimize():
    if root.state() == "iconic":
        root.after(1, root.deiconify)
        root.attributes("-topmost", True)
    root.after(1, prevent_minimize)

def keep_on_top():
    root.lift()
    root.attributes("-topmost", True)
    root.after(500, keep_on_top)

def close_app():
    root.quit()
    root.destroy()

# --- Tkinter Setup ---
root = tk.Tk()
root.title("Battery+Network")
root.geometry(f"{canvas_width}x{canvas_height}")
root.configure(bg='black')
root.wm_attributes('-alpha', 0.5)  # Use wm_attributes for better compatibility
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
label.place(x=10, rely=0.5, anchor="w")  # Initially position on left side

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