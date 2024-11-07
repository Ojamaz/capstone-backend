import requests

def fetch_wikidata(params):
    url = 'https://www.wikidata.org/w/api.php'
    try:
        return requests.get(url, params=params)
    except:
        return 'There was and error'
    
# What text to search for
query = 'Enzyme'

# Which parameters to use
params = {
        'action': 'wbsearchentities',
        'format': 'json',
        'search': query,
        'language': 'en'
    }

# Fetch API
data = fetch_wikidata(params)

#show response as JSON
data = data.json()
id = data['search'][0]['id']

# Create parameters
params = {
            'action': 'wbgetentities',
            'ids':id, 
            'format': 'json',
            'languages': 'en'
        }

# fetch the API
data = fetch_wikidata(params)

# Show response
data = data.json()
print(data['entities'][id]['claims'].keys())


