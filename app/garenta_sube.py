import requests
from bs4 import BeautifulSoup as bs
import json

url = "https://www.garenta.com.tr/garenta-subeleri/?_gl=1*150io00*_up*MQ..&gclid=Cj0KCQjwiMmwBhDmARIsABeQ7xSeOe7stkUI9Ia47bjifty81NriCb8HoAtw_cH0UlZFtj3m3uVzSv4aAr1yEALw_wcB"

re = requests.get(url)
print(re.status_code)

soup = bs(re.content, "html.parser")
result = soup.find_all("div", class_="offices_links")
print(len(result))

loc_dict = {}
for sube in result:
    links = sube.find_all("a")
    loc = (float(links[0]["data-latitude"]), float(links[0]["data-longitude"])) # lat long
    loc_name = links[1]["href"].split("/")[1]
    loc_dict[loc_name] = loc
    #print(links[1]["href"].split("/")[1])

with open("app/garenta_sube.json", "w") as f:
    json.dump(loc_dict, f, indent=4)

