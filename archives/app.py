# file: app.py
import streamlit as st
from urllib.parse import urlparse
from crawler import crawl_website
from knowledge_Base import create_and_store_embeddings
from qa_agent import query_knowledge_base
from llm_handler import get_llm_answer # <-- IMPORT OUR NEW AI FUNCTION

# --- App Configuration ---
st.set_page_config(page_title="CIAgent 🕵️", page_icon="🕵️", layout="wide")

st.title("Company Intelligence Agent 🕵️")
st.write("This tool builds a knowledge base from a company's website and answers your questions.")

# --- Session State Initialization ---
if 'company_name' not in st.session_state:
    st.session_state.company_name = None

# --- Main App Logic ---

# Section 1: Build the Knowledge Base
with st.sidebar:
    st.header("1. Build Knowledge Base")
    url_input = st.text_input("Enter Company Website URL", placeholder="e.g., https://www.mongodb.com")

    if st.button("Build Knowledge Base"):
        if url_input:
            with st.spinner(f"Processing {url_input}..."):
                try:
                    parsed_url = urlparse(url_input)
                    company_name = parsed_url.netloc.replace(".", "_")
                    if not company_name:
                        st.error("Invalid URL.")
                        st.stop()
                except Exception as e:
                    st.error(f"Could not parse URL. Error: {e}")
                    st.stop()
                
                website_text = crawl_website(url_input)

            if website_text:
                with st.spinner(f"Building knowledge base for '{company_name}'..."):
                    create_and_store_embeddings(company_name, website_text)
                st.session_state.company_name = company_name
                st.success(f"Knowledge base for '{company_name}' is ready!")
            else:
                st.error("Failed to fetch content.")
        else:
            st.warning("Please enter a URL.")

st.markdown("---")

# Section 2: Ask Questions
st.header("2. Ask Questions About the Company")

if st.session_state.company_name:
    st.info(f"Knowledge Base Active for: **{st.session_state.company_name}**")
    
    query_input = st.text_input("Ask a question", placeholder="e.g., What services do they offer?")
    
    if st.button("Get Answer"):
        if query_input:
            with st.spinner("Thinking..."):
                # 1. Retrieve relevant chunks
                retrieved_chunks = query_knowledge_base(st.session_state.company_name, query_input)
                
                # 2. Get the final answer from the LLM
                final_answer = get_llm_answer(query_input, retrieved_chunks)
                
                # 3. Display the results
                st.subheader("🤖 AI-Generated Answer:")
                st.markdown(final_answer)
                
                with st.expander("Show Retrieved Context"):
                    st.info("The AI generated its answer based on the following text chunks from the website:")
                    for i, chunk in enumerate(retrieved_chunks):
                        st.write(f"**Chunk {i+1}:**\n\n> {chunk}")
        else:
            st.warning("Please enter a question.")
else:
    st.warning("You must build a knowledge base first. Use the sidebar to enter a website URL.")