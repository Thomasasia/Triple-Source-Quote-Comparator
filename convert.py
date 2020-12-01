import pandas as pd
import json

text = []

def validateJSON(jsonData):
    try:
        dic = json.loads(jsonData)
        if dic.get("reviewText") is not None:
            text.append(dic["reviewText"])
    except ValueError as err:
        return False
    return True

f = open('videogames1.json')

l = 1
for line in f:
    val = validateJSON(line)
    if not val:
        print(l)
    l +=1
f.close()
f = open("reviews.csv","a")

for t in text:
    f.write(t)
    
    
f.close()






"""
pdObj = pd.read_json('videogames1.json', orient='index')
csvData = pdObj.to_csv('new.csv',index=False)
"""