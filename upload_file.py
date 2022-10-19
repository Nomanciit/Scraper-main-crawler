import streamlit as st
from telegramcsv import GetData
import os
import shutil

getdata = GetData()

@st.cache
def convert_df_to_csv(df):
  # IMPORTANT: Cache the conversion to prevent computation on every rerun
  return df.to_csv().encode('utf-8')

def remove_files():
  try:
    directory = os.getcwd()
    csv_files = os.listdir(directory)
    files_ = []
    for item_csv in csv_files:
      if item_csv.endswith(".html"):
          os.remove(item_csv)
                            
  except OSError as error:
    print(error)


def main():
    st.title("Telegram message File Upload.")

    uploaded_files = st.file_uploader("Upload Telegram message.html files", accept_multiple_files=True,type=["html"])
    multiple_files =[]
    
    try:
        if uploaded_files:
            for uploaded_file in uploaded_files:
                multiple_files.append(uploaded_file.name)
                
                with open(os.path.join(uploaded_file.name),"wb") as f:
                    f.write(uploaded_file.getbuffer())
        print(multiple_files)
                
    except Exception as e:
        print(e)
        pass
    button = st.button("Get Data")
    
    if button:
        result,file_name= getdata.get_data(multiple_files)
        
        st.download_button(label="Download data as CSV",
                                      data=convert_df_to_csv(result),
                                      file_name=file_name,
                                      mime='text/csv',
                                    )
        st.success("Converted Successfully.....")
        remove_files()
        print('successfully all deleted...')

        try:
            directory = os.getcwd()
            html_files = os.listdir(directory)
            
            for item in html_files:
                if item.endswith(".html"):
                    os.remove( os.path.join( directory, item ) )
                        
        except OSError as error:
            print(error)



