from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
import pandas as pd
import streamlit as st
import numpy as np

#from streamlit.report_thread import get_report_ctx
import streamlit as st


hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """


def app():
    st.title("Hashtag Overlap Detection")

    index = "tweets"

    # sidebar = st.sidebar.empty()
    hashtag1 = st.text_input("Hashtag 1:", value="")

    # sidebar2 = st.sidebar.empty()
    hashtag2 = st.text_input("Hashtag 2:", value="")

    # sidebar3 = st.sidebar.empty()
    button = st.button("Find Overlap")

    if hashtag1 and hashtag2 and button:
        data_load_state = st.text("Performing overlap analysis.....")
        HOST_URL = "http://localhost:9200"
        es_client = Elasticsearch(
            [HOST_URL], http_auth=("ipri", "123"), retry_on_timeout=True
        )

        constructed_query = {
            "query": {
                "bool": {
                    "must": [],
                    "filter": [
                        {
                            "bool": {
                                "should": [{"match_phrase": {"hashtags": hashtag1}}],
                                "minimum_should_match": 1,
                            }
                        }
                    ],
                    "should": [],
                    "must_not": [],
                }
            }
        }
        hits = list(
            scan(client=es_client, index=index, query=constructed_query, size=1000)
        )

        results = []
        for hit in hits:
            results.append(hit["_source"])

        df_1 = pd.DataFrame(results)

        constructed_query = {
            "query": {
                "bool": {
                    "must": [],
                    "filter": [
                        {
                            "bool": {
                                "should": [{"match_phrase": {"hashtags": hashtag2}}],
                                "minimum_should_match": 1,
                            }
                        }
                    ],
                    "should": [],
                    "must_not": [],
                }
            }
        }

        hits = list(
            scan(client=es_client, index=index, query=constructed_query, size=1000)
        )

        results = []
        for hit in hits:
            results.append(hit["_source"])

        df_2 = pd.DataFrame(results)

        try:
            b_complement = df_1[~df_1.username.isin(df_2.username)]
            b_complement = (
                b_complement.groupby(["name", "username"])
                .size()
                .reset_index(name="counts")
                .sort_values("counts", ascending=False)
            )
            b_complement["profile link"] = (
                "https://twitter.com/" + b_complement["username"]
            )

            a_complement = df_2[~df_2.username.isin(df_1.username)]
            a_complement = (
                a_complement.groupby(["name", "username"])
                .size()
                .reset_index(name="counts")
                .sort_values("counts", ascending=False)
            )
            a_complement["profile link"] = (
                "https://twitter.com/" + a_complement["username"]
            )

            df_1 = df_1[df_1.username.isin(df_2.username)]
            df_2 = df_2[df_2.username.isin(df_1.username)]

            final_df = pd.concat([df_1, df_2]).drop_duplicates(subset=["id"])
            final_df = final_df.sort_values("username")

            final_df.fillna("", inplace=True)

            usernames = (
                final_df.groupby(["name", "username"])
                .size()
                .reset_index(name="counts")
                .sort_values("counts", ascending=False)
            )

            usernames["profile link"] = "https://twitter.com/" + usernames["username"]

            st.subheader("Users tweeting on both #" + hashtag1 + " and #" + hashtag2)
            st.write(usernames)

            st.subheader("Users tweeting on #" + hashtag1 + " but not #" + hashtag2)
            st.write(b_complement)

            st.subheader("Users tweeting on #" + hashtag2 + " but not #" + hashtag1)
            st.write(a_complement)

            st.subheader("Tweets on these hashtags")
            st.write(final_df)

            st.markdown(hide_streamlit_style, unsafe_allow_html=True)

            result = {
                "tweets": final_df.to_dict("records"),
                "users": usernames.to_dict("records"),
            }

            data_load_state.text("Overlap analysis...done!")
        except AttributeError as ex:
            st.error("No data found for the provided hashtags")


st.markdown(hide_streamlit_style, unsafe_allow_html=True)
