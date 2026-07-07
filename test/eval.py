"""
Retrieval evaluation script for IntellRead.

Purpose:
- Measure whether the retriever actually surfaces the right chunk for a
  given question (precision@k), instead of assuming it does.
- Capture the real distance-score distribution for genuinely relevant vs.
  genuinely irrelevant queries, so DISTANCE_THRESHOLD is set from evidence,
  not guesswork.

Usage:
    python eval_retrieval.py

Requires: the same .env (CHROMA_DIR) as your running app, and a document
already ingested (run /ingest_pdf first).
"""

import os
from dotenv import load_dotenv

load_dotenv()

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

CHROMA_DIR = os.getenv("CHROMA_DIR")
if not CHROMA_DIR:
    raise RuntimeError("CHROMA_DIR not set — check your .env")

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vs = Chroma(collection_name="vectors", embedding_function=embeddings, persist_directory=CHROMA_DIR)

TOP_K = 4

# ---------------------------------------------------------------------------
# EVAL SET
# Each entry: a question, and a substring that should appear in the chunk
# that correctly answers it. `expect_relevant=True` means we expect the
# retriever to find a good match; `False` means this question SHOULDN'T
# match anything in the document (tests the "I don't know" / threshold path).
#
# NOTE: these are based on the Edge Detection & Line Detection PDF
# (Digital Image Processing, MTCS-202). Swap this list out for a different
# eval set if you test against a different document.
# ---------------------------------------------------------------------------
EVAL_SET = [
    {
        "question": "What are the four types of edges in image processing?",
        "expect_substring": "Ramp type",
        "expect_relevant": True,
    },
    {
        "question": "What mask does the Prewitt operator use to detect vertical edges?",
        "expect_substring": "-1 0 1",
        "expect_relevant": True,
    },
    {
        "question": "How is the Sobel operator different from the Prewitt operator?",
        "expect_substring": "coefficients of masks are not fixed",
        "expect_relevant": True,
    },
    {
        "question": "How many orientations does the Robinson compass mask have?",
        "expect_substring": "eight orientations",
        "expect_relevant": True,
    },
    {
        "question": "Who is the Kirsch operator named after?",
        "expect_substring": "Russell A. Kirsch",
        "expect_relevant": True,
    },
    {
        "question": "What is the difference between Laplacian operator and Prewitt, Sobel, Robinson, Kirsch?",
        "expect_substring": "second order derivative",
        "expect_relevant": True,
    },
    {
        "question": "What do you do after applying the positive Laplacian operator to get a sharpened image?",
        "expect_substring": "subtract the resultant",
        "expect_relevant": True,
    },
    {
        "question": "What are the two most popular line detection techniques?",
        "expect_substring": "Hough transform",
        "expect_relevant": True,
    },
    {
        "question": "In the Hough transform example, what are the coordinates given to prove collinearity?",
        "expect_substring": "(1,1)",
        "expect_relevant": True,
    },
    {
        "question": "What is the purpose of edge detection in image processing?",
        "expect_substring": "boundaries of",
        "expect_relevant": True,
    },
    {
        "question": "What is the capital of France?",
        "expect_substring": None,
        "expect_relevant": False,
    },
    {
        "question": "Who won the cricket world cup in 2011?",
        "expect_substring": None,
        "expect_relevant": False,
    },
    {
        "question": "What is the plot of the movie Inception?",
        "expect_substring": None,
        "expect_relevant": False,
    },
    {
        "question": "How do you make a chocolate cake?",
        "expect_substring": None,
        "expect_relevant": False,
    },
    {
        "question": "What is the population of Japan?",
        "expect_substring": None,
        "expect_relevant": False,
    },
]


def run_eval():
    relevant_scores = []
    irrelevant_scores = []
    hits = 0
    total_relevant = 0

    print(f"{'QUESTION':<55} {'BEST_SCORE':<12} {'HIT?':<6} {'EXPECTED'}")
    print("-" * 100)

    for case in EVAL_SET:
        question = case["question"]
        expect_substring = case["expect_substring"]
        expect_relevant = case["expect_relevant"]

        results = vs.similarity_search_with_score(question, k=TOP_K)
        if not results:
            best_score = None
            hit = False
        else:
            best_score = min(score for _, score in results)
            if expect_relevant and expect_substring:
                hit = any(expect_substring.lower() in doc.page_content.lower() for doc, _ in results)
            else:
                hit = None  # not applicable for irrelevant queries

        if expect_relevant:
            total_relevant += 1
            if hit:
                hits += 1
            if best_score is not None:
                relevant_scores.append(best_score)
        else:
            if best_score is not None:
                irrelevant_scores.append(best_score)

        hit_display = ("YES" if hit else "NO") if hit is not None else "n/a"
        expected_display = "relevant" if expect_relevant else "irrelevant"
        score_display = f"{best_score:.4f}" if best_score is not None else "-"
        print(f"{question:<55} {score_display:<12} {hit_display:<6} {expected_display}")

    print()
    print("=" * 100)
    print(f"Precision@{TOP_K} on relevant questions: {hits}/{total_relevant} = {hits/total_relevant:.1%}")
    print()

    if relevant_scores:
        print(f"Relevant-query best scores   -> min={min(relevant_scores):.4f}  max={max(relevant_scores):.4f}  avg={sum(relevant_scores)/len(relevant_scores):.4f}")
    if irrelevant_scores:
        print(f"Irrelevant-query best scores  -> min={min(irrelevant_scores):.4f}  max={max(irrelevant_scores):.4f}  avg={sum(irrelevant_scores)/len(irrelevant_scores):.4f}")

    if relevant_scores and irrelevant_scores:
        gap_low = max(relevant_scores)
        gap_high = min(irrelevant_scores)
        print()
        if gap_low < gap_high:
            suggested = (gap_low + gap_high) / 2
            print(f"Clean separation found. Suggested DISTANCE_THRESHOLD ~= {suggested:.4f}")
        else:
            print(f"WARNING: relevant and irrelevant score ranges OVERLAP "
                  f"(relevant max={gap_low:.4f}, irrelevant min={gap_high:.4f}).")
            print("No single threshold will perfectly separate them with this eval set/model.")
            print("Consider: more/better eval questions, a reranker, or a larger embedding model.")


if __name__ == "__main__":
    run_eval()