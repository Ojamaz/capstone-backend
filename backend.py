from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from neo4j import GraphDatabase

# ---- Neo4j connection ----
driver = GraphDatabase.driver(
        "bolt://localhost:7687",
        auth=("neo4j", "password"))       

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hard-coded colours for the 9 top-level branches 
BRANCH_COLORS = {
    "Physics":       "#00bcd4",
    "Chemistry":     "#ff9800",
    "Biology":       "#4caf50",
    "Medicine":      "#e91e63",
    "Mathematics":   "#9c27b0",
    "Engineering":   "#3f51b5",
    "Technology":    "#009688",
    "Earth Science": "#795548",
    "History":       "#607d8b",
    "Unsorted":      "#9e9e9e"
}

# ---------- Helpers ----------
def run_tx(cypher, **kv):
    with driver.session() as s:
        return list(s.run(cypher, **kv))

# ---------- API ----------
@app.get("/topics")
def all_topics():
    recs = run_tx("""
        MATCH (t:Topic)
        RETURN t.name AS name,
               coalesce(head(t.hierarchy), 'Unsorted') AS branch
    """)
    return [{"name": r["name"], "branch": r["branch"]} for r in recs]

@app.get("/discoveries/{topic_name}")
def discoveries(topic_name: str):
    recs = run_tx("""
        MATCH (d:Discovery)-[:BELONGS_TO]->(t:Topic {name:$topic})
        RETURN d.name AS name,
               d.year AS year,
               d.url  AS url
        ORDER BY toInteger(d.year) ASC
    """, topic=topic_name)
    if not recs:
        raise HTTPException(404, f"No discoveries for {topic_name}")
    return [{"name": r["name"], "year": r["year"], "url": r["url"]} for r in recs]

@app.get("/colour/{branch}")
def colour(branch:str):
    return {"color": BRANCH_COLORS.get(branch, "#9e9e9e")}


# in api/main.py – add at bottom
from neo4j import GraphDatabase


@app.get("/graph")
def full_graph():
    q = """
    MATCH (d:Discovery)-[:BELONGS_TO]->(t:Topic)
    RETURN d.id   AS id,
           d.name AS name,
           coalesce(d.year,'?') AS year,
           t.name  AS topic,
           head(t.hierarchy) AS branch
    """
    rows = run_tx(q)

    # ---- build nodes ----
    topics_seen = {}
    nodes = []
    links = []

    for r in rows:
        # add topic node once
        if r["topic"] not in topics_seen:
            topics_seen[r["topic"]] = True
            nodes.append({
                "id": r["topic"],
                "label": r["topic"],
                "branch": r["branch"] or "Unsorted",
                "level": 0
            })

        # discovery node
        nodes.append({
            "id": r["id"],
            "label": r["name"],
            "year": r["year"],
            "branch": r["branch"] or "Unsorted",
            "level": 1,
            "url": f"https://en.wikipedia.org/wiki/{r['name'].replace(' ', '_')}"
        })

        links.append({"source": r["topic"], "target": r["id"]})

    return {"nodes": nodes, "links": links}


#(to run)
# python -m uvicorn main:app --reload --port 8000 
