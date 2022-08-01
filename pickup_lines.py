# pickup_lines.py
# This file will contain methods that are used to generate pickup lines.
# 8/1/22
#

import requests
import bs4
import random


# This method will generate a random pickup line using the ponly.com resource.
def generate_ponly_line():
    # Send a get request to the html page, we will parse it using the BeautifulSoup framework.
    html_contents: str = requests.get("https://ponly.com/200-pick-up-lines/").text
    soup: bs4.BeautifulSoup = bs4.BeautifulSoup(html_contents, "html.parser")

    # All the lines seem to have the p1 class associated with them.
    pickup_lines: [] = soup.find_all("p", class_="p1")

    # Return a random one.
    choice: str = random.choice(pickup_lines).text

    return choice[choice.find(".") + 2:]
