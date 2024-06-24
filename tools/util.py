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

def parse_column_config(table_config: dict, table_name: str):
    tbl_attributes_list = table_config[table_name].split(sep=",")
    parsed_values = {}
    for column in tbl_attributes_list:
        column = column.strip()
        if bool(re.search(r"PRIMARY KEY", column, re.IGNORECASE)):
            continue
        else:
            col_to_list = column.split(sep=" ")
            if bool(re.search(r"date", col_to_list[0], re.IGNORECASE)):
                parsed_values[col_to_list[0]] = "DATE"
            else:
                parsed_values[col_to_list[0]] = col_to_list[1]
    return parsed_values

def formfactory(table_config: dict, table_name, submit_text: str):
    parsed_config = parse_column_config(table_config, table_name)
    values = {}
    for key, value in parsed_config.items():
        if value in("TEXT"):
            input = st.text_input(key)
            values[key] = input
        elif value in("INTEGER"):
            input = st.text_input(key)
            values[key] = input
        elif value in("DATE"):
            input = st.date_input(key)
            values[key] = input
    submitted = st.form_submit_button(submit_text)
    if submitted:
        return values
