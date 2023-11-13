from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains.question_answering import load_qa_chain
import pinecone
import streamlit as st
import time


# Create an OpenAI embeddings instance
OPENAI_API_KEY = st.secrets['OPENAI_API_KEY']
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# Initialize Pinecone docsearch
PINECONE_API_KEY = st.secrets['PINECONE_API_KEY']
PINECONE_API_ENV = "gcp-starter"
index_name = "testing"
index = pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_API_ENV)

docsearch = Pinecone.from_existing_index(index_name, embeddings)

# Create an OpenAI LLM (Language Model) instance
llm = ChatOpenAI(temperature=0.5, openai_api_key=OPENAI_API_KEY, model='gpt-4')
chain = load_qa_chain(llm, chain_type="stuff")

# Create Question and Answer function
def QnA(question):
    query = question
    docs = docsearch.similarity_search(query)
    answer = chain.run(input_documents=docs, question=query)
    return answer, docs



# BEGIN WEBPAGE:

# Title
st.title("MTI 1000")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask me anything"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    answer = QnA(prompt)[0]
    docs = QnA(prompt)[1][0].page_content

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        assistant_response = answer

        # Simulate stream of response with milliseconds delay
        for chunk in assistant_response.split():
            full_response += chunk + " "
            time.sleep(0.05)
            # Add a blinking cursor to simulate typing
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})

