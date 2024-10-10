#!/usr/bin/env python3
"""
Fish Stocking Data Scraper
"""
from datetime import datetime
import requests


class StockingDataScraper:
    """
    Class that scrapes the latest stocking data to look for new stocking events
    """

    def __init__(self, spots_to_check, scraped_data_file, logwriter=None) -> None:
        now = datetime.now()
        self.date_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
        self.url = "https://dwrapps.utah.gov/fishstocking/Fish"
        self.scraped_data_file = scraped_data_file
        self.spots_to_check = spots_to_check
        self.scraped_data = []
        self.last_update = None
        self.logwriter = logwriter
        self.log(f"Downloading latest data ({self.date_time_str})")
        self.fish_data = self.downloadData(self.url)
        if len(self.fish_data) > 0:
            self.log("Parsing data...")
            self.parseFishData(self.spots_to_check, self.fish_data)
        else:
            self.log("Failed to download")
            return

        last_scraped_data = self.loadLastScrapedData(self.scraped_data_file)
        self.log("comparing data...")
        self.new_events = self.checkForNewStockingEvents(
            self.scraped_data, last_scraped_data
        )
        if len(self.new_events) > 0:
            self.log("New stocking events")
            self.log("\n\n".join(self.new_events))
            self.log("dumping new data to file...")
            self.dumpScrapedDataToFile(
                self.scraped_data, self.scraped_data_file, self.date_time_str
            )

    def log(self, s):
        if self.logwriter:
            self.logwriter.write(s + "\n")
        else:
            print(s)

    def downloadData(self, url):
        """
        Downloads the stocking information and returns a string of the result
        """
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.text
            fish_data = data
        else:
            self.log(f"Request failed with status code: {response.status_code}")
            fish_data = ""

        return fish_data

    def parseFishData(self, spots, data):
        """
        Parses the latest stocking event data into a list of event descriptions
        """
        lines = data.split("\n")
        for i, line in enumerate(lines):
            if any(spot in line for spot in spots):
                self.scraped_data.append(self.scrapeStockingData(lines, i))

    def loadLastScrapedData(self, scraped_data_file):
        """
        Loads the scraped data file to a string
        """
        with open(scraped_data_file, "r", encoding="utf-8") as f:
            scraped_data_raw = f.readlines()
            scraped_data = [d.replace("\n", "") for d in scraped_data_raw]
        try:
            self.last_update = datetime.strptime(
                scraped_data[0].replace("Last Update: ", ""), "%Y-%m-%d %H:%M:%S"
            )
        except IndexError:
            self.last_update = datetime(2020, 1, 1)

        return scraped_data[1:]

    @staticmethod
    def checkForNewStockingEvents(scraped_data, last_scraped_data):
        """
        Compares current stocking events against saved events to see if any new data is available
        """
        new_events = []
        lsd_set = set(last_scraped_data)
        for entry in scraped_data:
            if entry not in lsd_set:
                new_events.append(entry)
        return new_events

    @staticmethod
    def dumpScrapedDataToFile(scraped_data, file, time_str):
        """
        Dumps the scraped data to a file
        """
        # Format the date and time as a string
        with open(file, "w", encoding="utf-8") as f:
            f.write(f"Last Update: {time_str}\n")
            for entry in scraped_data:
                f.write(entry)
                f.write("\n")

    @staticmethod
    def scrapeStockingData(lines, i):
        """
        Scrapes the stocking data out of the data string for a stocking event
        """
        spot = lines[i].split(">")[-2].split("</")[-2]
        species = lines[i + 2].split(">")[-2].split("</")[-2]
        quantity = lines[i + 3].split(">")[-2].split("</")[-2]
        size = lines[i + 4].split(">")[-2].split("</")[-2]
        date = lines[i + 5].split(">")[-2].split("</")[-2]
        return f"{quantity} {species} ({size} in) were stocked at {spot} on {date}"

    @staticmethod
    def checkShouldSendLogs(logfile, current_time, timeout):
        """Determines if logs should be emailed now

        Args:
            logfile (string): log file with full path
            current_time (datetime): current time
            timeout (int): frequency(days) to send the logs (if 0, dont send)

        Returns:
            bool: whether to send logs
        """

        if timeout == 0:
            return False
        should_send_logs = False

        with open(logfile, "r", encoding="utf-8") as f:
            _ = f.readline()
            first_line = f.readline()
            if first_line:
                try:
                    log_start = datetime.strptime(
                        first_line.split("-----")[1].replace("running ", ""),
                        "%Y-%m-%d %H:%M:%S",
                    )
                except IndexError:
                    print("no start time")
                    log_start = datetime(2020, 1, 1)
                time_since_update = current_time - log_start
                should_send_logs = time_since_update.days > timeout
        return should_send_logs
