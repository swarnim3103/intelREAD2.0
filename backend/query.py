import os
from pathlib import Path

from dotenv import load_dotenv
import google.generativeai as genai
from vectorstore import get_vectorstore

load_dotenv(Path(__file__).resolve().parent / ".env")


gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)


TOP_K = 4
# Chroma's default distance is cosine distance (lower = more similar).
# Anything above this threshold is treated as "not relevant enough" -> refuse to guess.
DISTANCE_THRESHOLD = 2.2

STRICT_GROUNDING_PROMPT = """You are a document assistant. Answer the question using ONLY the information in the CONTEXT below.

Rules:
- If the answer is not contained in the CONTEXT, respond exactly with: "I couldn't find this in the document."
- Do not use outside knowledge, even if you know the answer from elsewhere.
- Do not guess or make up details not present in the CONTEXT.
- Keep the answer concise and cite which source chunk(s) you used if possible.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:"""


HYBRID_PROMPT = """You are a document assistant. Answer the question primarily using the CONTEXT below.
You are allowed to add relevant outside/general knowledge if it helps answer the question more completely.

Rules:
- Structure your answer in two clearly labeled parts:
  1) "From the document:" — only what is directly supported by the CONTEXT. If nothing relevant is in the CONTEXT, write "Nothing relevant found in the document."
  2) "Additional context (outside the document):" — any extra general knowledge you're adding. If you have nothing to add, write "None."
- Never blend the two together — keep them in separate labeled sections so the user can tell what is sourced vs. not.
- Do not present outside knowledge as if it came from the document.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:"""


def run_llm(prompt: str) -> str:
    """Send prompt to Gemini model and return generated text"""
    try:
        if not gemini_api_key:
            return "Error: GEMINI_API_KEY not found in environment variables"

        model = genai.GenerativeModel('models/gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"Error calling Gemini API: {str(e)}"


def get_qa_chain():
    vectorstore = get_vectorstore()

    def qa_function(query: str, allow_outside_knowledge: bool = False):
        # similarity_search_with_score gives us (doc, distance) pairs,
        # which we need to decide whether retrieval was actually good enough to answer from.
        try:
            results = vectorstore.similarity_search_with_score(query, k=TOP_K)
        except Exception as e:
            return {
                "answer": f"Error during retrieval: {str(e)}",
                "sources": [],
                "mode": "hybrid" if allow_outside_knowledge else "strict",
            }
        mode = "hybrid" if allow_outside_knowledge else "strict"

     
        print(f"[query] Query: {query!r}")
        for doc, score in results:
            print(f"[query]   score={score:.4f} | source={doc.metadata.get('source')} | text={doc.page_content[:80]!r}")
        if not results:
            if allow_outside_knowledge:
                prompt = HYBRID_PROMPT.format(context="(no document content available)", question=query)
                answer = run_llm(prompt)
                return {"answer": answer, "sources": [], "mode": mode}
            return {
                "answer": "I couldn't find this in the document.",
                "sources": [],
                "mode": mode,
            }
        relevant = [(doc, score) for doc, score in results if score <= DISTANCE_THRESHOLD]

        if not relevant:
            if allow_outside_knowledge:
                prompt = HYBRID_PROMPT.format(
                    context="(no sufficiently relevant document content found)",
                    question=query,
                )
                answer = run_llm(prompt)
                return {
                    "answer": answer,
                    "sources": [],
                    "mode": mode,
                    "debug_best_score": min(score for _, score in results),
                }
            return {
                "answer": "I couldn't find this in the document.",
                "sources": [],
                "mode": mode,
                "debug_best_score": min(score for _, score in results),
            }

        context = "\n\n".join(
            f"[{doc.metadata.get('source', 'unknown')} | chunk {doc.metadata.get('chunk_index', '?')}]\n{doc.page_content}"
            for doc, _ in relevant
        )

        template = HYBRID_PROMPT if allow_outside_knowledge else STRICT_GROUNDING_PROMPT
        prompt = template.format(context=context, question=query)
        answer = run_llm(prompt)

        sources = [
            {
                "source": doc.metadata.get("source", "unknown"),
                "page": doc.metadata.get("page"),
                "chunk_index": doc.metadata.get("chunk_index"),
                "score": score,
            }
            for doc, score in relevant
        ]

        return {"answer": answer, "sources": sources, "mode": mode}

    return qa_function