# fishstuff
fish stocking notifier for Utah DWR

This Scraped Info from "https://dwrapps.utah.gov/fishstocking/Fish"

To use it, first edit the `config.yaml` file (or copy it to `config.yaml.local` if you want the changes gitignored) to have the correct email credentials and desired stocking spots notified.

## Email credentials
To get this working with a gmail account, I had to make sure 2fa was on, then create an app password for the email address (probably use a secondary email address as the sender to prevent security issues because this probably isnt super safe)

[Instructions for setting up app password](https://knowledge.workspace.google.com/kb/how-to-create-app-passwords-000009237)

this should be the link to create a new app password [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)

## Running Automatically
To get this to run automatically, just put the script in your crontab (you will need to prevent your computer from going to sleep or signing out to get this to run consistently)

The following line will run the script at 6 am and 6pm every day

```
0 6,18  * * * <username> /path/to/scrape_fish_data.py
```

