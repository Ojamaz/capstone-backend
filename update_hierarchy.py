from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "password"  

# Define the hierarchy mapping
hierarchy_map = {
    "Antimatter Physics": ["Physics", "Particle Physics"],
    "Quantum Mechanics": ["Physics", "Quantum Theory"],
    "Laser Technology": ["Physics", "Optics"],
    "Medicinal Chemistry": ["Chemistry", "Pharmaceuticals"],
    "Quantum Computing": ["Technology", "Computing", "Quantum"],
    "Light Microscopy": ["Technology", "Imaging"],
    "Modern Astronomy": ["Physics", "Astronomy"],
    "Theory of Relativity": ["Physics", "Relativity"],
    "Electric Devices": ["Engineering", "Electrical"],
    "Nanoscale Imaging": ["Technology", "Nanoscience"],
    "Genetic Engineering": ["Biology", "Genetics"],
    "Copernican Astronomy": ["Physics", "Astronomy", "History"],
    "Military Aviation": ["Engineering", "Aerospace"],
    "Metal Production": ["Engineering", "Materials"],
    "Fossil Biology": ["Biology", "Paleontology"],
    "Early Computers": ["Technology", "Computing", "History"],
    "Heart Scanning": ["Medicine", "Cardiology", "Imaging"],
    "Steam Engines": ["Engineering", "Mechanical"],
    "Ancient Weaponry": ["History", "Warfare"],
    "Data Encoding": ["Technology", "Information Theory"],
    "Measurement Tools": ["Engineering", "Instrumentation"],
    "Sound Recording": ["Engineering", "Audio"],
    "Transistor Circuits": ["Technology", "Electronics"],
    "Bayesian Algorithms": ["Mathematics", "Statistics", "Bayesian"],
    "Behavioral Psychology": ["Social Science", "Psychology"],
    "Cancer Treatment": ["Medicine", "Oncology"],
    "Industrial Printing": ["Engineering", "Manufacturing"],
    "Electromagnetic Theory": ["Physics", "Electromagnetism"],
    "Plastic Materials": ["Chemistry", "Polymers"],
    "Computer Memory": ["Technology", "Computing", "Hardware"],
    "Gas Pressure Systems": ["Physics", "Thermodynamics"],
    "Immunization": ["Biology", "Immunology"],
    "Probability Distributions": ["Mathematics", "Statistics"],
    "Nuclear Magnetics": ["Physics", "Spectroscopy"],
    "Particle Physics Models": ["Physics", "Theoretical Physics"],
    "Statistical Inference": ["Mathematics", "Statistics"],
    "Timekeeping Devices": ["Engineering", "Instrumentation"],
    "Tissue Staining": ["Biology", "Histology"],
    "Brain Surgery": ["Medicine", "Neurosurgery"],
    "Rechargeable Batteries": ["Engineering", "Energy"],
    "Chemical Reactions": ["Chemistry", "Organic Chemistry"],
    "Earthquake Science": ["Earth Science", "Geophysics"],
    "Atomic Energy": ["Physics", "Nuclear"],
    "Glue Chemistry": ["Chemistry", "Materials"],
    "Dating Fossils": ["Earth Science", "Geochronology"],
    "Statistical Thermodynamics": ["Physics", "Statistical Mechanics"],
    "Fertility Treatment": ["Medicine", "Reproductive Health"],
    "Mathematical Proofs": ["Mathematics", "Pure Math"],
    "Computer Graphics": ["Technology", "Graphics"],
}

# Cypher updater
def update_hierarchy(driver, hierarchy_map):
    with driver.session() as session:
        for topic, hierarchy in hierarchy_map.items():
            session.run(
                """
                MATCH (t:Topic {name: $name})
                SET t.hierarchy = $hierarchy
                """,
                name=topic,
                hierarchy=hierarchy
            )

# Main updater function
def main():
    driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))
    update_hierarchy(driver, hierarchy_map)
    driver.close()
    print("✅ Hierarchy fields updated successfully in Neo4j.")

main()
