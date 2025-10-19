import psutil
import time

def get_battery_info():
    """Get battery info"""
    battery = psutil.sensors_battery()
    if battery:
        return (battery.percent, battery.power_plugged)
    return ("N/A", False)

def get_network_speed(last_net_io, last_time, speed_text):
    """Calculate current network speeds"""
    current_net_io = psutil.net_io_counters()
    current_time = time.time()
    time_elapsed = current_time - last_time

    if time_elapsed < 0.1:
        return speed_text, last_net_io, last_time

    upload = (current_net_io.bytes_sent - last_net_io.bytes_sent) * 8 / 1024 / time_elapsed
    download = (current_net_io.bytes_recv - last_net_io.bytes_recv) * 8 / 1024 / time_elapsed

    def format_speed(speed):
        return f"{speed/1000:.1f}M" if speed >= 1000 else f"{speed:.1f}K"

    result = f"{format_speed(upload)}▲" if upload > download else f"{format_speed(download)}▼"

    return result, current_net_io, current_time