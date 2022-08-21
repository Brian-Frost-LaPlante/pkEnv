from bs4 import BeautifulSoup as bs
import requests
from os.path import basename

for i in range(1,152):
    if i<10:
        numstr = '00'+str(i)
    elif i<100:
        numstr = '0'+str(i)
    else:
        numstr = str(i)

    image_url = 'https://www.serebii.net/pokearth/sprites/green/'+numstr+'.png'

    with open(basename(image_url), "wb") as f:
        f.write(requests.get(image_url).content)
