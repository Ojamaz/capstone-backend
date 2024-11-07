import requests

def fetch_wikidata(params):
    url = 'https://www.wikidata.org/w/api.php'
    try:
        return requests.get(url, params=params)
    except:
        return 'There was an error'

query = 'Enzyme'

params = {
    'action': 'wbsearchentities',
    'format': 'json',
    'search': query,
    'language': 'en'
}
data = fetch_wikidata(params)
data = data.json()
entity_id = data['search'][0]['id']

params = {
    'action': 'wbgetentities',
    'ids': entity_id,
    'format': 'json',
    'languages': 'en'
}
data = fetch_wikidata(params)
data = data.json()


properties_to_display = ['P31', 'P575']

for prop_id in properties_to_display:
    if prop_id in data['entities'][entity_id]['claims']:
        claim = data['entities'][entity_id]['claims'][prop_id]
        print(f"Property {prop_id}:")
        for statement in claim:
            datavalue = statement['mainsnak'].get('datavalue', {}).get('value')
            print(f" Value: {datavalue}")
    else:
        print(f"Property {prop_id}: No value found")


entity_label = data['entities'][entity_id]['labels']['en']['value']
print(f"Label: {entity_label}")

