from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from app.utils.logger import get_logger

logger = get_logger(__name__)

class PIIScrubber:
    def __init__(self):
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        
        # Define what to replace PII with
        self.operators = {
            "PERSON": OperatorConfig(
                "replace", {"new_value": "[PATIENT_NAME]"}
            ),
            "US_SSN": OperatorConfig(
                "replace", {"new_value": "[SSN_REDACTED]"}
            ),
            "US_DRIVER_LICENSE": OperatorConfig(
                "replace", {"new_value": "[LICENSE_REDACTED]"}
            ),
            "PHONE_NUMBER": OperatorConfig(
                "replace", {"new_value": "[PHONE_REDACTED]"}
            ),
            "EMAIL_ADDRESS": OperatorConfig(
                "replace", {"new_value": "[EMAIL_REDACTED]"}
            ),
            "US_BANK_NUMBER": OperatorConfig(
                "replace", {"new_value": "[BANK_REDACTED]"}
            ),
            "CREDIT_CARD": OperatorConfig(
                "replace", {"new_value": "[CARD_REDACTED]"}
            ),
            "DATE_TIME": OperatorConfig(
                "replace", {"new_value": "[DATE_REDACTED]"}
            ),
            "LOCATION": OperatorConfig(
                "replace", {"new_value": "[LOCATION_REDACTED]"}
            ),
            "MEDICAL_LICENSE": OperatorConfig(
                "replace", {"new_value": "[LICENSE_REDACTED]"}
            ),
        }

    def scrub(self, text: str) -> dict:
        """
        Scrub PII from text.
        Returns dict with scrubbed text and list of found entities.
        """
        if not text or not text.strip():
            return {"scrubbed_text": text, "entities_found": []}

        try:
            # Analyze text for PII
            analysis_results = self.analyzer.analyze(
                text=text,
                language="en",
                entities=list(self.operators.keys())
            )

            # Anonymize detected PII
            anonymized = self.anonymizer.anonymize(
                text=text,
                analyzer_results=analysis_results,
                operators=self.operators
            )

            entities_found = [
                {
                    "type": r.entity_type,
                    "score": round(r.score, 2)
                }
                for r in analysis_results
            ]

            if entities_found:
                logger.info(
                    f"Scrubbed {len(entities_found)} PII entities: "
                    f"{[e['type'] for e in entities_found]}"
                )

            return {
                "scrubbed_text": anonymized.text,
                "entities_found": entities_found
            }

        except Exception as e:
            logger.error(f"PII scrubbing failed: {e}")
            # Return original text if scrubbing fails
            # so pipeline doesn't break
            return {"scrubbed_text": text, "entities_found": []}

    def scrub_text(self, text: str) -> str:
        """Convenience method — returns just the scrubbed text."""
        return self.scrub(text)["scrubbed_text"]