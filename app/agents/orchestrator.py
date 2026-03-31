from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from app.agents.policy_agent import PolicyAgent
from app.agents.clinical_agent import ClinicalAgent
from app.agents.gap_detector import GapDetectorAgent
from app.agents.recommendation import RecommendationAgent
from app.pipelines.vector_store import VectorStore
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Define the state that flows through the graph
class AuthState(TypedDict):
    procedure: str
    policy_analysis: Optional[str]
    clinical_analysis: Optional[str]
    gap_analysis: Optional[str]
    approval_likelihood: Optional[int]
    recommendations: Optional[str]
    approval_likelihood_after: Optional[int]
    error: Optional[str]
    completed_steps: list

class AuthOrchestrator:
    """
    LangGraph orchestrator that coordinates all agents.
    Manages the flow: Policy → Clinical → Gaps → Recommendations
    """

    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.policy_agent = PolicyAgent(vector_store)
        self.clinical_agent = ClinicalAgent(vector_store)
        self.gap_detector = GapDetectorAgent()
        self.recommendation_agent = RecommendationAgent()
        self.graph = self._build_graph()
        logger.info("AuthOrchestrator initialized with LangGraph")

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph agent workflow."""
        workflow = StateGraph(AuthState)

        # Add all agent nodes
        workflow.add_node("analyze_policy", self._analyze_policy)
        workflow.add_node("analyze_clinical", self._analyze_clinical)
        workflow.add_node("detect_gaps", self._detect_gaps)
        workflow.add_node("generate_recommendations", self._generate_recommendations)

        # Define the flow
        workflow.set_entry_point("analyze_policy")
        workflow.add_edge("analyze_policy", "analyze_clinical")
        workflow.add_edge("analyze_clinical", "detect_gaps")
        workflow.add_edge("detect_gaps", "generate_recommendations")
        workflow.add_edge("generate_recommendations", END)

        return workflow.compile()

    def _analyze_policy(self, state: AuthState) -> AuthState:
        """Node 1: Analyze insurance policy."""
        logger.info("Step 1/4: Analyzing insurance policy...")
        try:
            result = self.policy_agent.analyze(state["procedure"])
            if result["status"] == "success":
                state["policy_analysis"] = result["analysis"]
                state["completed_steps"].append("policy_analysis")
                logger.info("✓ Policy analysis complete")
            else:
                state["error"] = result["message"]
        except Exception as e:
            logger.error(f"Policy analysis failed: {e}")
            state["error"] = str(e)
        return state

    def _analyze_clinical(self, state: AuthState) -> AuthState:
        """Node 2: Analyze clinical documentation."""
        logger.info("Step 2/4: Analyzing clinical documentation...")
        try:
            result = self.clinical_agent.analyze(state["procedure"])
            if result["status"] == "success":
                state["clinical_analysis"] = result["analysis"]
                state["completed_steps"].append("clinical_analysis")
                logger.info("✓ Clinical analysis complete")
            else:
                state["error"] = result["message"]
        except Exception as e:
            logger.error(f"Clinical analysis failed: {e}")
            state["error"] = str(e)
        return state

    def _detect_gaps(self, state: AuthState) -> AuthState:
        """Node 3: Detect gaps between policy and clinical docs."""
        logger.info("Step 3/4: Detecting documentation gaps...")
        try:
            if not state.get("policy_analysis") or \
               not state.get("clinical_analysis"):
                state["error"] = "Missing policy or clinical analysis"
                return state

            result = self.gap_detector.analyze(
                policy_analysis=state["policy_analysis"],
                clinical_analysis=state["clinical_analysis"]
            )
            state["gap_analysis"] = result["analysis"]
            state["approval_likelihood"] = result["approval_likelihood"]
            state["completed_steps"].append("gap_detection")
            logger.info(
                f"✓ Gap detection complete. "
                f"Approval likelihood: {result['approval_likelihood']}%"
            )
        except Exception as e:
            logger.error(f"Gap detection failed: {e}")
            state["error"] = str(e)
        return state

    def _generate_recommendations(self, state: AuthState) -> AuthState:
        """Node 4: Generate actionable recommendations."""
        logger.info("Step 4/4: Generating recommendations...")
        try:
            if not state.get("gap_analysis"):
                state["error"] = "Missing gap analysis"
                return state

            result = self.recommendation_agent.generate(
                gap_analysis=state["gap_analysis"],
                approval_likelihood=state.get("approval_likelihood", 50)
            )
            state["recommendations"] = result["recommendations"]
            state["approval_likelihood_after"] = \
                result["approval_likelihood_after"]
            state["completed_steps"].append("recommendations")
            logger.info("✓ Recommendations generated")
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            state["error"] = str(e)
        return state

    def run(self, procedure: str) -> dict:
        """
        Run the full authorization analysis pipeline.
        Returns complete analysis with recommendations.
        """
        logger.info(f"Starting authorization analysis for: {procedure}")

        initial_state = AuthState(
            procedure=procedure,
            policy_analysis=None,
            clinical_analysis=None,
            gap_analysis=None,
            approval_likelihood=None,
            recommendations=None,
            approval_likelihood_after=None,
            error=None,
            completed_steps=[]
        )

        final_state = self.graph.invoke(initial_state)

        if final_state.get("error"):
            logger.error(f"Pipeline error: {final_state['error']}")
            return {
                "status": "error",
                "error": final_state["error"],
                "completed_steps": final_state["completed_steps"]
            }

        logger.info(
            f"Analysis complete. "
            f"Steps completed: {final_state['completed_steps']}"
        )

        return {
            "status": "success",
            "procedure": procedure,
            "policy_analysis": final_state["policy_analysis"],
            "clinical_analysis": final_state["clinical_analysis"],
            "gap_analysis": final_state["gap_analysis"],
            "approval_likelihood": final_state["approval_likelihood"],
            "recommendations": final_state["recommendations"],
            "approval_likelihood_after": final_state["approval_likelihood_after"],
            "completed_steps": final_state["completed_steps"]
        }