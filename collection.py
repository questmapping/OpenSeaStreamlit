# Fetch a full collection (knowing that response limit is 50 at a time)

# Siccome le collezioni possono essere anche grandi, è meglio lanciare questo script una volta sola
# e spingere l'output in un json file al quale vi si può accedere in futuro

import requests
import json

line = input("Quale Collezione:\n").rstrip()
 
collection_url = "https://api.opensea.io/api/v1/assets"

offset = 0

data = {'assets':[]}

print("Starting Data Mining, please wait...")

#pk is primary key
while True:

    collection_params = {
        'collection':line,
        'offset':offset,
        'limit':50,
        'order_by':'pk',
        'order_direction':'asc'
    }

    r = requests.get(collection_url, params=collection_params).json()

    # metodo rapido di aggiungere dati
    data['assets'].extend(r['assets'])

    # continua ad iterare finchè ci sono paginazioni da mostrare
    if len(r['assets']) < 50:
        break

    offset += 50

with open('full_collection.json', 'w') as f:
    json.dump(data, f)

print('Data Mined. Enjoy!')