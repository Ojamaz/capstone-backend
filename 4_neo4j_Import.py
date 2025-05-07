import json
import pandas as pd
from neo4j import GraphDatabase

# --- Load your JSON data ---
with open("json files/discoveries_with_friendly_topics.json", "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data)

# --- Neo4j connection setup ---
uri = "bolt://localhost:7687"
username = "neo4j"
password = "password"

driver = GraphDatabase.driver(uri, auth=(username, password))

# --- Function to import discoveries ---
def import_discovery(tx, discovery):
    query = """
    
    MERGE (d:Discovery {id: $id})
    SET   d.name = $name,
          d.year = $year

    
    MERGE (primary_topic:Topic {name: $topic_label})
      ON CREATE SET primary_topic.hierarchy = $topic_hierarchy
      ON MATCH  SET primary_topic.hierarchy =
                   coalesce(primary_topic.hierarchy, $topic_hierarchy)
    MERGE (d)-[:BELONGS_TO]->(primary_topic)

    WITH d, $topic_hierarchy AS topic_hierarchy

    UNWIND topic_hierarchy AS topic_name
      MERGE (t:Topic {name: topic_name})
        ON CREATE SET t.hierarchy = topic_hierarchy
        ON MATCH  SET t.hierarchy =
                     coalesce(t.hierarchy , topic_hierarchy)
      MERGE (d)-[:IN_HIERARCHY]->(t)
    """

    tx.run(query, **discovery)


# --- Clear existing data (run once at start) ---
with driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")

print("Importing...")
# --- Import Data into Neo4j ---
with driver.session() as session:
    for _, row in df.iterrows():
        discovery_data = {
            "id": row["id"],
            "name": row["name"].strip('"'),
            "year": row["year"].strip('"') if isinstance(row["year"], str) else row["year"],
            "topic_label": row["topic_label"].strip('"'),
            "topic_hierarchy": [x.strip('"') for x in row["topic_hierarchy"]]
        }

        session.execute_write(import_discovery, discovery_data)

print("Data imported with BELONGS_TO relationships")

driver.close()
