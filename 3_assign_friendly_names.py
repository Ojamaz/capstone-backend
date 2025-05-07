import json
import pandas as pd

# Load clustered data
with open("json files/discoveries_with_topics.json", "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data)

# Manually defined topic name mapping
friendly_names = {
     0: "Heart Ultrasound Imaging",
     1: "Space & Galaxy Observation",
     2: "Drug Chemistry",
     3: "Gene-Editing Tools",
     4: "Light Microscopes",
     5: "Quantum Entanglement",
     6: "Industrial Chemicals",
     7: "Relativistic Quantum Physics",
     8: "Atomic Light Spectra",
     9: "High-Power Electronics",
    10: "Military Radar Systems",
    11: "Printing Technologies",
    12: "Statistical Sampling Methods",
    13: "Steel & Iron Making",
    14: "Molecular Modelling",
    15: "Einstein’s Gravity",
    16: "Error-Correcting Codes",
    17: "Classic Physics Experiments",
    18: "Behavioural Psychology",
    19: "Sun-Centred Astronomy",
    20: "Ancient Chinese Weapons",
    21: "Steam Engines",
    22: "Early Computers",
    23: "String Theory Ideas",
    24: "Nano-Scale Conductors",
    25: "Rare Chemical Elements",
    26: "Early Sound Recorders",
    27: "Fusion Reactors",
    28: "Temperature Measuring Tools",
    29: "Antimatter Research",
    30: "Underwater Vehicles",
    31: "Evolutionary Biology",
    32: "Neutrino Research",
    33: "Heat & Statistics",
    34: "Holograms & Interference",
    35: "Magnetic Materials",
    36: "Particle Accelerators",
    37: "Medical Scopes",
    38: "Modern Transistors",
    -1: "Unsorted Discoveries",
}


# Replace numeric topic labels with friendly names
df["topic_label"] = df["topic_id"].apply(lambda x: friendly_names.get(x, f"Topic {x}") if x != -1 else "Unsorted Discoveries")



# Define hierarchy map
hierarchy_map = {
    "Heart Ultrasound Imaging":      ["Medicine", "Cardiology"],
    "Space & Galaxy Observation":    ["Physics", "Astronomy"],
    "Drug Chemistry":                ["Chemistry", "Medicinal"],
    "Gene-Editing Tools":            ["Biology", "Genetics"],
    "Light Microscopes":             ["Technology", "Imaging"],
    "Quantum Entanglement":          ["Physics", "Quantum"],
    "Industrial Chemicals":          ["Chemistry", "Industrial"],
    "Relativistic Quantum Physics":  ["Physics", "Theory"],
    "Atomic Light Spectra":          ["Physics", "Atomic"],
    "High-Power Electronics":        ["Engineering", "Electrical"],
    "Military Radar Systems":        ["Engineering", "Defense"],
    "Printing Technologies":         ["Engineering", "Manufacturing"],
    "Statistical Sampling Methods":  ["Mathematics", "Statistics"],
    "Steel & Iron Making":           ["Engineering", "Materials"],
    "Molecular Modelling":           ["Chemistry", "Computational"],
    "Einstein’s Gravity":            ["Physics", "Relativity"],
    "Error-Correcting Codes":        ["Technology", "Information Theory"],
    "Classic Physics Experiments":   ["Physics", "Foundations"],
    "Behavioural Psychology":        ["Social Science", "Psychology"],
    "Sun-Centred Astronomy":         ["Physics", "Astronomy", "History"],
    "Ancient Chinese Weapons":       ["History", "Military"],
    "Steam Engines":                 ["Engineering", "Mechanical"],
    "Early Computers":               ["Technology", "Computing", "History"],
    "String Theory Ideas":           ["Physics", "Particle Theory"],
    "Nano-Scale Conductors":         ["Physics", "Condensed Matter"],
    "Rare Chemical Elements":        ["Chemistry", "Inorganic"],
    "Early Sound Recorders":         ["Engineering", "Audio"],
    "Fusion Reactors":               ["Physics", "Plasma"],
    "Temperature Measuring Tools":   ["Engineering", "Instrumentation"],
    "Antimatter Research":           ["Physics", "Particle"],
    "Underwater Vehicles":           ["Engineering", "Marine"],
    "Evolutionary Biology":          ["Biology", "Evolution"],
    "Neutrino Research":             ["Physics", "Particle"],
    "Heat & Statistics":             ["Physics", "Statistical"],
    "Holograms & Interference":      ["Physics", "Optics"],
    "Magnetic Materials":            ["Physics", "Magnetism"],
    "Particle Accelerators":         ["Physics", "Accelerator"],
    "Medical Scopes":                ["Medicine", "Diagnostics"],
    "Modern Transistors":            ["Engineering", "Semiconductors"],
    "Unsorted Discoveries":          ["Unsorted"],
}
hierarchy_map["Unsorted Discoveries"] = ["Unsorted"]

# Assign hierarchy path to each row
df["topic_hierarchy"] = df["topic_label"].apply(lambda x: hierarchy_map.get(x, ["Uncategorized"]))

# Save updated file
df.to_json("json files/discoveries_with_friendly_topics.json", orient="records", indent=2)
print("Friendly topic names assigned and saved to 'discoveries_with_friendly_topics.json'")

topics = sorted([t for t in df["topic_label"].unique() if t != "Unsorted Discoveries"])
topics.append("Unsorted Discoveries")

# Print how many nodes are in each category
print("\n Topic Counts:")
topic_counts = df["topic_label"].value_counts()
for label, count in topic_counts.items():
    print(f"{label}: {count} nodes")
