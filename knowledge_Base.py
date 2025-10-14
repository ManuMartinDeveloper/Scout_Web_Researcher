# file: knowledge_base.py
import chromadb
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Initialize the embedding model once
print("Loading embedding model...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
print("Embedding model loaded.")

# Initialize ChromaDB client
# This will create a local persistent database in the 'chroma_db' directory
client = chromadb.PersistentClient(path="./chroma_db")

def create_and_store_embeddings(company_name: str, text_corpus: str):
    """
    Creates a knowledge base for a company by chunking text,
    creating embeddings, and storing them in ChromaDB.
    """
    # 1. Sanitize company name for collection name
    collection_name = company_name.lower().replace(" ", "_")
    
    # 2. Get or create a collection in ChromaDB
    collection = client.get_or_create_collection(name=collection_name)
    
    # 3. Split the text into manageable chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )
    chunks = text_splitter.split_text(text_corpus)
    
    if not chunks:
        print("Text corpus is empty, nothing to store.")
        return None
        
    # 4. Create embeddings and store them in ChromaDB
    # ChromaDB's add method can handle embedding creation automatically if you pass the model
    # But doing it manually gives us more control. Let's do it manually.
    print(f"Creating embeddings for {len(chunks)} chunks...")
    embeddings = embedding_model.encode(chunks, show_progress_bar=True)
    
    # Generate IDs for each chunk
    ids = [f"{collection_name}_{i}" for i in range(len(chunks))]
    
    # 5. Add to the collection
    collection.add(
        embeddings=embeddings.tolist(),
        documents=chunks,
        ids=ids
    )
    
    print(f"Successfully created knowledge base for '{company_name}' with {len(chunks)} chunks.")
    return collection

# Test function
if __name__ == '__main__':
    from crawler import crawl_website
    
    test_url = "https://www.webdura.in/about-us/"
    company = "webdura"
    
    print(f"--- Testing Knowledge Base Creation for {company} ---")
    page_text = crawl_website(test_url)
    
    if page_text:
        create_and_store_embeddings(company, page_text)