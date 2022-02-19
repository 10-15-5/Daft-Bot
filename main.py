from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import requests
import json
import os
import logging
import smtplib


# ------------------------------------------------------------------
#   Logging Setup
# ------------------------------------------------------------------

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%d-%m-%y %H:%M:%S')

file_handler = logging.FileHandler("logs.log", encoding='utf8')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

# ------------------------------------------------------------------


def main():

    # Creating a connction with the daft.ie website and adding headers
    headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:24.0) Gecko/20100101 Firefox/24.0"}

    response = requests.get("https://www.daft.ie/property-for-rent/kildare?numBeds_from=4", headers=headers)
    webpage = response.content

    # Parsing the webpage with Beautiful Soup
    soup = BeautifulSoup(webpage, "html.parser")

    gaffs = parse_webpage(soup)

    if not os.path.exists("gaffs.json"):
        new_gaffs = new_file_write(gaffs)
        msg = "First run of program, gaffs found: " + str(new_gaffs)
        logger.info(msg)
    else:
        new_gaffs = file_write_and_check(gaffs)
        msg = "New gaff(s) found: " + str(new_gaffs)
        logger.info(msg)

def parse_webpage(soup):

    gaffs = []

    gaff = soup.find_all(class_="TitleBlock__Address-sc-1avkvav-7 hRrWbx")
    beds = soup.find_all(class_="TitleBlock__CardInfoItem-sc-1avkvav-8 uaMgE")
    price = soup.find_all(class_="TitleBlock__StyledSpan-sc-1avkvav-4 bNjvqX")

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
        # send_email(new_gaffs)
    send_email(json_object)

    return new_gaffs


def send_email(gaffs):
    sender_email = "xxxxxxxxxx@xxxxxxx.com"
    receiver_email = "xxxxxxxxxx@xxxxxxx.com"

    smtp = smtplib.SMTP("EMAIL SERVER", "EMAIL SERVER PORT")
    
    try:
        email_content = "Gaffs to rent in Kildare: "
        for i in range(len(gaffs)):
            email_content += "\n" + str(gaffs[i])

        smtp.ehlo()
        smtp.starttls()

        smtp.login(sender_email, "SENDER EMAIL PASSWORD")

        message = MIMEMultipart()
        message["Subject"] = "Daft Gaff Update"
        message["From"] = sender_email
        message["To"] = receiver_email
        message.attach(MIMEText(email_content))

        smtp.sendmail(
            from_addr=sender_email,
            to_addrs=receiver_email,
            msg=message.as_string()
        )

        logger.info("Email successfully sent to:\t" + receiver_email)
    except Exception as e:
        logger.error(e)
    
    smtp.quit()



if __name__ == "__main__":
    main()