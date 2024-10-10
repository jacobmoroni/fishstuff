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

if __name__ == "__main__":

    # Set up logging
    LOGFILE = "/log_info.txt"
    now = datetime.now()
    date_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    path = os.path.dirname(os.path.abspath(__file__))
    logwriter = open(path + LOGFILE, "a", encoding="utf-8")
    logwriter.write(f"\n-----running {date_time_str}-----\n")

    # Load Config
    config_file = path + "/config.yaml.local"
    if os.path.isfile(path + "/config.yaml.local"):
        config_file = path + "/config.yaml.local"
        logwriter.write("found local config file: loading from there")
    with open(config_file, "r", encoding="utf-8") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logwriter.write(f"Failed to load config: {exc}\n")
            sys.exit()

    sds = StockingDataScraper(
        config["spotsToCheck"], path + "/last_scraped_data.txt", logwriter
    )

    emailer = Emailer(config["sendEmail"], config["sendEmailPassword"])

    # Send new stocking events
    if len(sds.new_events) > 0:
        logwriter.write("Sending email\n")
        emailer.sendEmail(
            subject="New Fish Stocking Event Detected",
            body="\n\n".join(sds.new_events),
            recipients=config["recipients"],
        )
    else:
        logwriter.write("No new stocking information\n")

    # Send logs
    if sds.checkShouldSendLogs(path + LOGFILE, now, config["logSendFreqDays"]):
        with open(path + LOGFILE, "r", encoding="utf-8") as logs:
            body = logs.read()
            emailer.sendEmail(
                subject="Fish Stocking Log Report:",
                body=body,
                recipients=config["recipients"],
            )
            logs.close()
        logwriter.close()
        # Clear file
        with open(path + LOGFILE, "w", encoding="utf-8") as f:
            f.close()
    else:
        logwriter.close()
