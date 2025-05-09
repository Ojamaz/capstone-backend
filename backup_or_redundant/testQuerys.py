import csv
from SPARQLWrapper import SPARQLWrapper, JSON

#Set up the SPARQL endpoint
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

#Set up the query
sparql.setQuery("""
    SELECT ?concept ?conceptLabel ?description ?fieldLabel WHERE  {
  VALUES ?conceptClass { 
    wd:Q11234   # scientific principle
    wd:Q12136   # scientific theory
    wd:Q223557  # physical phenomenon
    wd:Q4026292 # technological field
    wd:Q1798053 # natural science
                
  }
  
  ?concept wdt:P31 ?conceptClass;
           rdfs:label ?conceptLabel;
           schema:description ?description.

  OPTIONAL { ?concept wdt:P279 ?field. }  #Field or subclass
  
  FILTER (LANG(?conceptLabel) = "en")
  FILTER (LANG(?description) = "en")

  #attempting to remove unwanted entries
  FILTER NOT EXISTS { ?concept wdt:P31 wd:Q11436 }        # Exclude inventions (prototypes, aircraft, etc.)
  FILTER NOT EXISTS { ?concept wdt:P31 wd:Q1062836 }      # Exclude aircraft models
  FILTER NOT EXISTS { ?concept wdt:P31 wd:Q170635 }       # Exclude military aircraft
  FILTER NOT EXISTS { ?concept wdt:P31 wd:Q30612 }        # Exclude general aircraft
  FILTER NOT EXISTS { ?concept wdt:P31 wd:Q1457376 }      # Exclude bombers
    

  FILTER NOT EXISTS { ?concept wdt:P31 wd:Q13442814 }     # Exclude brands
  FILTER NOT EXISTS { ?concept wdt:P31 wd:Q431289 }       # Exclude brand items
  FILTER NOT EXISTS { ?concept wdt:P31 wd:Q7889 }         # Exclude chemical elements
  
  FILTER NOT EXISTS { ?concept wdt:P31 wd:Q838948 }       # Exclude artworks
  FILTER NOT EXISTS { ?concept wdt:P31 wd:Q220659 }       # Exclude artifacts
    FILTER NOT EXISTS { ?concept wdt:P31 wd:Q35120 }        # Exclude historical objects
  FILTER NOT EXISTS { ?concept wdt:P31 wd:Q860861 }       # Exclude cosmetic objects
  FILTER NOT EXISTS { ?concept wdt:P31 wd:Q1327215 }      # Exclude miscellaneous objects
  FILTER NOT EXISTS { ?concept wdt:P31 wd:Q131578 }       # Exclude art objects
  FILTER NOT EXISTS { ?concept wdt:P31 wd:Q1183543 }      # Exclude historical artifacts

  FILTER NOT EXISTS { ?concept wdt:P31 wd:Q47461344 }     # Exclude musical instruments
  FILTER NOT EXISTS { ?concept wdt:P31 wd:Q31855 }        # Exclude fictional characters

  #Exclude specific terms in labels to filter out unwanted entries
  FILTER ( !CONTAINS(LCASE(?conceptLabel), "art") )
  FILTER ( !CONTAINS(LCASE(?conceptLabel), "instrument") )
  FILTER ( !CONTAINS(LCASE(?conceptLabel), "music") )

LIMIT 1000

""")

#set the return format
sparql.setReturnFormat(JSON)
sparql.addCustomHttpHeader("User-Agent", "MyCapstoneProjectBot/1.0 (https://myprojecturl.example.com)")

#query and parse the results
try:
    results = sparql.query().convert()

    #creates a set to avoid duplicates
    seen_concepts = set()

    #write results to CSV
    with open("scientific_concepts.csv", mode="w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Concept", "Description", "Field"])

        for result in results["results"]["bindings"]:
            concept = result["conceptLabel"]["value"]
            description = result["description"]["value"]
            field = result.get("fieldLabel", {}).get("value", "Unknown")
            
            entry = (concept, description, field)
            
            #only write the entry if it's not already seen
            if entry not in seen_concepts:
                writer.writerow([concept, description, field])
                seen_concepts.add(entry)

    print("Data has been saved to broad_scientific_concepts_no_duplicates.csv without duplicates or aircraft/military entries")

except Exception as e:
    print("An error occurred:", e)
