# file: qa_agent.py
import chromadb
from sentence_transformers import SentenceTransformer

# Load the same embedding model we used to create the knowledge base
print("QA Agent: Loading embedding model...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
print("QA Agent: Embedding model loaded.")

# Connect to the same persistent ChromaDB client
client = chromadb.PersistentClient(path="./chroma_db")

def query_knowledge_base(company_name: str, query: str, n_results: int = 3):
    """
    Queries the knowledge base for a given company and question.
    """
    # 1. Sanitize company name to get the collection name
    collection_name = company_name.lower().replace(" ", "_")
    
    try:
        # 2. Get the collection from ChromaDB
        collection = client.get_collection(name=collection_name)
        
        # 3. Create an embedding for the user's query
        query_embedding = embedding_model.encode(query).tolist()
        
        # 4. Query the collection
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        # 5. Return the documents (the actual text chunks)
        return results['documents'][0]
        
    except ValueError as e:
        print(f"Error: Collection '{collection_name}' not found. {e}")
        return [f"Knowledge base for '{company_name}' not found. Please build it first."]

# Test function
if __name__ == '__main__':
    company = "www_mongodb_com" # Use the sanitized name from your db
    test_query = "What is MongoDB Atlas?"
    
    print(f"--- Testing QA Agent for '{company}' ---")
    retrieved_chunks = query_knowledge_base(company, test_query)
    
    print(f"\nQuery: '{test_query}'")
    print("\n--- Retrieved Context ---")
    for i, chunk in enumerate(retrieved_chunks):
        print(f"Chunk {i+1}:\n{chunk}\n")