from app.pipelines.document_parser import DocumentParser
from app.pipelines.vector_store import VectorStore
from app.agents.orchestrator import AuthOrchestrator
from app.utils.logger import get_logger

logger = get_logger("agent_test")

def setup_test_data(vector_store: VectorStore):
    """Load sample policy and clinical note into vector store."""
    parser = DocumentParser()

    sample_policy = """
    Spinal Fusion Surgery Coverage Policy - Section 4.2
    
    Prior Authorization Requirements:
    All spinal fusion procedures (CPT codes 22612, 22630, 22633) 
    require prior authorization before scheduling.
    
    Medical Necessity Criteria - ALL must be met:
    1. Minimum 6 weeks of supervised physical therapy with documented 
       progress notes from a licensed physical therapist
    2. Conservative treatment for minimum 3 months including NSAIDs
    3. MRI or CT imaging within 90 days of authorization request
    4. Documentation of failed conservative management
    5. Two independent specialist opinions for multi-level fusion
    
    Required Documentation:
    - Physical therapy progress notes (all sessions)
    - Imaging reports with radiologist interpretation
    - Prescribing physician's letter of medical necessity
    - Documentation of conservative treatment failure
    - Complete medication history
    
    Exclusions:
    - Fusion performed solely for degenerative disc disease without 
      neurological compromise will not be covered
    """

    sample_clinical = """
    Patient Clinical Summary
    
    Diagnosis: Lumbar disc herniation L4-L5 with radiculopathy
    ICD-10: M51.16, G54.4
    
    Procedure Requested: Spinal Fusion L4-L5
    CPT Code: 22612
    
    Conservative Treatment History:
    - Physical therapy: 4 weeks completed (ongoing)
    - NSAIDs (Ibuprofen 800mg): 2 months
    - Epidural steroid injection: 1 administered 3 weeks ago
    
    Clinical Notes:
    Patient presents with severe lower back pain radiating to left leg.
    Significant functional impairment affecting daily activities.
    Conservative management has provided minimal relief.
    
    Imaging: MRI lumbar spine performed 45 days ago showing
    significant disc herniation with nerve root compression at L4-L5.
    
    Physician Recommendation: Surgical intervention required due to
    progressive neurological symptoms and failed conservative treatment.
    """

    policy_doc = parser.parse_text(sample_policy, "spinal_fusion_policy")
    clinical_doc = parser.parse_text(sample_clinical, "patient_clinical_note")

    vector_store.add_policy_document(policy_doc)
    vector_store.add_clinical_note(clinical_doc)
    print("✅ Test data loaded into vector store")

if __name__ == "__main__":
    print("\n🤖 Testing Multi-Agent System...\n")

    # Initialize
    vector_store = VectorStore()
    setup_test_data(vector_store)

    # Run orchestrator
    orchestrator = AuthOrchestrator(vector_store)
    result = orchestrator.run("Spinal Fusion L4-L5 (CPT 22612)")

    if result["status"] == "success":
        print("\n" + "="*60)
        print("AUTHORIZATION ANALYSIS COMPLETE")
        print("="*60)
        print(f"\nSteps completed: {result['completed_steps']}")
        print(f"\nApproval Likelihood: {result['approval_likelihood']}%")
        print(f"After Fixes: {result['approval_likelihood_after']}%")
        print("\n--- POLICY ANALYSIS ---")
        print(result['policy_analysis'])
        print("\n--- CLINICAL ANALYSIS ---")
        print(result['clinical_analysis'])
        print("\n--- GAP ANALYSIS ---")
        print(result['gap_analysis'])
        print("\n--- RECOMMENDATIONS ---")
        print(result['recommendations'])
        print("\n✅ Multi-agent system working!")
    else:
        print(f"❌ Error: {result['error']}")