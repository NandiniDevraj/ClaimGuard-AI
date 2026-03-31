from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from app.utils.config import config
from app.utils.logger import get_logger

logger = get_logger(__name__)

class GapDetectorAgent:
    """
    Compares policy requirements against clinical documentation.
    Identifies exactly what is missing or insufficient.
    This is the core value of the system.
    """

    def __init__(self):
        self.llm = ChatOpenAI(
            model=config.OPENAI_MODEL,
            api_key=config.OPENAI_API_KEY,
            temperature=0
        )
        self.prompt = ChatPromptTemplate.from_template("""
You are an expert prior authorization specialist who has reviewed
thousands of insurance claims. You know exactly why claims get denied
and what documentation fixes those denials.

Your job is to compare what the insurance policy REQUIRES against
what the clinical documentation SHOWS, and identify every gap.

POLICY REQUIREMENTS ANALYSIS:
{policy_analysis}

CLINICAL DOCUMENTATION ANALYSIS:
{clinical_analysis}

Perform a gap analysis and provide:

1. APPROVAL LIKELIHOOD: Estimate probability of approval (0-100%)
2. CRITICAL GAPS: Issues that will DEFINITELY cause denial
3. MODERATE GAPS: Issues that might cause denial or delay
4. SATISFIED REQUIREMENTS: What is already properly documented
5. DENIAL RISK FACTORS: Specific reasons this could be denied

Be brutally honest. Insurance companies deny claims on technicalities.
Flag every potential issue no matter how small.

Response format:
APPROVAL LIKELIHOOD: [X%]
APPROVAL LIKELIHOOD REASONING: [explanation]

CRITICAL GAPS (will cause denial):
- GAP: [description]
  POLICY REQUIRES: [exact requirement]
  DOCUMENTATION SHOWS: [what is present]
  IMPACT: [why this causes denial]

MODERATE GAPS (may cause delay):
- GAP: [description]
  FIX: [what to add]

SATISFIED REQUIREMENTS:
- [requirement]: ✓ [how it is satisfied]

DENIAL RISK FACTORS:
- [risk factor 1]
- [risk factor 2]
""")

    def analyze(
        self,
        policy_analysis: str,
        clinical_analysis: str
    ) -> dict:
        """
        Compare policy requirements against clinical documentation.
        Returns gap analysis with approval likelihood.
        """
        logger.info("GapDetectorAgent performing gap analysis")

        chain = self.prompt | self.llm
        response = chain.invoke({
            "policy_analysis": policy_analysis,
            "clinical_analysis": clinical_analysis
        })

        # Extract approval likelihood from response
        approval_likelihood = self._extract_likelihood(response.content)

        logger.info(
            f"Gap analysis complete. "
            f"Approval likelihood: {approval_likelihood}%"
        )

        return {
            "status": "success",
            "analysis": response.content,
            "approval_likelihood": approval_likelihood
        }

    def _extract_likelihood(self, analysis_text: str) -> int:
        """Extract the approval likelihood percentage from analysis."""
        try:
            lines = analysis_text.split("\n")
            for line in lines:
                if "APPROVAL LIKELIHOOD:" in line and "REASONING" not in line:
                    # Extract number from line like "APPROVAL LIKELIHOOD: 45%"
                    parts = line.split(":")
                    if len(parts) > 1:
                        num = "".join(
                            filter(str.isdigit, parts[1].strip())
                        )
                        if num:
                            return min(100, max(0, int(num)))
        except Exception:
            pass
        return 50  # Default if extraction fails