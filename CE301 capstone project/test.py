import json
import pandas as pd

# Load your enriched JSON file
with open("discoveries_with_friendly_topics.json", "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data)

total_entries = len(df)
unique_ids = df["id"].nunique()
topic_counts = df["topic_label"].value_counts()
total_from_topics = topic_counts.sum()

print(f"🔢 Total entries in file: {total_entries}")
print(f"🆔 Unique ID count: {unique_ids}")
print(f"🧮 Total counted via topic labels: {total_from_topics}")
print("\n📊 Per-topic counts:")
print(topic_counts)
