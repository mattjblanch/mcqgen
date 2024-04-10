import os
import json
import pandas as pd
import traceback
from dotenv import load_dotenv
from src.mcqgenerator.logger import logging
from src.mcqgenerator.utils import read_file, get_table_data

load_dotenv()

key = os.getenv("OPENAI_API_KEY")

from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SequentialChain
from langchain.callbacks import get_openai_callback

llm = ChatOpenAI(openai_api_key=key,model_name="gpt-4-0125-preview", temperature=0.25)



template = """
Text: {text}
You are an expert Multiple Choice Question writer. 
You have been asked to write a multiple choice question based on the {text} and {subject}. 
The question should be challenging and test the reader's understanding of the text. 
The questions should not be repeated, and correct answer should be checked with question.
The question should have Four answer choices, with one correct answer and three distractors. 
The question should be multiple choice and have only one correct answer. 
The question should be clear and concise. 
The question should be in {tone} tone.
ensure that there are {number} of multiple choice questions.
Make sure to format your response like RESPONSE_JSON below and use it as a guide, and be sure to return valid json dixtionry as string as this will be used.
{response_json}
"""


# define input prompt
quiz_generateion_prompt = PromptTemplate(
    input_variables=["text", "number","subject", "tone", "response_json"],
    template=template
)
print("I'm a test pointer")
quiz_chain=LLMChain(llm=llm, prompt=quiz_generateion_prompt, output_key="quiz", verbose=True)


template2="""
You are an expert english grammarian and writer. Given a Multiple Choice Quiz for {subject} students.
You need to evaluate the complexity of the question and give a complete analysis of the quiz. Only use at max 200 words for complete analysis.
if the quiz is not at par with the cognitive and analytical skills of the students,
update the quiz questions which needs to be changed and the tone such that it perfectly fits the student abilities
Quiz_MCQs: {quiz}

Check from an expert English writer of the above quiz and update the quiz questions and tone to fit the student abilities.

"""

quiz_evaluation_prompt=PromptTemplate(input_variables=["subject", "quiz"], template=template2)



review_chain=LLMChain(llm=llm, prompt=quiz_evaluation_prompt, output_key="review", verbose=True)


generate_evaluate_chain=SequentialChain(chains=[quiz_chain, review_chain], input_variables=["text","number","subject","tone", "response_json"], output_variables=["quiz", "review"], verbose=True)


