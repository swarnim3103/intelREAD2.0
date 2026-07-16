"""
Chunking strategy comparison for IntellRead.

Purpose:
- Test multiple chunk_size/overlap configurations against the SAME eval
  questions, using temporary in-memory Chroma collections, so we can pick
  a chunking strategy backed by a number instead of a guess.
- Does NOT touch your real persisted vectorstore (uses ephemeral collections).

Usage:
    python compare_chunking.py --pdf path/to/Edge_detection.pdf

Requires: PyPDF2, langchain_text_splitters, langchain_community, langchain_chroma
"""

import argparse
import uuid
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# ---------------------------------------------------------------------------
# Same eval set as eval_retrieval.py, so results are directly comparable.
# Keep this in sync manually if you update the eval set there.
# ---------------------------------------------------------------------------
EVAL_SET = [
    {"question": "What are the four types of edges in image processing?", "expect_substring": "Ramp type", "expect_relevant": True},
    {"question": "What mask does the Prewitt operator use to detect vertical edges?", "expect_substring": "-1 0 1", "expect_relevant": True},
    {"question": "How is the Sobel operator different from the Prewitt operator?", "expect_substring": "coefficients of masks are not fixed", "expect_relevant": True},
    {"question": "How many orientations does the Robinson compass mask have?", "expect_substring": "eight orientations", "expect_relevant": True},
    {"question": "Who is the Kirsch operator named after?", "expect_substring": "Russell A. Kirsch", "expect_relevant": True},
    {"question": "What is the difference between Laplacian operator and Prewitt, Sobel, Robinson, Kirsch?", "expect_substring": "second order derivative", "expect_relevant": True},
    {"question": "What do you do after applying the positive Laplacian operator to get a sharpened image?", "expect_substring": "subtract the resultant", "expect_relevant": True},
    {"question": "What are the two most popular line detection techniques?", "expect_substring": "Hough transform", "expect_relevant": True},
    {"question": "In the Hough transform example, what are the coordinates given to prove collinearity?", "expect_substring": "(1,1)", "expect_relevant": True},
    {"question": "What is the purpose of edge detection in image processing?", "expect_substring": "boundaries of", "expect_relevant": True},
    {"question": "What is the capital of France?", "expect_substring": None, "expect_relevant": False},
    {"question": "Who won the cricket world cup in 2011?", "expect_substring": None, "expect_relevant": False},
    {"question": "What is the plot of the movie Inception?", "expect_substring": None, "expect_relevant": False},
    {"question": "How do you make a chocolate cake?", "expect_substring": None, "expect_relevant": False},
    {"question": "What is the population of Japan?", "expect_substring": None, "expect_relevant": False},
]

# Chunking configs to compare: (chunk_size, chunk_overlap, label)
CONFIGS = [
    (400, 50, "small_400_50"),
    (800, 100, "current_800_100"),
    (1200, 150, "large_1200_150"),
]

TOP_K = 4


def extract_pages(pdf_path):
    reader = PdfReader(pdf_path)
    pages = []
    for page in reader.pages:
        try:
            pages.append(page.extract_text() or "")
        except Exception:
            pages.append("")
    return pages


def build_ephemeral_store(pages, chunk_size, chunk_overlap, embeddings):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    chunks = []
    metadatas = []
    for page_num, page_text in enumerate(pages, start=1):
        if not page_text.strip():
            continue
        page_chunks = splitter.split_text(page_text)
        for chunk in page_chunks:
            chunks.append(chunk)
            metadatas.append({"page": page_num})

    # In-memory, throwaway collection per config - no persist_directory,
    # unique collection name to avoid any collision.
    collection_name = f"eval_{uuid.uuid4().hex[:8]}"
    vs = Chroma(collection_name=collection_name, embedding_function=embeddings)
    vs.add_texts(chunks, metadatas=metadatas)
    return vs, len(chunks)


def run_eval_against_store(vs):
    relevant_scores = []
    irrelevant_scores = []
    hits = 0
    total_relevant = 0

    for case in EVAL_SET:
        results = vs.similarity_search_with_score(case["question"], k=TOP_K)
        if not results:
            best_score = None
            hit = False
        else:
            best_score = min(score for _, score in results)
            if case["expect_relevant"] and case["expect_substring"]:
                hit = any(case["expect_substring"].lower() in doc.page_content.lower() for doc, _ in results)
            else:
                hit = None

        if case["expect_relevant"]:
            total_relevant += 1
            if hit:
                hits += 1
            if best_score is not None:
                relevant_scores.append(best_score)
        else:
            if best_score is not None:
                irrelevant_scores.append(best_score)

    precision = hits / total_relevant if total_relevant else 0
    gap = None
    if relevant_scores and irrelevant_scores:
        gap = min(irrelevant_scores) - max(relevant_scores)  # positive = clean separation

    return {
        "precision": precision,
        "hits": hits,
        "total_relevant": total_relevant,
        "relevant_min": min(relevant_scores) if relevant_scores else None,
        "relevant_max": max(relevant_scores) if relevant_scores else None,
        "irrelevant_min": min(irrelevant_scores) if irrelevant_scores else None,
        "irrelevant_max": max(irrelevant_scores) if irrelevant_scores else None,
        "gap": gap,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", required=True, help="Path to the PDF to test chunking configs against")
    args = parser.parse_args()

    print(f"Extracting pages from {args.pdf}...")
    pages = extract_pages(args.pdf)
    print(f"Extracted {len(pages)} pages.\n")

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    print(f"{'CONFIG':<20} {'#CHUNKS':<10} {'PRECISION@4':<14} {'REL_RANGE':<18} {'IRREL_RANGE':<18} {'GAP':<10}")
    print("-" * 100)

    results_summary = []

    for chunk_size, chunk_overlap, label in CONFIGS:
        vs, num_chunks = build_ephemeral_store(pages, chunk_size, chunk_overlap, embeddings)
        result = run_eval_against_store(vs)
        results_summary.append((label, num_chunks, result))

        rel_range = f"{result['relevant_min']:.3f}-{result['relevant_max']:.3f}" if result['relevant_min'] is not None else "n/a"
        irrel_range = f"{result['irrelevant_min']:.3f}-{result['irrelevant_max']:.3f}" if result['irrelevant_min'] is not None else "n/a"
        gap_display = f"{result['gap']:.3f}" if result['gap'] is not None else "n/a"

        print(f"{label:<20} {num_chunks:<10} {result['hits']}/{result['total_relevant']} ({result['precision']:.0%}){'':<3} {rel_range:<18} {irrel_range:<18} {gap_display:<10}")

    print()
    print("=" * 100)
    print("Interpretation:")
    print("- Higher precision@4 = better retrieval accuracy for this config.")
    print("- Larger GAP = cleaner separation between relevant/irrelevant scores")
    print("  (makes threshold-based 'I don't know' detection more reliable).")
    print("- If precision ties, prefer the config with the larger gap and/or fewer chunks")
    print("  (fewer chunks = less storage/embedding cost for the same accuracy).")


if __name__ == "__main__":
    main()