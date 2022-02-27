import requests
import json
import os
import logging
import smtplib
import configparser
import re
import time

from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# ------------------------------------------------------------------
#   Logging Setup
# ------------------------------------------------------------------

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%d-%m-%y %H:%M:%S')

file_handler = logging.FileHandler("settings/logs.log", encoding='utf8')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

# ------------------------------------------------------------------

config = configparser.RawConfigParser()
configFilePath = r"settings/config.txt"
config.read(configFilePath, encoding="utf-8")


def main():

    while(True):
        # Creating a connction with the daft.ie website and adding headers
        headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:24.0) Gecko/20100101 Firefox/24.0"}

        response = requests.get(config.get("CONFIG", "DAFT_URL"), headers=headers)
        webpage = response.content

        # Parsing the webpage with Beautiful Soup
        soup = BeautifulSoup(webpage, "html.parser")

        gaffs = parse_webpage(soup)

        if not os.path.exists("gaffs.json"):
            new_gaffs = new_file_write(gaffs)
            msg = "First run of program, gaffs found: " + str(new_gaffs)
            logger.info(msg)
            send_email(new_gaffs)
        else:
            new_gaffs = file_write_and_check(gaffs)
            if len(new_gaffs) == 0:
                msg = "No new gaffs found"
            else:
                msg = "New gaff(s) found: " + str(new_gaffs)
            logger.info(msg)
        
        time.sleep(int(config.get("CONFIG", "WAIT_PERIOD")))

def parse_webpage(soup):

    gaffs = []

    gaff = soup.find_all(class_=config.get("CONFIG", "GAFF_CLASS"))
    beds = soup.find_all(class_=config.get("CONFIG", "BEDS_CLASS"))
    price = soup.find_all(class_=config.get("CONFIG", "PRICE_CLASS"))

    for i in gaff:
        gaff = {"address": i.text}
            
        gaffs.append(gaff)

    count = 0
    for j in beds:
        if "Bed" in j.text:
            gaffs[count].update({"beds": j.text})
            count += 1

    count = 0
    for k in price:
        if re.match("^€[1-9]", k.text):
            k_text = (k.text).replace("€", "")
            gaffs[count].update({"price": k_text})
            count += 1

    return gaffs


def new_file_write(gaffs):
    with open("gaffs.json", "w") as file:
        file.write(json.dumps(gaffs, indent=4))
    file.close()

    return gaffs


def file_write_and_check(gaffs):
    new_gaffs = []

    with open("gaffs.json", "r") as file_read:
        json_object = json.load(file_read)

    for i in range(len(gaffs)):
        if gaffs[i] not in json_object:
            new_gaffs.append(gaffs[i])

    file_read.close()

    if len(new_gaffs) > 0:
        for j in range(len(new_gaffs)):
            json_object.append(new_gaffs[j])
        with open("gaffs.json", "w") as file:
            file.write(json.dumps(json_object, indent=4))
        file.close()
        send_email(new_gaffs)
    elif len(gaffs) < len(json_object) and len(new_gaffs) == 0:
        with open("gaffs.json", "w") as file:
            file.write(json.dumps(gaffs, indent=4))
        file.close()
    return new_gaffs


def send_email(gaffs):
    smtp = smtplib.SMTP(config.get("CONFIG", "SMTP_SERVER"), config.get("CONFIG", "SMTP_PORT"))

    receiving_emails = config.get("CONFIG", "SMTP_RECEIVING_EMAIL").split(",")
    
    try:
        email_content = "Gaffs to rent: \n\n"
        for i in range(len(gaffs)):
            email_content += "\n" + "Address:\t" + str(gaffs[i]["address"])
            email_content += "\n" + "Beds:\t" + str(gaffs[i]["beds"])
            email_content += "\n" + "Price:\t" + "€" + str(gaffs[i]["price"]) + "\n"

        smtp.ehlo()
        smtp.starttls()

        smtp.login(config.get("CONFIG", "SMTP_SENDING_EMAIL"), config.get("CONFIG", "SMTP_PASSWORD"))

        for email in receiving_emails:
            message = MIMEMultipart()
            message["Subject"] = "Daft Gaff Update"
            message["From"] = config.get("CONFIG", "SMTP_SENDING_EMAIL")
            message["To"] = email
            message.attach(MIMEText(email_content))

            smtp.sendmail(
                from_addr=config.get("CONFIG", "SMTP_SENDING_EMAIL"),
                to_addrs=email,
                msg=message.as_string()
            )

            logger.info("Email successfully sent to:\t" + email)
    except Exception as e:
        logger.error(e)
    
    smtp.quit()


if __name__ == "__main__":
    main()