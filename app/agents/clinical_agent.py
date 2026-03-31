from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from app.pipelines.vector_store import VectorStore
from app.utils.config import config
from app.utils.logger import get_logger

logger = get_logger(__name__)

class ClinicalAgent:
    """
    Reads and understands clinical documentation.
    Extracts what has been done, what is documented,
    and what the patient's current status is.
    """

    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.llm = ChatOpenAI(
            model=config.OPENAI_MODEL,
            api_key=config.OPENAI_API_KEY,
            temperature=0
        )
        self.prompt = ChatPromptTemplate.from_template("""
You are an expert clinical documentation analyst with deep knowledge
of US healthcare documentation standards, ICD-10 codes, and CPT codes.

Your job is to extract and summarize all clinically relevant information
from patient records to support a prior authorization request.

CLINICAL DOCUMENTATION:
{clinical_context}

PROCEDURE BEING REQUESTED:
{procedure}

Extract and analyze:
1. DIAGNOSIS: Primary and secondary diagnoses with ICD-10 codes
2. PROCEDURE REQUESTED: CPT code and full description
3. CONSERVATIVE TREATMENTS COMPLETED: What has already been tried
4. TREATMENT DURATION: How long each treatment was administered
5. CLINICAL JUSTIFICATION: Why surgery/procedure is now necessary
6. MISSING INFORMATION: What clinical information is absent or unclear
7. DOCUMENTATION STRENGTH: Rate the documentation (Strong/Moderate/Weak)

Be precise. Use exact durations, dates, and codes where available.
Flag any inconsistencies or gaps in the documentation.

Response format:
DIAGNOSIS: [ICD-10 code] - [description]
PROCEDURE REQUESTED: CPT [code] - [description]
CONSERVATIVE TREATMENTS:
- [treatment]: [duration] - [outcome]
CLINICAL JUSTIFICATION: [summary]
MISSING INFORMATION:
- [missing item 1]
- [missing item 2]
DOCUMENTATION STRENGTH: [Strong/Moderate/Weak]
REASONING: [why you rated it this way]
""")

    def analyze(self, procedure: str) -> dict:
        """
        Analyze clinical documentation for a procedure request.
        Returns structured clinical summary.
        """
        logger.info(f"ClinicalAgent analyzing documentation for: {procedure}")

        # Retrieve relevant clinical chunks
        query = f"{procedure} patient history treatment documentation"
        clinical_chunks = self.vector_store.query_clinical(query)

        if not clinical_chunks:
            logger.warning("No clinical documents found in vector store")
            return {
                "status": "error",
                "message": "No clinical notes found. Please upload patient documentation first.",
                "procedure": procedure,
                "clinical_context": "",
                "analysis": None
            }

        # Combine retrieved chunks
        clinical_context = "\n\n".join([
            f"[Note {i+1}]:\n{chunk['text']}"
            for i, chunk in enumerate(clinical_chunks)
        ])

        # Run LLM analysis
        chain = self.prompt | self.llm
        response = chain.invoke({
            "clinical_context": clinical_context,
            "procedure": procedure
        })

        logger.info("ClinicalAgent analysis complete")

        return {
            "status": "success",
            "procedure": procedure,
            "clinical_context": clinical_context,
            "analysis": response.content,
            "chunks_used": len(clinical_chunks)
        }