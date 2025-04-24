import json
import pandas as pd
import re
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from bertopic.representation import KeyBERTInspired



# ---------- Settings ----------
NR_TOPICS = 50  # Final number of topics after reduction
MIN_TOPIC_SIZE = 3  # Minimum documents per topic
EMBEDDING_MODEL_NAME = "all-mpnet-base-v2"


# ---------- Load Data ----------
with open('json files/discoveries.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

df = pd.DataFrame(data)

# ---------- Preprocess Text ----------
def preprocess_text(text):
    text = re.sub(r'\[\d+\]', '', text)
    text = re.sub(r'[\(\)\/;]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

df["clean_text"] = df["description"].fillna("").apply(preprocess_text)

# ---------- Embedding Model ----------
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

# ---------- Topic Modeling ----------
topic_model = BERTopic(
    embedding_model=embedding_model,
    verbose=True,
    min_topic_size=MIN_TOPIC_SIZE,
    calculate_probabilities=True
)

topics, probs = topic_model.fit_transform(df["clean_text"])

# ---------- Reduce and Refine Topics ----------
topic_model.reduce_topics(df["clean_text"], nr_topics=NR_TOPICS)
representation_model = KeyBERTInspired()
topic_model.update_topics(df["clean_text"], representation_model=representation_model)

# ---------- Inspect Topic Words for Manual Naming ----------
for topic_id in topic_model.get_topics():
    if topic_id == -1:
        continue
    print(f"Topic {topic_id}: {[word for word, _ in topic_model.get_topic(topic_id)]}")

# ---------- Assign Topics ----------
topics, _ = topic_model.transform(df["clean_text"])
df["topic_id"] = topics

def safe_get_label(x):
    if x == -1:
        return "Unclustered"
    topic = topic_model.get_topic(x)
    if topic and isinstance(topic, list) and len(topic) > 0:
        return topic[0][0]
    return f"Topic {x}"

df["topic_label"] = df["topic_id"].apply(safe_get_label)

# ---------- Save Output ----------
df.to_json('discoveries_with_topics.json', orient='records', indent=2)
print("\n Done. Topics refined and saved to discoveries_with_topics.json")