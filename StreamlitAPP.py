import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
from src.mcqgenerator.utils import read_file, get_table_data
import streamlit as st
from langchain_community.callbacks import get_openai_callback
from src.mcqgenerator.mcqgenerator import generate_evaluate_chain
from src.mcqgenerator.logger import logging

# loading json file
with open('./Response.json', 'r') as file:
    RESPONSE_JSON = json.load(file)

st.title("Multiple Choice Question Generator with Langchain")

# Create a form 
with st.form("user_inputs"):

    # Create a file uploader
    uploaded_file = st.file_uploader("Upload a pdf or txt file")

    # Input fields
    mcq_count = st.number_input("Number of MCQs", min_value=1, max_value=10, value=5)

    # Set the subject
    subject = st.text_input("Insert Subject", max_chars=20)

    # Set the tone
    tone = st.selectbox("Select Tone", ["Formal", "Informal"])

    # Create submit button
    button = st.form_submit_button("Generate MCQs")

    # Check if the button is clicked and all required fields are filled
    if button and uploaded_file is not None and mcq_count and subject and tone:

        try:
            # Read the file
            text = read_file(uploaded_file)
            print("file read successfully")
            # Count tokens and cost of the API call
            with get_openai_callback() as cb:
                response=generate_evaluate_chain(
                    {
                        "text": text,
                        "number": mcq_count,
                        "subject": subject,
                        "tone": "tone",
                        "response_json": json.dumps(RESPONSE_JSON)
                    }
                )
            # Display the generated MCQs
            #st.write(get_table_data(response["quiz"]))

        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
            st.error("Error generating MCQs")
            st.error(str(e))

        else:
            if isinstance(response, dict):
                # Extract the quiz data from the response
                quiz=response.get("quiz")
                quiz = quiz.replace("```json\n","").replace("\n```","")
                if quiz is not None:
                    table_data = get_table_data(quiz)
                    if table_data is not None:
                        print("Table data is what i am about to print")
                        print(type(table_data))
                        print("Table data should be above")
                        df=pd.DataFrame(table_data)
                        df.index=df.index+1
                        st.table(df)
                        # Display the review in a text box as well
                        st.text_area(label="Review", value=response["review"])
                        st.text_area(
                            label="Cost",
                            value=f"""Total cost is USD${cb.total_cost} 
                                     Total tokens is {cb.total_tokens}  
                                     Prompt tokens is {cb.prompt_tokens}
                                     Completion tokens is {cb.completion_tokens}"""
                                     )
                        
                        # Save the quiz data to a csv file
                        quiz=pd.DataFrame(table_data, columns=["Question Number", "Question", "Options", "Correct Answer"])
                        quiz.to_csv(f"./experiment/{subject}-{tone}-{mcq_count}.csv",index=False)
                    else:
                        st.error("Error getting table data")
            else:
                st.write(response)