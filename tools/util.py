import re

import streamlit as st

def st_state_changer(state_value: str):
    """Cycle between True/False for a session state with the same button"""
    if st.session_state[state_value]:
        st.session_state[state_value] = False
    else:
        st.session_state[state_value] = True

def dynamic_table_form(table_name: str, attributes_dict: dict):
    tbl_attributes_list = attributes_dict[table_name].split(sep="'")
    # for column in tbl_attributes_list:
    #     if bool(re.search(r"PRIMARY KEY", column, re.IGNORECASE)):
    #         next
    #     else:
    #         col_to_list = column.split(sep=" ")
    #         if col_to_list[1] == "TEXT":
    #             st.text_input(col)