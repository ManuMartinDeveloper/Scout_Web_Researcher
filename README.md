### Project Summary

This project, named **"Scout Web Researcher"** or **"Company Intelligence Agent,"** is a sophisticated AI-powered tool designed to perform in-depth analysis of a company's website. The application allows a user to input a website URL, which the tool then crawls to build a comprehensive knowledge base. Subsequently, the user can ask questions about the company in a conversational chat interface and receive AI-generated answers based solely on the crawled website content.

The repository contains two different front-end implementations for this application: one using **Streamlit** and a more recent version using **Gradio**.

---
### Key Features

* **Deep Web Crawling**: The tool features an advanced web crawler that systematically navigates a target website, following internal links to gather text from multiple pages. The user can control the depth of the crawl using a slider.
* **Vector-Based Knowledge Base**: It uses a `sentence-transformer` model (`all-MiniLM-L6-v2`) to convert the crawled text into numerical embeddings. These embeddings are then stored in a local **ChromaDB** vector database, creating a searchable knowledge base specific to each company.
* **Retrieval-Augmented Generation (RAG)**: To answer questions without hallucination, the application uses a RAG pipeline. When a user asks a question, the `qa_agent.py` module retrieves the most relevant text chunks from the ChromaDB knowledge base.
* **Conversational AI Chat**: The retrieved text chunks and the user's question are passed to a large language model (LLM) via the Hugging Face API. The `llm_handler.py` is configured to use powerful conversational models like **Meta's Llama 3** to generate a final, human-readable answer.
* **Dual UI Implementations**: The repository includes both a Streamlit version (`app_streamlit.py`) and a Gradio version (`app_gradio.py`), demonstrating flexibility in front-end development. The Gradio version is the most recent implementation.

---
### Technical Architecture

The application is modular, with distinct Python scripts for each part of the workflow:

1.  **`crawler.py`**: Handles the deep crawling of the target website.
2.  **`knowledge_Base.py`**: Manages text chunking, embedding creation, and storage in ChromaDB.
3.  **`qa_agent.py`**: Responsible for querying the ChromaDB database to retrieve relevant text chunks based on the user's question.
4.  **`llm_handler.py`**: Interfaces with the Hugging Face API using the `InferenceClient` to get the final answer from the chosen LLM.
5.  **`app_gradio.py` / `app_streamlit.py`**: Provides the user interface for interacting with the system.

The project is configured to use a `.gitignore` file to exclude virtual environments and `.env` files from the repository. The `requirements.txt` file lists all necessary dependencies, including `gradio`, `streamlit`, `chromadb`, `sentence-transformers`, and `huggingface_hub`.
