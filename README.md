# Daft-Bot
A web scraper written in Python to go to a specific address on daft and find certain houses

## How it works
* update `settings/config.txt` with:
    - the URL to search on daft
    - the class name for displaying the house address
    - the class name for displaying the amount of beds
    - the class name for displaying the proce of the house
    - the email address sending the emails
    - the receiving emails, if you're sending to more than one, sepearte them by commas
    - the password for the sending email
    - the SMTP address for the sending mail
    - the port number for SMTP access
* Start the program with `python main.py`
* A JSON file called "gaffs" and a log file will be created on first run
* After that, on every run, an email will be sent to the receiving emails only if a new house is found
    - This stops the program from sending an email every time with the same list of houses
