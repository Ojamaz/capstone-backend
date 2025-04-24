import json
import pandas as pd
import nltk
import re
from nltk.corpus import stopwords
from gensim.corpora import Dictionary
from gensim.models.ldamulticore import LdaMulticore

def main():
    # ---------- Setup ----------
    nltk.download('punkt')
    nltk.download('stopwords')

    with open('json files/discoveries.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    documents = df['description'].fillna("").tolist()

    stop_words = set(stopwords.words('english'))

    def preprocess(text):
        tokens = re.findall(r'\b\w+\b', text.lower())
        return [t for t in tokens if t.isalpha() and t not in stop_words]

    processed_docs = [preprocess(doc) for doc in documents]

    dictionary = Dictionary(processed_docs)
    corpus = [dictionary.doc2bow(text) for text in processed_docs]

    lda_model = LdaMulticore(
        corpus=corpus,
        id2word=dictionary,
        num_topics=10,
        passes=10,
        workers=2
    )

    topics = []
    for doc_bow in corpus:
        topic_distribution = lda_model.get_document_topics(doc_bow)
        dominant_topic = max(topic_distribution, key=lambda x: x[1])[0]
        topics.append(dominant_topic)

    df['topic_id'] = topics
    df.to_json('discoveries_with_topics.json', orient='records', indent=2)
    print("Done. Saved to discoveries_with_topics.json")

    print("-----------------------------------------------------------------------\n")
    for i in range(20):
        print(f"Topic {i}:")
        print([word for word, _ in lda_model.show_topic(i, topn=10)])
        print()


#Fix for Windows multiprocessing
if __name__ == '__main__':
    main()
