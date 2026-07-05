from flask import Flask, request, jsonify, render_template
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

app = Flask(__name__)

model = None

def get_model():
    global model
    if model is None:
        import torch
        # Restrict PyTorch to a single thread to save memory on free tiers
        torch.set_num_threads(1)
        print("Loading sentence-transformers model (all-MiniLM-L6-v2)...")
        model = SentenceTransformer("all-MiniLM-L6-v2")
        print("Model loaded.")
    return model

DEFAULT_SENTENCES = [
    "The cat sat quietly on the warm windowsill.",
    "A kitten was resting on the sunny window ledge.",
    "The stock market crashed sharply this morning.",
    "Investors panicked as share prices plummeted today.",
    "She learned to play the guitar over the summer.",
    "He spent the summer practicing chords on his guitar.",
    "The recipe requires two cups of flour and one egg.",
    "Artificial intelligence is transforming how we work.",
    "Machine learning models can now understand human language.",
    "It rained heavily throughout the entire weekend.",
]


def compute_similarity(sentences):
    m = get_model()
    embeddings = m.encode(sentences, convert_to_numpy=True)
    sim_matrix = cosine_similarity(embeddings)

    n = len(sentences)
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            pairs.append({
                "i": i,
                "j": j,
                "sentence_a": sentences[i],
                "sentence_b": sentences[j],
                "score": round(float(sim_matrix[i][j]), 4),
            })

    pairs_sorted = sorted(pairs, key=lambda x: x["score"], reverse=True)

    centered = embeddings - embeddings.mean(axis=0)
    _, _, vt = np.linalg.svd(centered, full_matrices=False)
    coords_2d = centered @ vt[:2].T

    coords_min = coords_2d.min(axis=0)
    coords_max = coords_2d.max(axis=0)
    coords_range = np.where((coords_max - coords_min) == 0, 1, coords_max - coords_min)
    coords_norm = ((coords_2d - coords_min) / coords_range) * 80 + 10

    return {
        "sentences": sentences,
        "matrix": [[round(float(v), 4) for v in row] for row in sim_matrix],
        "pairs": pairs_sorted,
        "top_pairs": pairs_sorted[:5],
        "coords": [{"x": round(float(x), 2), "y": round(float(y), 2)} for x, y in coords_norm],
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/default", methods=["GET"])
def default():
    return jsonify({"sentences": DEFAULT_SENTENCES})


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    sentences = data.get("sentences", [])

    sentences = [s.strip() for s in sentences if s.strip()]

    if len(sentences) < 3:
        return jsonify({"error": "Please provide at least 3 sentences."}), 400
    if len(sentences) > 15:
        return jsonify({"error": "Please provide no more than 15 sentences for a clear visualization."}), 400

    result = compute_similarity(sentences)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, port=5002)
