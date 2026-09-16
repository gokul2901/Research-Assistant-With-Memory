"""
LangGraph Supervisor Agent.
The entry point for all chat queries — classifies intent and routes
to the appropriate specialized agent (RAG Agent or General Knowledge).
"""

from typing import TypedDict, Optional, List, Dict, Any
from langgraph.graph import StateGraph, END

from src.agents.supervisor.router import IntentClassifier, QueryIntent
from src.agents.rag_agent.agent import RAGAgent
from src.agents.llm.provider import MultiLLMRouter, LLMResponse
from src.rag.rag_pipeline import RAGPipeline, RAGResult
from src.schemas.chat import CitationItem, SourceMetadataRef
from src.utils.logger import logger


# =============================================================================
# State Schema
# =============================================================================

class SupervisorState(TypedDict, total=False):
    """State passed through the LangGraph supervisor workflow."""
    # Input
    question: str
    top_k: int
    similarity_threshold: float
    source_filters: Optional[List[str]]
    model_override: Optional[str]

    # Routing
    intent: str

    # Output
    answer: str
    citations: List[CitationItem]
    sources: List[SourceMetadataRef]
    model_used: str
    is_grounded: bool
    retrieved_chunks_count: int
    execution_time_ms: float


# =============================================================================
# Supervisor Agent (Compiled Graph)
# =============================================================================

class SupervisorAgent:
    """
    High-level interface for the LangGraph Supervisor.
    Encapsulates graph construction and provides a clean async invoke API.
    """

    def __init__(
        self,
        rag_pipeline: Optional[RAGPipeline] = None,
        llm_router: Optional[MultiLLMRouter] = None,
        intent_classifier: Optional[IntentClassifier] = None,
    ):
        self.rag_pipeline = rag_pipeline or RAGPipeline()
        self.llm_router = llm_router or MultiLLMRouter()
        self.intent_classifier = intent_classifier or IntentClassifier(self.llm_router)
        self.rag_agent = RAGAgent(
            rag_pipeline=self.rag_pipeline,
            llm_router=self.llm_router,
        )

        # Build and compile the graph
        self._graph = self._build_graph()

    def _build_graph(self) -> Any:
        """
        Construct the LangGraph supervisor workflow:

        [START] → [classify_intent] → {
            "rag_query"  → [rag_agent]     → [END]
            "general"    → [general_agent] → [END]
        }
        """
        graph = StateGraph(SupervisorState)

        # Register nodes
        graph.add_node("classify_intent", self._classify_intent_node)
        graph.add_node("rag_agent", self._rag_agent_node)
        graph.add_node("general_agent", self._general_agent_node)

        # Set entry point
        graph.set_entry_point("classify_intent")

        # Conditional routing based on intent
        graph.add_conditional_edges(
            "classify_intent",
            self._route_by_intent,
            {
                "rag_query": "rag_agent",
                "general": "general_agent",
            },
        )

        # Terminal edges
        graph.add_edge("rag_agent", END)
        graph.add_edge("general_agent", END)

        return graph.compile()

    # =========================================================================
    # Graph Nodes
    # =========================================================================

    async def _classify_intent_node(self, state: SupervisorState) -> dict:
        """Node: Classify the user's query intent."""
        question = state["question"]
        intent = await self.intent_classifier.classify(question)
        logger.info(f"[Supervisor] Intent classified: {intent.value} for '{question[:60]}'")
        return {"intent": intent.value}

    def _route_by_intent(self, state: SupervisorState) -> str:
        """Conditional edge: route to the appropriate agent based on classified intent."""
        return state.get("intent", "rag_query")

    async def _rag_agent_node(self, state: SupervisorState) -> dict:
        """Node: Invoke the RAG Agent for knowledge-grounded answers."""
        return await self.rag_agent.invoke(state)

    async def _general_agent_node(self, state: SupervisorState) -> dict:
        """Node: Generate a general knowledge response (no RAG retrieval)."""
        import time
        start_time = time.perf_counter()

        question = state["question"]
        model_override = state.get("model_override")

        logger.info(f"[GeneralAgent] Generating general knowledge response for '{question[:60]}'")

        llm_res: LLMResponse = await self.llm_router.generate_general_response(
            question=question,
            model_override=model_override,
        )

        exec_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return {
            "answer": llm_res.content,
            "citations": [],
            "sources": [],
            "model_used": llm_res.model_used,
            "is_grounded": False,
            "retrieved_chunks_count": 0,
            "execution_time_ms": exec_time_ms,
        }

    # =========================================================================
    # Public API
    # =========================================================================

    async def ainvoke(self, input_state: dict) -> SupervisorState:
        """
        Async invoke the supervisor graph with the given input state.
        Returns the final state with answer, citations, sources, etc.
        """
        result = await self._graph.ainvoke(input_state)
        return result


def build_supervisor_graph(
    rag_pipeline: Optional[RAGPipeline] = None,
    llm_router: Optional[MultiLLMRouter] = None,
) -> SupervisorAgent:
    """Factory function to build and return a configured SupervisorAgent."""
    return SupervisorAgent(
        rag_pipeline=rag_pipeline,
        llm_router=llm_router,
    )
