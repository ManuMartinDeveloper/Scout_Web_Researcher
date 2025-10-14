# file: app.py
import streamlit as st
from urllib.parse import urlparse
from crawler import crawl_website
from knowledge_Base import create_and_store_embeddings
from qa_agent import query_knowledge_base
import pandas as pd
from llm_handler import get_llm_answer # Or your preferred LLM handler

# --- App Configuration ---
st.set_page_config(
    page_title="CIAgent 🕵️ | Conversational",
    page_icon="🕵️",
    layout="wide"
)

# --- Session State Initialization ---
# This ensures that variables persist across user interactions
if 'company_name' not in st.session_state:
    st.session_state.company_name = None
if "messages" not in st.session_state:
    st.session_state.messages = []
visited_urls = []
# --- Sidebar for Building the Knowledge Base ---
with st.sidebar:
    st.header("1. Build Knowledge Base")
    url_input = st.text_input("Enter Company Website URL", placeholder="https://stripe.com")
    access_website = st.slider(
        label="Deepness of Website Crawl",
        min_value=0,
        max_value=50,
        value=25,  # The default starting value
        step=1      # The interval between values
        )


    if st.button("Build Knowledge Base"):
        if url_input:
            with st.spinner(f"Processing {url_input}... This may take a few minutes."):
                try:
                    parsed_url = urlparse(url_input)
                    company_name = parsed_url.netloc.replace(".", "_")
                    if not company_name:
                        st.error("Invalid URL.")
                        st.stop()
                except Exception as e:
                    st.error(f"Could not parse URL. Error: {e}")
                    st.stop()
                
                # Use the powerful crawler
                website_text, visited_urls = crawl_website(url_input, max_pages=access_website)

            if website_text:
                with st.spinner(f"Creating knowledge base for '{company_name}'..."):
                    create_and_store_embeddings(company_name, website_text)
                
                # Update session state
                st.session_state.company_name = company_name
                # Reset chat history for the new company
                st.session_state.messages = [{"role": "assistant", "content": f"Hello! I've learned about {company_name}. What would you like to know?"}]
                st.success(f"Knowledge base for '{company_name}' is ready!")
            else:
                st.error("Failed to fetch content. The website may be blocking crawlers or requires JavaScript.")
        else:
            st.warning("Please enter a URL.")
    if st.session_state.company_name and visited_urls:    
        st.write(f"List of websites crawled: ")
        df = pd.DataFrame(visited_urls, columns=["Crawled URLs"])
        st.dataframe(df)

# --- Main Chat Interface ---
st.title("Company Intelligence Agent 🕵️")

if st.session_state.company_name:
    st.info(f"Knowledge Base Active for: **{st.session_state.company_name}**")
else:
    st.info("Please build a knowledge base for a company using the sidebar to begin.")

# Display past chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# The chat input box at the bottom of the screen
if prompt := st.chat_input("Ask a follow-up question...", disabled=(not st.session_state.company_name)):
    # 1. Add user's message to history and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Generate and display the AI's response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Retrieve context from the knowledge base
            retrieved_chunks = query_knowledge_base(st.session_state.company_name, prompt)
            
            # Get the final answer from the LLM
            final_answer = get_llm_answer(prompt, retrieved_chunks) # Or your preferred LLM function call
            
            st.markdown(final_answer)
    
    # 3. Add AI's response to the history
    st.session_state.messages.append({"role": "assistant", "content": final_answer})