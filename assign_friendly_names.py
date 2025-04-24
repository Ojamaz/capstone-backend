import json
import pandas as pd

# Load clustered data
with open("discoveries_with_topics.json", "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data)

# Manually defined topic name mapping
friendly_names = {
    0: "Antimatter Physics",
    1: "Quantum Mechanics",
    2: "Laser Technology",
    3: "Medicinal Chemistry",
    4: "Quantum Computing",
    5: "Light Microscopy",
    6: "Modern Astronomy",
    7: "Theory of Relativity",
    8: "Electric Devices",
    9: "Nanoscale Imaging",
    10: "Genetic Engineering",
    11: "Copernican Astronomy",
    12: "Military Aviation",
    13: "Metal Production",
    14: "Fossil Biology",
    15: "Early Computers",
    16: "Heart Scanning",
    17: "Steam Engines",
    18: "Ancient Weaponry",
    19: "Data Encoding",
    20: "Measurement Tools",
    21: "Sound Recording",
    22: "Transistor Circuits",
    23: "Bayesian Algorithms",
    24: "Behavioral Psychology",
    25: "Cancer Treatment",
    26: "Industrial Printing",
    27: "Electromagnetic Theory",
    28: "Plastic Materials",
    29: "Computer Memory",
    30: "Gas Pressure Systems",
    31: "Immunization",
    32: "Probability Distributions",
    33: "Nuclear Magnetics",
    34: "Particle Physics Models",
    35: "Statistical Inference",
    36: "Timekeeping Devices",
    37: "Tissue Staining",
    38: "Brain Surgery",
    39: "Rechargeable Batteries",
    40: "Chemical Reactions",
    41: "Earthquake Science",
    42: "Atomic Energy",
    43: "Glue Chemistry",
    44: "Dating Fossils",
    45: "Statistical Thermodynamics",
    46: "Fertility Treatment",
    47: "Mathematical Proofs",
    48: "Computer Graphics",
}


# Replace numeric topic labels with friendly names
df["topic_label"] = df["topic_id"].apply(lambda x: friendly_names.get(x, f"Topic {x}") if x != -1 else "Unsorted Discoveries")



# Define hierarchy map
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

hierarchy_map["Unsorted Discoveries"] = ["Unsorted"]


# Assign hierarchy path to each row
df["topic_hierarchy"] = df["topic_label"].apply(lambda x: hierarchy_map.get(x, ["Uncategorized"]))

# Save updated file
df.to_json("discoveries_with_friendly_topics.json", orient="records", indent=2)
print("Friendly topic names assigned and saved to 'discoveries_with_friendly_topics.json'")

topics = sorted([t for t in df["topic_label"].unique() if t != "Unsorted Discoveries"])
topics.append("Unsorted Discoveries")


# Print how many nodes are in each category
print("\n Topic Counts:")
topic_counts = df["topic_label"].value_counts()
for label, count in topic_counts.items():
    print(f"{label}: {count} nodes")
