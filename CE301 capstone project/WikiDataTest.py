import requests

def fetch_wikidata(params):
    url = 'https://www.wikidata.org/w/api.php'
    try:
        response = requests.get(url, params=params)
        return response.json()
    except requests.exceptions.RequestException:
        print("There was an error with the request.")
        return None

def get_entity_id(query):
    params = {
        'action': 'wbsearchentities',
        'format': 'json',
        'search': query,
        'language': 'en'
    }
    data = fetch_wikidata(params)
    if data and 'search' in data and data['search']:
        return data['search'][0]['id']
    return None

def get_entity_data(entity_id):
    params = {
        'action': 'wbgetentities',
        'ids': entity_id,
        'format': 'json',
        'languages': 'en'
    }
    return fetch_wikidata(params)

def get_property_value(entity_data, entity_id, prop_id):
    claims = entity_data['entities'][entity_id]['claims']
    if prop_id in claims:
        claim = claims[prop_id]
        # Get the first statement value
        for statement in claim:
            datavalue = statement['mainsnak'].get('datavalue', {}).get('value')
            if isinstance(datavalue, dict) and 'time' in datavalue:
                # Extracting the date if it's a time object
                return datavalue['time']
            else:
                return datavalue
    return None

def get_related_entity_date(entity_id):
    """
    If the main entity has no discovery date, try finding a discovery date from related entities.
    """
    params = {
        'action': 'wbgetentities',
        'ids': entity_id,
        'format': 'json',
        'languages': 'en',
        'props': 'claims'
    }
    data = fetch_wikidata(params)
    if data:
        entity_data = data['entities'][entity_id]
        #Try 'subclass of' (P279) and 'instance of" relationships for discovery date
        related_properties = ['P279', 'P31']
        for prop_id in related_properties:
            if prop_id in entity_data['claims']:
                for claim in entity_data['claims'][prop_id]:
                    related_entity_id = claim['mainsnak']['datavalue']['value']['id']
                    related_entity_data = get_entity_data(related_entity_id)
                    if related_entity_data:
                        related_date = get_property_value(related_entity_data, related_entity_id, 'P575')
                        if related_date:
                            return related_date
    return None


def get_discovery_date(entity_label):
    entity_id = get_entity_id(entity_label)
    if not entity_id:
        print("Entity not found.")
        return None

    entity_data = get_entity_data(entity_id)
    if not entity_data:
        print("Could not retrieve entity data.")
        return None

    #Attempt to get discovery date directly
    discovery_date = get_property_value(entity_data, entity_id, 'P575')
    if discovery_date:
        return discovery_date

    #If P575 is missing, try related entities
    related_discovery_date = get_related_entity_date(entity_id)
    if related_discovery_date:
        return related_discovery_date

    #return false if no information was found
    return False  

#example Use for 1 topic "enzymes"
entity_label = "Enzyme"
discovery_date = get_discovery_date(entity_label)
print(f"Discovery date for {entity_label}: {discovery_date}")
