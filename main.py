# python -m venv C:\Users\pc\MyCodebase\Streamlit\sltest
# activate
# python -m pip install --upgrade pip
# pip install streamlit
# pip install requests

# pip install wheel
# pip install web3 
# nel caso di errore Visual C++: https://aka.ms/vs/16/release/vs_buildtools.exe
# Install Visual C++ Build tools core features, Visual C++ 2019 Redistributable Update
# like here https://i.stack.imgur.com/lEV8r.png
# then select "Modify" and then "Individual Components" and install the "Windows 10 SDK"
# it shuold ask to reboot. do it

# pip freeze (per vedere le versioni da mettere in requirements.txt)
# streamlit run main.py
# ctrl+C
# deactivate

# principali endpoint delle API di OpenSea https://docs.opensea.io/reference/api-overview

import streamlit as sl
import requests
import json
from web3 import Web3
import pandas as pd

def rendering(asset):
    if asset['name'] is not None:
        sl.subheader(asset['name'])
    else:
        sl.subheader(f"{asset['collection']['name']} n° {asset['token_id']}")
    
    if asset['description'] is not None:
        sl.write(asset['description'])
    else:
        sl.write(asset['collection']['description'])

    if asset['image_url'].endswith('mp4') or asset['image_url'].endswith('mov'):
        sl.video(asset['image_url'])
    elif asset['image_url'].endswith('svg'):
        svg = requests.get(asset['image_url']).content.decode()
        sl.image(svg)
    else:
        sl.image(asset['image_url'])

mainselection = sl.sidebar.selectbox("Cosa Fare",['Assets','Events','Rarity'])

sl.header(f"Esplora le API di OpenSea: {mainselection}")

if mainselection=='Assets':

    sl.sidebar.subheader('Filtri')

    collection = sl.sidebar.text_input('Collection name')

    owner = sl.sidebar.text_input('Owner Address')

    assets_url = "https://api.opensea.io/api/v1/assets"
    assets_params = {
        'offset':0,
        'limit':10,
        'order_by':'sale_price',
        'order_direction':'desc'
    }
       
    if collection:
        assets_params['collection'] = collection
    
    if owner:
        assets_params['owner'] = owner
    
    if owner or collection:
        r = requests.get(assets_url, params=assets_params).json()

        if len(r['assets']):
            #sl.write(r)

            for asset in r['assets']:

                rendering(asset)

        else:
            sl.write('Non trovo Assets con i Filtri indicati')

elif mainselection=='Events':

    events_url = "https://api.opensea.io/api/v1/events"

    events_params = {
        'only_opensea':True,
        'offset':0,
        'limit':10,

    }

    r = requests.get(events_url, params=events_params).json()

    event_list = []
    for event in r['asset_events']:
        if event['event_type'] == 'offer_entered':
            if event['bid_amount']:
                bid_amount = Web3.fromWei(int(event['bid_amount']),'ether')
            if event['from_account']['user']:
                bidder = event['from_account']['user']['username']
            else:
                bidder = event['from_account']['address']
            event_list.append([
                event['created_date'], 
                bidder, 
                float(bid_amount), 
                event['asset']['collection']['name'], 
                event['asset']['token_id']
            ])
    df = pd.DataFrame(event_list, columns=['time', 'bidder', 'bid_amount', 'collection', 'token_id'])

    sl.dataframe(df)


elif mainselection=='Rarity':

    # ci serve la collezione completa da spulciare. Per scaricarla vedi collection.py
    with open('full_collection.json') as f:
        data = json.loads(f.read())
        asset_rarities = []

        for asset in data['assets']:
            
            asset_rarity = 1

            # qual'è la probabilità che ci siano più tratti particolari
            for trait in asset['traits']:
                trait_rarity = trait['trait_count'] / 8888
                asset_rarity *= trait_rarity

            asset_rarities.append({
                'token_id':asset['token_id'],
                'name':f"the-wanderers n°{asset['token_id']}",
                'description':asset['description'],
                'rarity':asset_rarity,
                'traits':asset['traits'],
                'image_url': asset['image_url'],
                'collection':asset['collection']
            })

        assets_sorted = sorted(asset_rarities, key= lambda asset: asset['rarity'], reverse=False)

        for asset in assets_sorted[:10]:
            if asset['rarity']:
                    sl.subheader(f"Rarity Score: {asset['rarity']}")
            rendering(asset)