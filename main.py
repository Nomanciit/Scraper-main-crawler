from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
import pandas as pd
import streamlit as st
from multiapp import MultiApp
import numpy as np
#
from streamlit.report_thread import get_report_ctx
#from streamlit.script_run_context import get_script_run_ctx as get_report_ctx
import overlap_detection, crawl_hashtag, crawl_user,upload_file



hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """


class SessionState(object):
    def __init__(self, **kwargs):
        """A new SessionState object.

        Parameters
        ----------
        **kwargs : any
            Default values for the session state.

        Example
        -------
        >>> session_state = SessionState(user_name='', favorite_color='black')
        >>> session_state.user_name = 'Mary'
        ''
        >>> session_state.favorite_color
        'black'

        """
        for key, val in kwargs.items():
            setattr(self, key, val)


@st.cache(allow_output_mutation=True)
def get_session(id, **kwargs):
    return SessionState(**kwargs)


def get(**kwargs):
    """Gets a SessionState object for the current session.

    Creates a new object if necessary.

    Parameters
    ----------
    **kwargs : any
        Default values you want to add to the session state, if we're creating a
        new one.

    Example
    -------
    >>> session_state = get(user_name='', favorite_color='black')
    >>> session_state.user_name
    ''
    >>> session_state.user_name = 'Mary'
    >>> session_state.favorite_color
    'black'

    Since you set user_name above, next time your script runs this will be the
    result:
    >>> session_state = get(user_name='', favorite_color='black')
    >>> session_state.user_name
    'Mary'

    """
    ctx = get_report_ctx()
    id = ctx.session_id
    return get_session(id, **kwargs)


username = "ipri"
password = "nomi"


session_state = get(password="")

app = MultiApp()

# Add all your application here
app.add_app("Overlap Detection", overlap_detection.app)
app.add_app("Crawl Hashtag", crawl_hashtag.app)
app.add_app("Crawl User", crawl_user.app)
app.add_app("Telegram Scraper", upload_file.main)

if session_state.password != password:
    username_placeholder = st.sidebar.empty()
    usr = username_placeholder.text_input(
        "Username:",
        value="",
    )

    pwd_placeholder = st.sidebar.empty()
    pwd = pwd_placeholder.text_input("Password:", value="", type="password")

    btn_placeholder = st.sidebar.empty()
    btn = btn_placeholder.button("Login")

    session_state.password = pwd
    if btn and session_state.password == password and username == usr:
        pwd_placeholder.empty()
        username_placeholder.empty()
        btn.empty()
        app.run()
    elif session_state.password != "":
        st.error("the password you entered is incorrect")
else:
    app.run()


st.markdown(hide_streamlit_style, unsafe_allow_html=True)
