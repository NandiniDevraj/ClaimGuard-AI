from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from app.pipelines.vector_store import VectorStore
from app.utils.config import config
from app.utils.logger import get_logger

logger = get_logger(__name__)

class PolicyAgent:
    """
    Reads and reasons over insurance policy documents.
    Finds relevant clauses and determines coverage criteria.
    """

    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.llm = ChatOpenAI(
            model=config.OPENAI_MODEL,
            api_key=config.OPENAI_API_KEY,
            temperature=0
        )
        self.prompt = ChatPromptTemplate.from_template("""
You are an expert insurance policy analyst with deep knowledge of 
US healthcare coverage rules and prior authorization requirements.

Your job is to analyze insurance policy clauses and determine 
the exact requirements for a given medical procedure.

RELEVANT POLICY CLAUSES:
{policy_context}

PROCEDURE BEING REQUESTED:
{procedure}

Analyze the policy clauses and provide:
1. COVERAGE STATUS: Is this procedure covered? (Yes/No/Conditional)
2. REQUIREMENTS: List every requirement that must be met
3. REQUIRED DOCUMENTATION: List every document needed
4. CPT CODES: Which CPT codes are covered for this procedure
5. POLICY CITATIONS: Quote the exact policy language supporting each requirement

Be specific, thorough, and cite exact policy language.
If information is missing from the policy, explicitly state what is unclear.

Response format:
COVERAGE STATUS: [Yes/No/Conditional]
REQUIREMENTS:
- [requirement 1]
- [requirement 2]
REQUIRED DOCUMENTATION:
- [document 1]
- [document 2]
CPT CODES: [list]
POLICY CITATIONS:
- "[exact quote]" - supports [requirement]
""")

    def analyze(self, procedure: str, additional_context: str = "") -> dict:
        """
        Analyze insurance policy for a given procedure.
        Returns structured coverage analysis.
        """
        logger.info(f"PolicyAgent analyzing: {procedure}")

        # Retrieve relevant policy clauses
        query = f"{procedure} coverage requirements prior authorization"
        policy_chunks = self.vector_store.query_policies(query)

        if not policy_chunks:
            logger.warning("No policy documents found in vector store")
            return {
                "status": "error",
                "message": "No policy documents found. Please upload an insurance policy first.",
                "procedure": procedure,
                "policy_context": "",
                "analysis": None
            }

        # Combine retrieved chunks
        policy_context = "\n\n".join([
            f"[Clause {i+1}]:\n{chunk['text']}"
            for i, chunk in enumerate(policy_chunks)
        ])

        # Run LLM analysis
        chain = self.prompt | self.llm
        response = chain.invoke({
            "policy_context": policy_context,
            "procedure": procedure
        })

        logger.info("PolicyAgent analysis complete")

        return {
            "status": "success",
            "procedure": procedure,
            "policy_context": policy_context,
            "analysis": response.content,
            "chunks_used": len(policy_chunks)
        }