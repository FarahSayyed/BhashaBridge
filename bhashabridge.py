import streamlit as st
from anuvaad import BhashiniPipeline 
import os

# set page configuration
st.set_page_config(
    page_title='Bhasha Bridge'
)

# initialize the BhashiniPipeline
pipeline = BhashiniPipeline(
    api_key=st.secrets["ulca_api_key"],
    user_id=st.secrets["ulca_userid"],
    auth_token=st.secrets["authorization_key"],
    endpoint="https://dhruva-api.bhashini.gov.in/services/inference/pipeline"
)

# define language options and their corresponding codes
language_mapping = {
    'English': 'en',
    'Assamese': 'as',
    'Awadhi': 'awa',
    'Bengali': 'bn',
    'Bhojpuri': 'bho',
    'Bodo': 'brx',
    'Dogri': 'doi',
    'Gujarati': 'gu',
    'Hindi': 'hi',
    'Kannada': 'kn',
    'Kashmiri': 'ks',
    'Khasi': 'kha',
    'Maithili': 'mai',
    'Malayalam': 'ml',
    'Manipuri': 'mni',
    'Marathi': 'mr',
    'Mizo': 'lus',
    'Odia': 'or',
    'Sanskrit': 'sa',
    'Sindhi': 'sd',
    'Tamil': 'ta',
    'Telugu': 'te',
    'Urdu': 'ur'
}

# create tuples for source and target languages
source_languages = tuple(language_mapping.keys())
target_languages = tuple(language_mapping.keys())

# title
st.markdown('<h1 style="text-align: center;"> BhashaBridge </h1>', unsafe_allow_html=True)
st.markdown('<h5 style="text-align: center; margin-top:-20px;"> Indian language translator </h5>', unsafe_allow_html=True)
st.write("")

# dropdowns for selecting source and target languages
source_lang = st.selectbox("Select a source language", source_languages)
st.write("")
default_target_index = target_languages.index("Hindi")
target_lang = st.selectbox("Select a target language", target_languages, index=default_target_index)
st.write("")

# get the corresponding language codes
s_lang = language_mapping.get(source_lang)
t_lang = language_mapping.get(target_lang)

# input text box for the text to translate
source_text = st.text_input("Enter the text to translate")

# translate button
# if st.button("Translate"):
if source_text and source_lang and target_lang:
    try:
        # perform translation
        result = pipeline.run_pipeline(
            source_text=source_text,
            source_lang=s_lang,
            target_lang=t_lang,
            translate=True
        )
        # display the translated text
        st.markdown(result['translation'])
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
