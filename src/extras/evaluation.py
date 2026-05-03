from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def semantic_consistency(captions):
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(captions)
    sim = cosine_similarity(X)
    return sim.mean()

def redundancy_rate(captions):
    unique = set(captions)
    return 1 - len(unique) / len(captions)

def annotation_metrics(captions):
    return {
        "semantic_consistency": semantic_consistency(captions),
        "redundancy_rate": redundancy_rate(captions),
        "avg_caption_length": sum(len(c.split()) for c in captions) / len(captions)
    }
