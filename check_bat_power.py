#!/usr/bin/env python3
"""
Fish Stocking Data Scraper Run Script
"""
import os
import sys
from datetime import datetime
import yaml
from stocking_data_scraper import StockingDataScraper
from emailer import Emailer
import psutil

def getBatteryStatus():
    battery = psutil.sensors_battery()
    if battery is None:
        return "No battery found"

    percentage = battery.percent
    is_charging = battery.power_plugged
    time_remaining = battery.secsleft

    status = "Charging" if is_charging else "Discharging"
    time_display = "Calculating..." if time_remaining == psutil.POWER_TIME_UNKNOWN else f"{time_remaining // 3600}h {time_remaining % 3600 // 60}m"

    return {
        "percentage": percentage,
        "status": status,
        "time_remaining": time_display
    }

if __name__ == "__main__":
    battery_info = getBatteryStatus()

    now = datetime.now()
    date_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    bat_info = getBatteryStatus()

    # Load Config
    path = os.path.dirname(os.path.abspath(__file__))
    config_file = path + "/config.yaml"
    if os.path.isfile(path + "/config.yaml.local"):
        config_file = path + "/config.yaml.local"
    with open(config_file, "r", encoding="utf-8") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logwriter.write(f"Failed to load config: {exc}\n")
            sys.exit()

    emailer = Emailer(config["sendEmail"], config["sendEmailPassword"])
    if (bat_info['percentage'] < 75 or bat_info['status'] == "Discharging"):    
        body = f"Battery Low: {bat_info['percentage']:.1f}%. {bat_info['status']}"
        # Send new stocking events
        emailer.sendEmail(
            subject="Scraper Power Issue Detected",
            body=body,
            recipients=config["recipients"],
        )
    else:
        print("Battery Good")

