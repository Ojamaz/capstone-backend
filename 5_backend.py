CONFIG = {
    # Neo4j
    "NEO4J_URI"     : "bolt://localhost:7687",
    "NEO4J_USER"    : "neo4j",
    "NEO4J_PASS"    : "password",

    "FRONTEND_ORIGINS": ["http://localhost:3000"],

    # Branch topics colour (must match React)
    "BRANCH_COLOURS": {
        "Physics"       : "#00bcd4",
        "Chemistry"     : "#ff9800",
        "Biology"       : "#4caf50",
        "Medicine"      : "#e91e63",
        "Mathematics"   : "#9c27b0",
        "Engineering"   : "#3f51b5",
        "Technology"    : "#009688",
        "Earth Science" : "#795548",
        "History"       : "#607d8b",
        "Unsorted"      : "#9e9e9e",
    }
}
# ------------------------------------------------

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder  
from neo4j import GraphDatabase

# ---- Neo4j connection -----------------------------------
driver = GraphDatabase.driver(
    CONFIG["NEO4J_URI"],
    auth=(CONFIG["NEO4J_USER"], CONFIG["NEO4J_PASS"])
)

# ---- FastAPI & CORS -------------------------------------
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=CONFIG["FRONTEND_ORIGINS"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Helpers --------------------------------------
def run_tx(cypher, **kv):
    with driver.session() as s:
        return list(s.run(cypher, **kv))

# ---------- API ------------------------------------------
@app.get("/topics")
def all_topics():
    recs = run_tx("""
        MATCH (t:Topic)<-[:BELONGS_TO]-(d:Discovery)
        WITH t, count(d) AS n
        WHERE n > 0
        RETURN t.name AS name,
               coalesce(head(t.hierarchy), 'Unsorted') AS branch
    """)
    return jsonable_encoder([r.data() for r in recs]) 


@app.get("/discoveries/{topic_name}")
def discoveries(topic_name: str):
    recs = run_tx("""
        MATCH (d:Discovery)-[:BELONGS_TO]->(t:Topic {name:$topic})
        RETURN d.name AS name, d.year AS year,
               'https://en.wikipedia.org/wiki/'+replace(d.name,' ','_') AS url
        ORDER BY toInteger(d.year) ASC
    """, topic=topic_name)

    if not recs:
        raise HTTPException(404, f"No discoveries for {topic_name}")
    return jsonable_encoder([r.data() for r in recs]) 


@app.get("/colour/{branch}")
def colour(branch: str):
    return {"color": CONFIG["BRANCH_COLOURS"].get(branch, "#9e9e9e")}


@app.get("/graph")
def full_graph(topic: str | None = None,
               min_year: int = Query(0,  ge=0),
               max_year: int = Query(3000, le=3000)):

    if topic:
        q = """
        MATCH (d:Discovery)-[:BELONGS_TO]->(t:Topic {name: $topic})
        WHERE coalesce(toInteger(d.year), 0) >= $min_year
          AND coalesce(toInteger(d.year), 3000) <= $max_year
        RETURN d.id AS id, d.name AS name, d.year AS year,
               t.name AS topic, head(t.hierarchy) AS branch
        """
        rows = [r.data() for r in run_tx(q, topic=topic, min_year=min_year, max_year=max_year)]

        topics_seen, nodes, links = {}, [], []
        for r in rows:
            if r["topic"] not in topics_seen:
                topics_seen[r["topic"]] = True
                nodes.append({
                    "id": r["topic"], "label": r["topic"],
                    "branch": r["branch"] or "Unsorted", "level": 0
                })
            nodes.append({
                "id": r["id"], "label": r["name"], "year": r["year"],
                "branch": r["branch"] or "Unsorted", "level": 1,
                "url": f"https://en.wikipedia.org/wiki/{r['name'].replace(' ', '_')}"
            })
            links.append({"source": r["topic"], "target": r["id"]})
        return {"nodes": nodes, "links": links}

    else:
        q = """
        MATCH (t:Topic)<-[:BELONGS_TO]-(d:Discovery)
        WHERE coalesce(toInteger(d.year), 0) >= $min_year
          AND coalesce(toInteger(d.year), 3000) <= $max_year
        WITH t, head(t.hierarchy) AS branch, count(d) AS n
        WHERE n > 0
        RETURN t.name AS topic, branch
        ORDER BY branch, topic
        """
        topic_rows = [r.data() for r in run_tx(q, min_year=min_year, max_year=max_year)]

        branch_nodes, topic_nodes, links = {}, [], []
        for r in topic_rows:
            branch = r["branch"] or "Unsorted"
            topic = r["topic"]

            if branch not in branch_nodes:
                branch_nodes[branch] = {
                    "id": branch, "label": branch,
                    "branch": branch, "level": 0
                }

            topic_nodes.append({
                "id": topic, "label": topic,
                "branch": branch, "level": 1
            })

            links.append({"source": branch, "target": topic})

        return {
            "nodes": list(branch_nodes.values()) + topic_nodes,
            "links": links
        }

#(to run)
# python -m uvicorn 5_backend:app --reload --port 8000
# ------------------------- next -----------------------
# open terminal in front-end folder
# npm start
