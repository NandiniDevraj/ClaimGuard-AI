from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from app.utils.config import config
from app.utils.logger import get_logger

logger = get_logger(__name__)

class RecommendationAgent:
    """
    Generates specific, actionable recommendations
    to maximize authorization approval likelihood.
    Tells doctors and billing staff exactly what to do.
    """

    def __init__(self):
        self.llm = ChatOpenAI(
            model=config.OPENAI_MODEL,
            api_key=config.OPENAI_API_KEY,
            temperature=0.1
        )
        self.prompt = ChatPromptTemplate.from_template("""
You are a prior authorization consultant who helps healthcare providers
get approvals for their patients. You know exactly what insurance
companies need to see to approve claims.

Your job is to give specific, actionable recommendations to fix
documentation gaps and maximize approval chances.

GAP ANALYSIS:
{gap_analysis}

APPROVAL LIKELIHOOD: {approval_likelihood}%

Generate recommendations for THREE audiences:

FOR THE PHYSICIAN:
- Specific clinical notes to add or update
- Additional documentation to order
- Exact language to use in medical necessity statements

FOR BILLING STAFF:
- Administrative steps to take
- Forms to complete or update
- Timeline and priority of actions

FOR THE PATIENT:
- What they need to do (if anything)
- What to expect in the process
- Estimated timeline

Also provide:
PRIORITY ACTIONS: Top 3 things to do TODAY to prevent denial
ESTIMATED TIMELINE: How long to gather missing documentation
APPROVAL FORECAST: Likelihood after implementing recommendations

Response format:
FOR THE PHYSICIAN:
- [specific action with exact detail]

FOR BILLING STAFF:
- [specific action with exact detail]

FOR THE PATIENT:
- [patient-friendly explanation]

PRIORITY ACTIONS (Do Today):
1. [most critical action]
2. [second most critical]
3. [third most critical]

ESTIMATED TIMELINE: [X days/weeks]
APPROVAL FORECAST: [X%] after implementing recommendations
""")

    def generate(
        self,
        gap_analysis: str,
        approval_likelihood: int
    ) -> dict:
        """
        Generate actionable recommendations based on gap analysis.
        """
        logger.info(
            f"RecommendationAgent generating recommendations. "
            f"Current likelihood: {approval_likelihood}%"
        )

        chain = self.prompt | self.llm
        response = chain.invoke({
            "gap_analysis": gap_analysis,
            "approval_likelihood": approval_likelihood
        })

        # Extract forecast likelihood
        forecast = self._extract_forecast(response.content)

        logger.info(
            f"Recommendations generated. "
            f"Forecast after fixes: {forecast}%"
        )

        return {
            "status": "success",
            "recommendations": response.content,
            "approval_likelihood_before": approval_likelihood,
            "approval_likelihood_after": forecast
        }

    def _extract_forecast(self, recommendations_text: str) -> int:
        """Extract the forecast approval likelihood."""
        try:
            lines = recommendations_text.split("\n")
            for line in lines:
                if "APPROVAL FORECAST:" in line:
                    parts = line.split(":")
                    if len(parts) > 1:
                        num = "".join(
                            filter(str.isdigit, parts[1].strip())
                        )
                        if num:
                            return min(100, max(0, int(num)))
        except Exception:
            pass
        return 75  # Default forecast