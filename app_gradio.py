# file: app.py
import gradio as gr
import pandas as pd
from urllib.parse import urlparse

# Import your existing backend functions
from crawler import crawl_website
from knowledge_Base import create_and_store_embeddings
from qa_agent import query_knowledge_base
from llm_handler import get_llm_answer

# --- 1. Gradio Core Functions (Event Handlers) ---

def build_knowledge_base(url, depth, progress=gr.Progress(track_tqdm=True)):
    """
    This function is triggered by the 'Build' button. It crawls a website,
    builds the knowledge base, and updates the UI.
    """
    if not url:
        raise gr.Error("URL cannot be empty.", "Please enter a valid website URL.")

    # --- Step 1: Parse URL and set up company name ---
    progress(0, desc="Parsing URL...")
    try:
        parsed_url = urlparse(url)
        company_name = parsed_url.netloc.replace(".", "_")
        if not company_name:
            raise gr.Error("Invalid URL.", "Please enter a full URL (e.g., https://www.example.com).")
    except Exception as e:
        raise gr.Error("URL Parsing Failed.", f"Could not parse the URL. Error: {e}")

    # --- Step 2: Crawl the website ---
    progress(0.2, desc=f"Crawling {url}...")
    website_text, visited_urls = crawl_website(url, max_pages=int(depth))
    if not website_text:
        raise gr.Error("Crawling Failed.", "Failed to fetch content. The website may be blocking crawlers or requires JavaScript.")
    
    # --- Step 3: Create the knowledge base ---
    progress(0.7, desc=f"Building knowledge base for '{company_name}'...")
    create_and_store_embeddings(company_name, website_text)
    
    # --- Step 4: Prepare UI updates ---
    progress(0.9, desc="Finalizing...")
    # Create the initial chat message
    welcome_message = [(None, f"Hello! I've learned about {company_name}. What would you like to know?")]
    # Create the DataFrame for visited URLs
    visited_urls_df = pd.DataFrame(visited_urls, columns=["Crawled URLs"])
    
    # Return updates for multiple components
    # CORRECT: Returning a list of values in the correct order
    return [
        company_name,
        welcome_message,
        gr.update(interactive=True, placeholder=f"Ask about {company_name}..."),
        visited_urls_df
    ]

def respond(user_message, chat_history, company_name):
    """
    This function is triggered when the user sends a message in the chat.
    """
    if not company_name:
        raise gr.Error("No Knowledge Base Active", "Please build a knowledge base first using the controls on the left.")

    # 1. Append the user's message to the chat history
    chat_history.append([user_message, None])
    yield chat_history # Yield to immediately show the user's message

    # 2. Retrieve context and get the LLM's answer
    retrieved_chunks = query_knowledge_base(company_name, user_message)
    final_answer = get_llm_answer(user_message, retrieved_chunks)

    # 3. Stream the final answer back to the chatbot
    chat_history[-1][1] = final_answer
    yield chat_history


# --- 2. Gradio Interface Definition ---

with gr.Blocks(theme=gr.themes.Soft(), title="Company Intelligence Agent 🕵️") as demo:
    # State variables to hold data that isn't a visible component
    company_name_state = gr.State(value=None)
    
    gr.Markdown("# Company Intelligence Agent 🕵️")

    with gr.Row():
        # --- Left Column (Controls) ---
        with gr.Column(scale=1):
            gr.Markdown("## 1. Build Knowledge Base")
            url_input = gr.Textbox(label="Enter Company Website URL", placeholder="https://stripe.com")
            crawl_depth_slider = gr.Slider(
                minimum=1, maximum=50, value=10, step=1, label="Crawl Depth (Max Pages)"
            )
            build_button = gr.Button("Build Knowledge Base", variant="primary")
            
            gr.Markdown("### Crawled URLs")
            visited_urls_df = gr.Dataframe(headers=["Crawled URLs"], wrap=True)

        # --- Right Column (Chat Interface) ---
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(label="Chat with the Agent", bubble_full_width=False)
            chat_input = gr.Textbox(
                label="Ask a question",
                placeholder="Build a knowledge base first...",
                interactive=False  # Disabled until a KB is built
            )
            chat_input.submit(
                fn=respond,
                inputs=[chat_input, chatbot, company_name_state],
                outputs=[chatbot],
            )
            chat_input.submit(lambda: "", None, chat_input) # Clear input box after submit

    # --- 3. Event Wiring ---
    build_button.click(
        fn=build_knowledge_base,
        inputs=[url_input, crawl_depth_slider],
        outputs=[company_name_state, chatbot, chat_input, visited_urls_df]
    )

if __name__ == "__main__":
    demo.launch()