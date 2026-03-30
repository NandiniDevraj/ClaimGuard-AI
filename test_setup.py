from app.utils.config import config
from app.utils.logger import get_logger

logger = get_logger("setup_test")

def test_openai():
    try:
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(
            model=config.OPENAI_MODEL,
            api_key=config.OPENAI_API_KEY,
            max_tokens=50
        )
        response = llm.invoke("Say exactly: Healthcare Auth Platform is ready.")
        logger.info(f"OpenAI: {response.content}")
        print("✅ OpenAI working")
    except Exception as e:
        print(f"❌ OpenAI failed: {e}")

def test_chromadb():
    try:
        import chromadb
        client = chromadb.PersistentClient(
            path=config.CHROMA_PERSIST_DIR
        )
        client.get_or_create_collection("test")
        print("✅ ChromaDB working")
    except Exception as e:
        print(f"❌ ChromaDB failed: {e}")

def test_presidio():
    try:
        from presidio_analyzer import AnalyzerEngine
        analyzer = AnalyzerEngine()
        results = analyzer.analyze(
            text="Patient John Doe, SSN 123-45-6789",
            language="en"
        )
        print(f"✅ Presidio working — {len(results)} PII entities found")
    except Exception as e:
        print(f"❌ Presidio failed: {e}")

def test_langchain():
    try:
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(
            model=config.OPENAI_MODEL,
            api_key=config.OPENAI_API_KEY
        )
        print("✅ LangChain + OpenAI working")
    except Exception as e:
        print(f"❌ LangChain failed: {e}")

def test_langgraph():
    try:
        from langgraph.graph import StateGraph
        print("✅ LangGraph working")
    except Exception as e:
        print(f"❌ LangGraph failed: {e}")

def test_embeddings():
    try:
        from langchain_openai import OpenAIEmbeddings
        embeddings = OpenAIEmbeddings(
            model=config.EMBEDDING_MODEL,
            api_key=config.OPENAI_API_KEY
        )
        result = embeddings.embed_query("test embedding")
        print(f"✅ OpenAI Embeddings working — dimension: {len(result)}")
    except Exception as e:
        print(f"❌ Embeddings failed: {e}")

if __name__ == "__main__":
    print("\n🔍 Testing all components...\n")
    test_openai()
    test_chromadb()
    test_presidio()
    test_langchain()
    test_langgraph()
    test_embeddings()
    print("\n🚀 If all green — we are ready to build!\n")