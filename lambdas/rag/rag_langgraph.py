"""
rag_langgraph.py — LangGraph-orchestrated RAG pipeline for mocktailverse
Wraps the existing retrieve → generate steps as a typed StateGraph.

Graph: START → retrieve_cocktails → generate_answer → END

Usage:
    from rag_langgraph import build_rag_graph
    graph = build_rag_graph()
    result = graph.invoke({"question": "What cocktail has mint?", "k": 3})
    print(result["answer"])
"""

import json
import time
from typing import TypedDict, List, Dict, Any

from langgraph.graph import StateGraph, START, END


# --- State schema ---
class RAGState(TypedDict):
    question: str
    k: int
    context_docs: List[Dict[str, Any]]
    context_str: str
    answer: str


# --- Node: retrieve cocktails (calls existing handler logic) ---
def retrieve_cocktails(state: RAGState) -> RAGState:
    """
    Retrieve relevant cocktails via search Lambda (or mock).
    Maps to: handler.retrieve_context + handler.build_context
    """
    import os
    import importlib.util
    from unittest.mock import MagicMock, patch

    # Load handler — use mock if AWS creds not available
    handler_path = os.path.join(os.path.dirname(__file__), "handler.py")
    spec = importlib.util.spec_from_file_location("handler", handler_path)

    try:
        import boto3
        boto3.client("sts").get_caller_identity()  # check real creds
        handler = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(handler)
    except Exception:
        # No AWS creds — use mock search results for local dev
        mock_docs = [
            {"name": "Mojito", "relevance_score": 0.92, "category": "Cocktail",
             "alcoholic": "Alcoholic", "description": "Classic rum cocktail with mint",
             "ingredients": [{"name": "rum", "measure": "2 oz"}, {"name": "mint", "measure": "10 leaves"},
                             {"name": "lime juice", "measure": "1 oz"}],
             "instructions": "Muddle mint. Add rum and lime. Top with soda water.",
             "flavor_profile": ["refreshing", "citrus", "herbal"],
             "occasions": ["summer", "casual"], "difficulty": "Easy", "prep_time_minutes": 5},
        ]
        return {**state, "context_docs": mock_docs,
                "context_str": f"Cocktail 1: {mock_docs[0]['name']}\n{mock_docs[0]['description']}"}

    context_docs = handler.retrieve_context(state["question"], k=state["k"])
    context_str = handler.build_context(context_docs)
    return {**state, "context_docs": context_docs, "context_str": context_str}


# --- Node: generate answer ---
def generate_answer(state: RAGState) -> RAGState:
    """
    Generate answer from retrieved context via Bedrock (or mock).
    Maps to: handler.generate_answer
    """
    import os
    import importlib.util

    if not state.get("context_docs"):
        return {**state, "answer": "No relevant cocktails found for your query."}

    handler_path = os.path.join(os.path.dirname(__file__), "handler.py")
    spec = importlib.util.spec_from_file_location("handler", handler_path)

    try:
        import boto3
        boto3.client("sts").get_caller_identity()
        handler = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(handler)
        answer = handler.generate_answer(state["question"], state["context_str"])
    except Exception:
        # No AWS creds — mock response for local dev
        doc = state["context_docs"][0]
        answer = (f"Based on your request, I recommend a {doc['name']}. "
                  f"{doc.get('description', '')} "
                  f"It pairs well with: {', '.join(doc.get('flavor_profile', []))}.")

    return {**state, "answer": answer}


# --- Build graph ---
def build_rag_graph() -> StateGraph:
    """
    Returns a compiled LangGraph StateGraph for the mocktailverse RAG pipeline.
    Flow: START → retrieve_cocktails → generate_answer → END
    """
    graph = StateGraph(RAGState)

    graph.add_node("retrieve_cocktails", retrieve_cocktails)
    graph.add_node("generate_answer", generate_answer)

    graph.add_edge(START, "retrieve_cocktails")
    graph.add_edge("retrieve_cocktails", "generate_answer")
    graph.add_edge("generate_answer", END)

    return graph.compile()


# --- Local smoke test ---
if __name__ == "__main__":
    print("Building RAG graph...")
    rag = build_rag_graph()

    test_questions = [
        "What cocktail should I make with rum?",
        "Recommend something refreshing for summer",
    ]

    for q in test_questions:
        print(f"\nQ: {q}")
        t0 = time.perf_counter()
        result = rag.invoke({"question": q, "k": 3})
        elapsed = (time.perf_counter() - t0) * 1000
        print(f"A: {result['answer'][:200]}")
        print(f"   Sources: {[d['name'] for d in result.get('context_docs', [])]}")
        print(f"   Latency: {elapsed:.0f}ms")

    print("\nGraph nodes:", list(rag.get_graph().nodes))
    print("LangGraph RAG pipeline: OK")
