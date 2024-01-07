import os
import json
import time
from datetime import datetime

import streamlit as st

from pojo.message_pojo import MessagePojo
from src.app.app_handler import AppHandler
from src.llm.model_handler import ModelHandler

if __name__ == "__main__":
    logfile = f"./var/log/{datetime.now().strftime('%Y%m%d')}.txt"

    chat_history = list()
    answer = None
    model_store = None

    if "message" not in st.session_state:
        message_template = MessagePojo()
        st.session_state.message = message_template.to_json()

    st.set_page_config(page_title="Technical Assessment (Tu Weile)", page_icon="👋")
    st.image("./data/openai_logo.png", width=50)
    st.subheader("OpenAI Generative AI COE – SAP Technical Assessment")

    with st.sidebar:
        st.sidebar.title("Configuration ")
        openapi_key = st.text_input("Enter OpenAI API key:", placeholder="OpenAI API Key", type="password")
        pinecone_key = st.text_input("Enter Pinecone API key:", placeholder="Pinecone API Key", type="password")
        pinecone_env = st.text_input("Enter Pinecone env key:", placeholder="Pinecone env Key")

        chunk_size = st.number_input("Customize chunk size (Optional):", min_value=128, max_value=2048, value=512)
        chunk_overlap = st.number_input("Customize chunk overlap (optional):", min_value=0, max_value=128, value=32)
        k_value = st.number_input("Customize k value for response generation (optional):", min_value=0, max_value=10,
                                  value=5)

        add_data = st.button("Apply Data")

        if add_data:
            if st.session_state.message["chunkSize"] != chunk_size or \
                    st.session_state.message["chunkOverlap"] != chunk_overlap:
                st.session_state.refresh = True

            st.session_state.message["openAIKey"] = openapi_key
            st.session_state.message["pineconeKey"] = pinecone_key
            st.session_state.message["pineconeEnv"] = pinecone_env
            st.session_state.message["kValue"] = k_value
            st.session_state.message["chunkSize"] = chunk_size
            st.session_state.message["chunkOverlap"] = chunk_overlap

            if "application" not in st.session_state:
                st.session_state.application = AppHandler(st.session_state.message, logfile)
                st.session_state.model_handler = ModelHandler(st.session_state.message, logfile)

            if "refresh" in st.session_state and st.session_state.refresh is True:
                st.session_state.refresh = False
                st.session_state.application.rebuild_embeddings()
                time.sleep(10)
                st.write("Model has been rebuilt. Please give up to a minute for the embeddings to be built.")

            if "application" in st.session_state:
                model_store = st.session_state.application.pre_actions()
                st.session_state.ms = model_store

        st.write("Developed by Tu Weile in fulfillment of the requirements for the technical assessment.")

    styl = f"""
    <style>
        .stTextArea {{
          position: fixed;
          bottom: 3rem;
          z-index: 999;
        }}
    </style>
    """
    st.markdown(styl, unsafe_allow_html=True)

    query = st.text_area(" ", placeholder="Ask a question about me!")

    if "chat_history" in st.session_state:
        chat_history = st.session_state.chat_history

    if query:
        if not st.session_state.message["openAIKey"] or not st.session_state.message["pineconeKey"] or not \
        st.session_state.message["pineconeEnv"]:
            st.write("You have not entered the API and environment keys given to you. "
                     "Please enter them in the sidebar.")

        elif "ms" in st.session_state:
            model_store = st.session_state.ms

            if not model_store:
                st.write("Invalid API and environment keys entered. Please enter them again.\n \n"
                         "Otherwise, please contact Tu Weile at tuweile@u.nus.edu or +6581002610 for assistance.")

            else:
                result = st.session_state.model_handler.get_response_ss_with_memory_streamlit(
                    query=query,
                    vector_store=model_store,
                    keywords=st.session_state.message.get("kValue"),
                    chat_history=chat_history
                )

                if result:
                    answer, chat_history = result[0], result[1]
                    st.session_state["chat_history"] = chat_history

                    if answer:
                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown(f"##### Question: \n")
                            st.write(answer.get('question'))
                        with col2:
                            st.markdown(f"##### Response: \n")
                            st.write(answer.get('answer'))

                        st.divider()

                        if len(st.session_state["chat_history"]) > 1:
                            st.markdown("#### Conversation History")

                            for i in range(len(st.session_state["chat_history"]) - 2,
                                           -1,
                                           -1):
                                col1, col2 = st.columns(2)
                                data = answer.get("chat_history")
                                past_query, past_answer = data[i][0], data[i][1]

                                with col1:
                                    st.markdown(f"##### Question: \n")
                                    st.write(past_query)

                                with col2:
                                    st.markdown(f"##### Response: \n")
                                    st.write(past_answer)

                                st.divider()
