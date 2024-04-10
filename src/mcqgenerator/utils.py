import os
import PyPDF2
import json
import traceback


def read_file(file):
    if file.name.endswith(".pdf"):
        try:
            pdf_reader=PyPDF2.PdfFileReader(file)
            text=""
            for page in pdf_reader.pages:
                text+=page.extract_text()
            return text
        
        except Exception as e:
            raise Exception("Error reading pdf file")
        
    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")
    
    else:
        raise Exception("Invalid file format")
    
def get_table_data(quiz_str):
    print("I am going to try to print quiz string from get_table_data function")
    print(quiz_str)
    print(type(quiz_str))
    print("quiz string should be above")
    try:
        quiz_dict=json.loads(quiz_str)
        quiz_table_data=[]

        for key,value in quiz_dict.items():
            mcq=value["mcq"]
            options= " | ".join([
                f"{option}: {option_value}"
                for option, option_value in value["option"].items()
            ])
            correct=value["correct"]
            quiz_table_data.append([key, mcq, options, correct])
        return quiz_table_data
    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        return False

