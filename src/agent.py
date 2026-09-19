from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        if self.store.get_collection_size() == 0:
            return "Knowledge base is empty."
            
        results = self.store.search(question, top_k=top_k)
        if not results:
            return "No relevant information found to answer the question."
            
        context_parts = []
        for i, res in enumerate(results, 1):
            source = res.get("metadata", {}).get("source", "Unknown")
            context_parts.append(f"[{i}] Source: {source}\n{res['content']}")
            
        context_str = "\n\n".join(context_parts)
        prompt = f"Using the following context, answer the question. Only use the provided context. If the answer is not in the context, say you cannot find it. Cite the chunk number (e.g., [1]) in your answer.\n\nContext:\n{context_str}\n\nQuestion: {question}"
        return self.llm_fn(prompt)
