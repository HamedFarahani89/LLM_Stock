# Import necessary libraries
import os  # For interacting with the operating system
import streamlit as st  # For creating a web-based UI
import pickle  # For saving and loading Python objects
import time  # For adding delays to simulate processing
from langchain import OpenAI  # LangChain's OpenAI interface for language models
from langchain.chains import RetrievalQAWithSourcesChain  # For retrieval-based Q&A with sources
from langchain.text_splitter import RecursiveCharacterTextSplitter  # For splitting text into chunks
from langchain.document_loaders import UnstructuredURLLoader  # For loading unstructured data from URLs
from langchain.embeddings import OpenAIEmbeddings  # For generating text embeddings using OpenAI
from langchain.vectorstores import FAISS  # FAISS library for efficient similarity search

# Load environment variables (e.g., OpenAI API key) from a .env file
from dotenv import load_dotenv

load_dotenv()

# Streamlit title and sidebar setup
st.title("EntityExplorer: AI-Powered Entity Research Tool 📈")  # Main title for the app
st.sidebar.title("News Article URLs")  # Sidebar title for URL input section

# Initialize a list to store user-provided URLs
urls = []
for i in range(5):  # Allow users to input up to 3 URLs
    url = st.sidebar.text_input(f"URL {i + 1}")  # Input box for each URL
    urls.append(url)

# Button to start processing the URLs
process_url_clicked = st.sidebar.button("Process URLs")

# File path to save or load the FAISS index
file_path = "faiss_store_openai.pkl"

# Placeholder for showing status messages on the main page
main_placeholder = st.empty()

# Initialize OpenAI language model (LLM) with specific parameters
llm = OpenAI(temperature=0.9, max_tokens=500)

# When the "Process URLs" button is clicked
if process_url_clicked:
    # Load data from the provided URLs
    loader = UnstructuredURLLoader(urls=urls)
    main_placeholder.text("Data Loading...Started...✅✅✅")
    data = loader.load()

    # Split the loaded text data into smaller chunks for efficient processing
    text_splitter = RecursiveCharacterTextSplitter(
        separators=['\n\n', '\n', '.', ','],  # Define chunk split rules
        chunk_size=1000  # Maximum size of each chunk
    )
    main_placeholder.text("Text Splitter...Started...✅✅✅")
    docs = text_splitter.split_documents(data)  # Perform text splitting

    # Generate text embeddings using OpenAI and save them into a FAISS vector store
    embeddings = OpenAIEmbeddings()
    vectorstore_openai = FAISS.from_documents(docs, embeddings)
    main_placeholder.text("Embedding Vector Started Building...✅✅✅")

    # Add a delay for a better user experience
    time.sleep(2)

    # Save the FAISS vector store to a pickle file for future use
    with open(file_path, "wb") as f:
        pickle.dump(vectorstore_openai, f)

# Input box for the user to ask a question about the processed data
query = main_placeholder.text_input("Question: ")

# If a query is provided
if query:
    # Check if the FAISS vector store file exists
    if os.path.exists(file_path):
        # Load the saved FAISS vector store from the pickle file
        with open(file_path, "rb") as f:
            vectorstore = pickle.load(f)

            # Create a retrieval chain with sources using the vector store and LLM
            chain = RetrievalQAWithSourcesChain.from_llm(
                llm=llm,
                retriever=vectorstore.as_retriever()
            )

            # Process the query and retrieve the result
            result = chain({"question": query}, return_only_outputs=True)
            # The result will be a dictionary with keys: "answer" and "sources"

            # Display the answer to the user's query
            st.header("Answer")
            st.write(result["answer"])

            # Display the sources, if available
            sources = result.get("sources", "")  # Retrieve sources, if any
            if sources:
                st.subheader("Sources:")
                # Split the sources by newlines for better readability
                sources_list = sources.split("\n")
                for source in sources_list:
                    st.write(source)
