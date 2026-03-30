from app.pipelines.document_parser import DocumentParser
from app.pipelines.vector_store import VectorStore
from app.utils.logger import get_logger

logger = get_logger("pipeline_test")

def test_pii_scrubber():
    print("\n--- Testing PII Scrubber ---")
    from app.pipelines.pii_scrubber import PIIScrubber
    scrubber = PIIScrubber()
    
    test_text = """
    Patient: John Doe
    SSN: 123-45-6789
    Phone: 555-867-5309
    The patient requires spinal fusion surgery.
    Insurance policy requires 6 weeks of physical therapy.
    Current therapy duration: 4 weeks completed.
    """
    
    result = scrubber.scrub(test_text)
    print(f"Original: {test_text[:100]}...")
    print(f"Scrubbed: {result['scrubbed_text'][:100]}...")
    print(f"Entities found: {result['entities_found']}")
    print("✅ PII Scrubber working")

def test_text_parsing():
    print("\n--- Testing Document Parser ---")
    parser = DocumentParser()
    
    sample_clinical_note = """
    Patient: Jane Smith, DOB: 01/15/1985
    Referring Physician: Dr. Robert Johnson
    
    Chief Complaint: Lower back pain radiating to left leg.
    
    Assessment: Patient presents with lumbar disc herniation at L4-L5.
    Conservative treatment has been attempted including:
    - Physical therapy: 4 weeks completed (6 weeks required by policy)
    - NSAIDs: 3 months
    - Epidural steroid injection: 1 administered
    
    Recommendation: Surgical intervention - Spinal Fusion L4-L5
    CPT Code: 22612
    ICD-10: M51.16
    
    Prior Authorization Required: Yes
    Estimated Cost: $45,000
    """
    
    result = parser.parse_text(
        sample_clinical_note,
        "test_clinical_note"
    )
    print(f"Chunks created: {result['total_chunks']}")
    print(f"PII found: {result['pii_entities_found']}")
    print(f"First chunk preview: {result['chunks'][0]['text'][:100]}...")
    print("✅ Document Parser working")
    return result

def test_vector_store(parsed_doc):
    print("\n--- Testing Vector Store ---")
    store = VectorStore()
    
    # Store sample policy text
    sample_policy = """
    Spinal Fusion Surgery Coverage Policy
    
    Medical Necessity Criteria:
    Prior authorization is required for all spinal fusion procedures.
    
    The following criteria must be met:
    1. Patient must complete minimum 6 weeks of physical therapy
    2. Conservative treatment must be documented for minimum 3 months
    3. MRI or CT scan required within 90 days of surgery request
    4. Two specialist opinions required for fusion at multiple levels
    
    CPT Codes Covered: 22612, 22630, 22633
    ICD-10 Codes: M51.16, M51.17, M47.816
    
    Documentation Required:
    - Physical therapy progress notes
    - Imaging reports
    - Specialist consultation notes
    - Failed conservative treatment documentation
    """
    
    from app.pipelines.document_parser import DocumentParser
    parser = DocumentParser()
    policy_doc = parser.parse_text(sample_policy, "sample_policy")
    
    # Store policy
    store.add_policy_document(policy_doc)
    
    # Store clinical note
    store.add_clinical_note(parsed_doc)
    
    # Query
    query = "What are the physical therapy requirements for spinal fusion?"
    results = store.query_policies(query)
    
    print(f"Stats: {store.get_collection_stats()}")
    print(f"Query: {query}")
    print(f"Top result: {results[0]['text'][:150]}...")
    print("✅ Vector Store working")

if __name__ == "__main__":
    print("\n🔍 Testing full pipeline...\n")
    test_pii_scrubber()
    parsed = test_text_parsing()
    test_vector_store(parsed)
    print("\n🚀 Pipeline ready. Day 1 complete!\n")