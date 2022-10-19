from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
import pandas as pd
#from airflow.api.client.local_client import Client
import streamlit as st
import numpy as np
from datetime import datetime

from Hashkeywords import ScrapeData
scrape_user =ScrapeData()


#from streamlit.report_thread import get_report_ctx
import streamlit as st


hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """

            
@st.cache
def convert_df_to_csv(df):
  # IMPORTANT: Cache the conversion to prevent computation on every rerun
  return df.to_csv().encode('utf-8')
  
  
def app():
    try:
        st.title("Crawl Hashtag")

        index = "tweets"

        hashtag = st.text_input("Hashtag or Keyword:", value="#Bajwa")
        _from = st.date_input("From: ")
        _to = st.date_input("To: ")
        limit = st.number_input("Limit",value=500)
    #
    #    if compute_sentiment:
    #        aspect = st.text_input("Sentiment aspect", value="")

        button = st.button("Fetch Data")
        file_name = hashtag+"_.csv"
        if hashtag and button:
            df = scrape_user.get_data(hashtag,_from,_to,limit)
            data_load_state = st.text("Data Fetched Successfully.....")
            st.download_button(label="Download data as CSV",
                                      data=convert_df_to_csv(df),
                                      file_name=file_name,
                                      mime='text/csv',
                                    )
    except:
        st.text("Something went wrong........")
        st.text("Please increase the limit and Change the Dates. Thanks")

        
    #        c.trigger_dag(dag_id='crawl_hashtags', run_id=unique_run_id, conf=config)

st.markdown(hide_streamlit_style, unsafe_allow_html=True)
