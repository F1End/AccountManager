import re

import streamlit as st

from tools.dbtools import dbManager
from tools.request_builder import SessionManager


def st_state_changer(state_value: str, ):
    """Cycle between True/False for a session state with the same button"""
    if st.session_state[state_value]:
        st.session_state[state_value] = False
    else:
        st.session_state[state_value] = True

def parse_column_config(table_config: dict, table_name: str) -> dict:
    tbl_attributes_list = table_config[table_name].split(sep=",")
    parsed_values = {}
    for column in tbl_attributes_list:
        column = column.strip()
        if bool(re.search(r"PRIMARY KEY", column, re.IGNORECASE)):
            continue
        elif bool(re.search(r"FOREIGN KEY", column, re.IGNORECASE)):
            col_to_list = column.split(sep=" ")
            concat_key = col_to_list[0] + " " + col_to_list[1]
            parsed_values[concat_key] = col_to_list[2] + " " + col_to_list[3]
        else:
            col_to_list = column.split(sep=" ")
            if bool(re.search(r"date", col_to_list[0], re.IGNORECASE)):
                parsed_values[col_to_list[0]] = "DATE"
            else:
                parsed_values[col_to_list[0]] = col_to_list[1]
    return parsed_values

def restricted_column_options(table_config: dict) -> dict:
    options = {}
    for key, val in table_config.items():
        parsed_key = re.split("[()]", key)
        match parsed_key:
            case ["FOREIGN KEY", column, _]:
                parsed_val = re.split("[( )]", val)
                options[column] = {parsed_val[1]: parsed_val[2]}
    return options

def option_list_from_table_values(session_mgr: SessionManager,table: str, column: str) -> list:
    df = session_mgr.read(session_mgr.tables[table])
    if df.empty:
        return [f"No selectable values found in table '{table}'"]
    dict_of_options = {}
    for d in df.to_dict(orient='records'):
        formatted = ' - '.join([f"{value}" for value in d.values()])
        dict_of_options[formatted] = d[column]
    return dict_of_options

def build_form_configs(table_name: str, session_mgr: SessionManager) -> (dict, dict):
    table_config = session_mgr.communicate_table_attributes(table_name)
    parsed_config = parse_column_config(table_config, table_name)
    restricted_value_columns = restricted_column_options(parsed_config)
    return parsed_config, restricted_value_columns

def build_val_column_selection(restricted_value_columns: dict, column: str,
                                          session_mgr: SessionManager) -> (dict, list):
    table, column = next(iter(restricted_value_columns[column].items()))
    options = option_list_from_table_values(session_mgr, table, column)
    options_display = [option for option in options.keys()]
    return options, options_display

def formfactory(table_name: str, submit_text: str, session_mgr: SessionManager) -> dict:
    parsed_config, restricted_value_columns = build_form_configs(table_name, session_mgr)
    values = {}
    for key, value in parsed_config.items():
        if key in restricted_value_columns.keys():
            options, options_display = build_val_column_selection(restricted_value_columns, key,
                                                                  session_mgr)
            selection_value = st.selectbox(key, options_display)
            values[key] = options[selection_value]
        elif value in ("TEXT"):
            input_value = st.text_input(key)
            values[key] = input_value
        elif value in ("INTEGER"):
            input_value = st.text_input(key)
            values[key] = input_value
        elif value in ("REAL"):
            input_value = st.number_input(key)
            values[key] = input_value
        elif value in ("DATE"):
            input_value = st.date_input(key)
            db_time = dbManager.to_dbtime(input_value)
            values[key] = db_time
    submitted = st.form_submit_button(submit_text)
    if submitted:
        return values

def columns_value_options_from_db(table_name: str, column_name: str, session_mngr: SessionManager) -> list:
    df = session_mngr.read(session_mngr.tables["types"])
    df = df[(df["category"] == table_name + "_col_values") & (df["option"] == column_name)]
    if not df.empty:
        return df["value"].to_list()
    return []

def show_any_tbl(session_mngr: SessionManager):
    tables = session_mngr.list_of_tables_in_db()
    with st.form("Browse table") as browse_form:
        selected_table = st.selectbox("Select table to display", tables)
        col1,col2,col3 = st.columns(3)
        with col1:
            submitted = st.form_submit_button("Show table")
        with col2:
            edit = st.form_submit_button("Edit table")
        with col3:
            add_entry = st.form_submit_button("Add new entry")

        if submitted:
            if selected_table == st.session_state["Browse-Show"]:
                st.session_state["Browse-Show"] = False
            else:
                st.session_state["Browse-Show"] = selected_table

        if edit:
            if selected_table == st.session_state["Browse-Edit"]:
                st.session_state["Browse-Edit"] = False
            else:
                st.session_state["Browse-Edit"] = selected_table

        if add_entry:
            if selected_table == st.session_state["Browse-Add"]:
                st.session_state["Browse-Add"] = False
            else:
                st.session_state["Browse-Add"] = selected_table

        if st.session_state["Browse-Show"]:
            show_table(session_mngr)
        if st.session_state["Browse-Edit"]:
            edit_table(session_mngr)
        if st.session_state["Browse-Add"]:
            append_table(session_mngr)

def edit_table(session_mngr: SessionManager) -> None:
    raise NotImplemented

def show_table(session_mngr: SessionManager) -> None:
    table_df = session_mngr.read(st.session_state["Browse-Show"])
    st.dataframe(table_df)

def append_table(session_mngr: SessionManager) -> None:
    table_to_append = st.session_state["Browse-Add"]
    values = formfactory(table_to_append, f"Adding entry to {table_to_append}", session_mngr)
    if values:
        print(f"Values to be written: {values}")
        st.write(values)
        session_mngr.add_entry(table_to_append, values)

def confirm_delete():
    raise NotImplemented

