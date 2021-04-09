# -*- coding: utf-8 -*-
"""
Created on Thu Apr 9
@author: SE

Requirements:
This is an API with the last 30 days by hour of bitcoin prices.
https://api.coinranking.com/v1/public/coin/1/history/30d

From that, output a JSON file, or display on a browser or endpoint values in this format:
[
{
    "date": "{date}",
    “price”: ”{value}",
    "direction": "{up/down/same}",
    "change": "{amount}",
    "dayOfWeek": "{name}”,
    "highSinceStart": "{true/false}”,
    “lowSinceStart": "{true/false}”
}
]

- date in format "2019-03-17T00:00:00"
- one entry per day at "00:00:00" hours
- results ordered by oldest date first.
- "direction" is direction of price change since previous day in the list, first day can be “na” ({up/down/same})
- "change" is the price difference between current and previous day. “na” for first
- "day of week" is name of the day (Saturday, Tuesday, etc)
- "high since start” / “low since start” is if this is the highest/lowest price since the oldest date in the list.
"""

import urllib, json 
from datetime import datetime
from flask import Flask

app = Flask(__name__)

@app.route("/")
def sort_proces():
    with urllib.request.urlopen("https://api.coinranking.com/v1/public/coin/1/history/30d") as url:
        data1 = json.loads(url.read().decode())
        
    ret=[]
    tzero = datetime.strptime("00:00:00", '%H:%M:%S').time()    
    data=sorted([x for x in data1['data']['history'] if datetime.utcfromtimestamp(x["timestamp"]/1000).time() == tzero], key=lambda item: item['timestamp'])
    mx, mn, prev_price = 0, 0, 0
    for d in data:   
        dd=datetime.utcfromtimestamp(d['timestamp']/1000)
        sdate=dd.strftime('%Y-%m-%dT%H:%M:%SZ')        
        dayOfWeek=dd.strftime('%A')
        price=float(d['price'])
        if len(ret)==0:
            direction='na'
            change='na'
            highSinceStart=True
            lowSinceStart=True
            mn=price 
            mx=price
        else:              
            if prev_price<price:
                direction='up'
            elif prev_price>price:
                direction='down'  
            else:
                direction='same'  
            change=price-prev_price   
            if mx>price:
                highSinceStart=False
            else:
                highSinceStart=True         
            if mn<price:
                lowSinceStart=False
            else:
                lowSinceStart=True
            if price > mx:
                mx=price
            if price < mn:
                mn=price                 
        prev_price=price
        ret.append({'date': sdate, 'price':price, 'direction':direction, 'change':change, 'dayOfWeek':dayOfWeek, 'highSinceStart':highSinceStart, 'lowSinceStart':lowSinceStart})     
    return json.dumps(ret) 

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
