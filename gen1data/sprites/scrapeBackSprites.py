from bs4 import BeautifulSoup as bs
import requests
from os.path import basename

for i in range(1,152):
    numstr = str(i)

    image_url = 'https://pkmn.net/sprites/back/'+numstr+'.PNG'

    with open(basename(image_url), "wb") as f:
        f.write(requests.get(image_url).content)
