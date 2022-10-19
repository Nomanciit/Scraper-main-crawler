from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
import pandas as pd
#from airflow.api.client.local_client import Client
import streamlit as st
import numpy as np
from datetime import datetime
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb

from timeline import ScrapeData
scrape_user = ScrapeData()


#from streamlit.report_thread import get_report_ctx
import streamlit as st
import base64


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
        st.title("Crawl User")

        index = "tweets"

        username = st.text_input("Twitter Handle:", value="@AbdulqadirARY")
        print("username",username)
        _from = st.date_input("From: ")
        _to = st.date_input("To: ")
        limit = st.number_input("Limit",value=500)
        
        

        button = st.button("Fetch Data")
        file_name = username+".csv"
        if username and button:
            scrape_user.get_data(username,_from,_to,limit)
            df = scrape_user.get_data(username,_from,_to,limit)
            data_load_state = st.text("Data Fetched Successfully.....")
            st.download_button(label="Download data as CSV",
                                      data=convert_df_to_csv(df),
                                      file_name=file_name,
                                      mime='text/csv',
                                    )
    except:
        st.text("Something went wrong")
        st.text("Please increase the limit and Change the Dates. Thanks")

            
            
       
#        c.trigger_dag(dag_id='crawl_users', run_id=unique_run_id, conf=config)
 
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
