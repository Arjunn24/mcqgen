import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
from src.mcqgenerator.utils import get_table_data,read_file
import streamlit as st
from langchain_community.callbacks import get_openai_callback
from src.mcqgenerator.MCQGenerator import generate_evaluate_chain
from src.mcqgenerator.logger import logging


with open(r'C:\Users\Dell\mcqgen\Response.json','r') as file :
    RESPONSE_JSON=json.load(file)


    st.title("MCQs creator application with langchain")

    with st.form("user inputs"):
        uploaded_file=st.file_uploader("upload a pdf or txt file")

        mcq_count=st.number_input("No. of MCQS", min_value=3, max_value=50)

        subject=st.text_input("Insert Subject",max_chars=20)

        tone=st.text_input("Complexity level of questions " ,max_chars=20 , placeholder="simple")

        button=st.form_submit_button("Create MCQs")

        if button and uploaded_file is not None and mcq_count and subject and tone :
            with st.spinner("loading"):
                try:
                    text=read_file(uploaded_file)
                    with get_openai_callback() as cb :
                        response=generate_evaluate_chain(
                            {
                                "text":text,
                                "number":mcq_count,
                                "subject":subject,
                                "tone":tone,
                                "response_json":json.dumps(RESPONSE_JSON)
                            }
                        )

                except Exception as e:
                    traceback.print_exception(type(e),e, e.__traceback__)
                    st.error("Error")        

                else:
                    print(f"Total Tokens :{cb.total_tokens}")
                    print(f"Prompt Tokens : {cb.prompt_tokens}")
                    print(f"Completion Tokens: {cb.completion_tokens}")
                    print(f"Total Cost : {cb.total_cost}")
                    if isinstance(response,dict):
                        quiz=response.get("quiz", None)
                        if quiz is not None:
                            table_data=get_table_data(quiz)
                            if table_data is not None :
                                df = pd.DataFrame(table_data)

                                df.index=df.index+1
                                st.table(df)
                                st.text_area(label="Review", value=response["review"])
                            else:
                                st.error("Error in the table data")

                    else:
                        st.write(response)                    
