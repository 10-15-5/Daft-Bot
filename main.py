from bs4 import BeautifulSoup
import requests
import json


# Creating a connction with the daft.ie website and adding headers
headers = {"User-Agent": "Mozilla/5.0 (Linux; U; Android 4.2.2; he-il; NEO-X5-116A Build/JDQ39) AppleWebKit/534.30 ("
                         "KHTML, like Gecko) Version/4.0 Safari/534.30"}

response = requests.get("https://www.daft.ie/property-for-rent/kildare?numBeds_from=4", headers=headers)
webpage = response.content

# Parsing the webpage with Beautiful Soup
soup = BeautifulSoup(webpage, "html.parser")

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

#print(gaffs)

# with open("gaffs.json", "r") as file_read:
#     json_object = json.load(file_read)

# print(json_object)
    
# file_read.close()


with open("gaffs.json", "a+") as file:
    file.write(json.dumps(gaffs, indent=4) + ",\n")
file.close()
