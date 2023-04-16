import streamlit as st
import openai as ai
import numpy as np
import pandas as pd
# import aspose.words as aw
from htmldocx import HtmlToDocx
from bing_image_downloader import downloader
import os
from PIL import Image
import base64
import os
import json
import pickle
import uuid
import re
import shutil
#from streamlit_login_auth_ui.widgets import __login__
import requests
from google.oauth2 import service_account
# from gsheetsdb import connect
from gspread_pandas import Spread,Client
import gspread_pandas
from datetime import datetime
from pptx import Presentation
from io import BytesIO
from pptx.util import Inches, Pt

# Config

ai.api_key = st.secrets["openai_api_key"]

API_KEY = st.secrets["openai_api_key"]
API_ENDPOINT = "https://api.openai.com/v1/chat/completions"

# For GPT-4
def generate_chat_completion(messages, model="gpt-4", temperature=1, max_tokens=None):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    data = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }

    if max_tokens is not None:
        data["max_tokens"] = max_tokens

    response = requests.post(API_ENDPOINT, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")

# For Da-Vinci 3
def generate_response(MODEL, PROMPT, MAX_TOKENS=750, TEMP=0.99, TOP_P=0.5, N=1, FREQ_PEN=0.3, PRES_PEN = 0.9):
  response = ai.Completion.create(
          engine = MODEL,
          # engine="text-davinci-002", # OpenAI has made four text completion engines available, named davinci, ada, babbage and curie. We are using davinci, which is the most capable of the four.
          prompt=PROMPT, # The text file we use as input (step 3)
          max_tokens=MAX_TOKENS, # how many maximum characters the text will consists of.
          temperature=TEMP,
          # temperature=int(temperature), # a number between 0 and 1 that determines how many creative risks the engine takes when generating text.,
          top_p=TOP_P, # an alternative way to control the originality and creativity of the generated text.
          n=N, # number of predictions to generate
          frequency_penalty=FREQ_PEN, # a number between 0 and 1. The higher this value the model will make a bigger effort in not repeating itself.
          presence_penalty=PRES_PEN # a number between 0 and 1. The higher this value the model will make a bigger effort in talking about new topics.
      )
  return response['choices'][0]['text']

MODEL = 'text-davinci-003'

st.header('Knowledge Organiser Generator')


txt_button = st.checkbox('What is a knowledge organiser?', help='The learning science behind Knowledge Organisers')
if txt_button:
    st.subheader('Key Features')
    overview_txt = st.markdown("""
    - [Precisely specifying what students should know by the end of the unit.](https://improvingteaching.co.uk/2017/04/23/better-planning-better-teaching-better-learning-a-template/)
    - Contain knowledge which is [broken down into manageble units.](https://www.supermemo.com/en/blog/twenty-rules-of-formulating-knowledge)
    - Knowledge organisers should be structured so students can use them to self-quiz.(https://researchschool.org.uk/bradford/news/knowledge-organisers-facilitating-retrieval)
    - Students should be taught how to use them to self-quiz. """)

    st.subheader('Tips for Use')
    key_concepts_txt = st.markdown('''
    - Use for [self-checking after a task.](https://classteaching.wordpress.com/2018/09/14/using-knowledge-organisers-to-improve-retrieval-practice/)
    - [Don't test all at once.](https://classteaching.wordpress.com/2018/09/14/using-knowledge-organisers-to-improve-retrieval-practice/)
    - [Students should understand concepts, learn how the concepts relate to others and form an overall picture and, finally, use a knoweldge organiser to memorise key information.](https://www.supermemo.com/en/blog/twenty-rules-of-formulating-knowledge)
    ''')

    st.subheader('"Objections"')
    lethal_injections_txt = st.markdown('''
    - Knowledge Organisers were originally developed at Michaela School, and pioneered by Joe Kirby.
    - Some teachers find they lead to students ['blindly copying answers'](https://shallteach.wordpress.com/2020/07/25/knowledge-organisers-a-failed-revolution/).
    - Knowledge organisers don't work as well for (subjects with more procedural knowledge)[https://tothereal.wordpress.com/2018/06/04/why-maths-teachers-dont-like-knowledge-organisers/], e.g. Maths.
    - They present knoweldge as linear, when [information is often relational.](https://shallteach.wordpress.com/2020/07/25/knowledge-organisers-a-failed-revolution/)
    ''')

email = st.text_input('Email')
topic = st.text_input('Knowledge Organiser Topic')
reading_age = st.slider('Reading Age', 0, 18)

components = []
st.markdown("Humanities and Sciences Options")
key_words_check = st.checkbox('Key Words')
key_concepts_check = st.checkbox('Key concepts')
timeline_check = st.checkbox('Timeline')

st.markdown("English Options")

characters_check = st.checkbox('Key Characters')
characters_quotes_check = st.checkbox('Character Quotes')
dramatic_devices_check = st.checkbox('Dramatic Devices')
plot_check = st.checkbox('Plot')

generate_worksheet = st.button('Generate Worksheet')

if generate_worksheet:
    with st.spinner(text="Your worksheet is in the oven 🧠 ... If you want to work with Pedagogical to improve the app please click [here](https://forms.gle/jDy1WNgrnCTWsDG16) ... Thank you!"):

        key_words_prompt = f"You are an expert teacher trying to teach your {reading_age} year old student about {topic}. Create a list of key words and their definitions so that student can understand the topic."
        if key_words_check:
            key_words_messages = [
                {"role": "system", "content": "You are an expert teacher."},
                {"role": "user", "content": key_words_prompt}
            ]
            key_words = generate_response(MODEL, key_words_prompt) #generate_chat_completion(key_words_messages)
            components.append(key_words)
                


        key_concepts_prompt = f"You are an expert teacher trying to teach your {reading_age} year old student about {topic}. Create a list of key concepts and their definitions that would be important for them to understand this topic."
        if key_concepts_check:
            key_concepts_messages = [
                {"role": "system", "content": "You are an expert teacher."},
                {"role": "user", "content": key_concepts_prompt}
            ]
            key_concepts = generate_response(MODEL, key_concepts_prompt)
            components.append(key_concepts)



        timeline_prompt = f"You are an expert teacher trying to teach your {reading_age} year old student about {topic}. Create a timeline so that your student can understand the topic."
        if timeline_check:
            timeline_messages = [
                {"role": "system", "content": "You are an expert teacher."},
                {"role": "user", "content": timeline_prompt}
            ]
            timeline = generate_response(MODEL, timeline_prompt)
            components.append(timeline)


        characters_prompt = f"You are an expert teacher trying to teach your {reading_age} year old student about {topic}. Create a list of important characters and their descriptions so that student can understand the topic."
        if characters_check:
            characters_messages = [
                {"role": "system", "content": "You are an expert teacher."},
                {"role": "user", "content": characters_prompt}
            ]
            characters = generate_response(MODEL, characters_prompt)
            components.append(characters)






        characters_quotes_prompt = f"You are an expert teacher trying to teach your {reading_age} year old student about {topic}. Create a list of important quotes by characters from {topic} so that your student can understand the topic."
        if characters_quotes_check:
            characters_quotes_messages = [
                {"role": "system", "content": "You are an expert teacher."},
                {"role": "user", "content": characters_quotes_prompt}
            ]
            characters_quotes = generate_response(MODEL, characters_quotes_prompt)
            components.append(characters_quotes)


        dramatic_devices_prompt = f"You are an expert teacher trying to teach your {reading_age} year old student about {topic}. Create a list of important dramatic devices from {topic} and how they used in {topic}."
        if dramatic_devices_check:
            dramatic_devices_messages = [
                {"role": "system", "content": "You are an expert teacher."},
                {"role": "user", "content": dramatic_devices_prompt}
            ]
            dramatic_devices = generate_response(MODEL, dramatic_devices_prompt )
            components.append(dramatic_devices)

        plot_prompt = f"You are an expert teacher trying to teach your {reading_age} year old student about {topic}. Create a list of key episodes in the plot so that your student can understand the topic."
        if plot_check:
            plot_messages = [
                {"role": "system", "content": "You are an expert teacher."},
                {"role": "user", "content": plot_prompt}
            ]
            plot = generate_response(MODEL, plot_prompt)
            components.append(plot)

        components_dict = {val: name for name, val in locals().items() if val in components}
        component_names = [components_dict[val] for val in components]

            # worksheet_end = """</body>
            # </html>"""

            # # Construct Worksheet from components
            # full_worksheet = worksheet_head

            # for component in components:
            #     if component:
            #         full_worksheet += component

            # full_worksheet += worksheet_end
    # f = open('worksheet.html','w')
    # f.write(knowledge_organiser_html)
    # f.close()

    # new_parser = HtmlToDocx()
    # new_parser.table_style = 'TableGrid'
    # new_parser.parse_html_file("worksheet.html", "worksheet")

    # file_path = 'worksheet.docx'
    # with open(file_path,"rb") as f:
    #     base64_word = base64.b64encode(f.read()).decode('utf-8')

    # with open("worksheet.docx", "rb") as word_file:
    #     wordbyte = word_file.read()


    # downloaded = st.download_button(label="Download Word Document", 
    # data=wordbyte,
    # file_name="pedagogical_worksheet.docx",
    # mime='application/octet-stream')
        

        prs = Presentation()
        title_only_slide_layout = prs.slide_layouts[5]
        slide = prs.slides.add_slide(title_only_slide_layout)
        shapes = slide.shapes

        shapes.title.text = f'{topic} Knowledge Organiser'

        cols = len(components)
        rows = 2
        left = top = Inches(2.0)
        width = Inches(6.0)
        height = Inches(0.8)

        table = shapes.add_table(rows, cols, left, top, width, height).table

        for i, component in enumerate(components):
            # set column widths
            table.columns[i].width = Inches(2.0)
            # table.columns[1].width = Inches(4.0)

            # table.font.size = Pt(6)

            # # write column headings
            # table.cell(0, 0).text = 'Key Words'
            # table.cell(0, 1).text = 'Key Concepts'

            # # write body cells
            # table.cell(1, 0).text = key_words
            # table.cell(1, 1).text = key_concepts

            # # write column headings
            table.cell(0, i).text = component_names[i]

            # # write body cells
            table.cell(1, i).text = component

        def iter_cells(table):
            for row in table.rows:
                for cell in row.cells:
                    yield cell

        for cell in iter_cells(table):
            for paragraph in cell.text_frame.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(6)


        prs.save('knowledge_organiser.pptx')

        # save the output into binary form
        binary_output = BytesIO()
        prs.save(binary_output) 

        st.download_button(label = 'Download Powerpoint',
                        data = binary_output.getvalue(),
                        file_name = 'pedagogical_knowledge_organiser.pptx')







