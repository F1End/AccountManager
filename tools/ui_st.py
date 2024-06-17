"""Streamlit ui as first iteration"""

# for most cases, ui to call request_builder.py classes/methods,
# which will then articulate it to the other moduls
# session state setup at start to include hide/show operator keys

import streamlit as st

from tools.util import st_state_changer
import  tools.request_builder as rb

states = {"CurrentDB": None,
          "View": False,
          "Summary": False,
          "Chart": False,
          "Browse": False,
          "Edit": False,
          "AddTrade": False,
          "AddAccount": False,
          "AddCashflow": False,
          "Update": False,
          "ManualUpdate": False,
          "AutoUpdate": False,
          "Settings": False,
          "DBSettings": False,
          "OtherSettings": False
          }

for state, value in states.items():
    if state not in st.session_state:
        st.session_state[state] = value

app_session = rb.SessionManager()
st.session_state["CurrentDB"] = app_session.db_path

st.markdown("""
<style>
button {
    height: auto;
    padding-top: 10px !important;
    padding-bottom: 10px !important;
    width: 150px !important;
    }
</style>
""", unsafe_allow_html=True)

centercols = st.columns([4, 3, 4])
centercols[1].caption(f"""Active database: {st.session_state["CurrentDB"]}""")

lvl1_col1, lvl1_col2, lvl1_col3, lvl_col4 = st.columns(4)

with lvl1_col1:
    if st.button("View"):
        st_state_changer("View")

with lvl1_col2:
    if st.button("Edit"):
        st_state_changer("Edit")

with lvl1_col3:
    if st.button("Update"):
        st_state_changer("Update")

with lvl_col4:
    if st.button("Settings"):
        st_state_changer("Settings")


if st.session_state["View"]:
    st.divider()
    centercols = st.columns([3, 1, 3])
    centercols[1].caption("View")

    col1,col2,col3 = st.columns(3)
    with col1:
        if st.button("Summary"):
            st_state_changer("Summary")
    with col2:
        if st.button("Chart"):
            st_state_changer("Chart")
    with col3:
        if st.button("Browse"):
            st_state_changer("Browse")

    if st.session_state["Summary"]:
        centercols = st.columns([1, 1, 1])
        try:
            summary_df = app_session.generate_summary()
            centercols[1].dataframe(summary_df)
        finally:
            st_state_changer("Summary")

    if st.session_state["Chart"]:
        centercols = st.columns([1, 1, 1])
        try:
            chart = app_session.generate_chart()
            # centercols[1].dataframe(summary_df)
        finally:
            st_state_changer("Chart")

    if st.session_state["Browse"]:
        centercols = st.columns([1, 1, 1])
        try:
            # table selection -> returning content dataframe, in future add filters?
            test = app_session.communicate_table_attributes("accounts")
            print(test.to_string())
        finally:
            st_state_changer("Browse")

if st.session_state["Edit"]:
    st.divider()
    centercols = st.columns([3, 1, 3])
    centercols[1].caption("Edit")

    col1,col2,col3 = st.columns(3)
    with col1:
        st.button("Add Trade")
        # Form with inputs pegged to function
    with col2:
        st.button("Add Account")
        # Form with inputs pegged to function
    with col3:
        st.button("Add Cashflow")
        # Form with inputs pegged to function

if st.session_state["Update"]:
    st.divider()
    centercols = st.columns([3, 1, 3])
    centercols[1].caption("Update")

    col1,col2,col3 = st.columns(3)
    with col1:
        st.button("Manual Update")
        # form with filtered input boxes/dropdowns for Update
    with col2:
        st.button("Auto Update")
        # TBD

if st.session_state["Settings"]:
    st.divider()
    centercols = st.columns([3, 1, 3])
    centercols[1].caption("Settings")
    # centercols = st.columns([4, 3, 4])
    # centercols[1].caption(f"""Active database: {st.session_state["CurrentDB"]}""")
    # Add new Database
    # Save database?
    # TBD

    col1,col2,col3 = st.columns(3)
    with col1:
        if st.button("Database Settings"):
            st_state_changer("DBSettings")
    with col2:
        st.button("Other Settings")

    if st.session_state["DBSettings"]:
        centercols = st.columns([1, 1, 1])
        st.session_state["db_tables"] = app_session.communicate_table_attributes()
        centercols[1].write(f"""Active Database: {st.session_state["CurrentDB"]}""")
        # centercols[1].write(f"""Current schema: {st.session_state["db_tables"]}""")
        centercols[1].write(f"""Current schema""")
        centercols[1].dataframe(st.session_state["db_tables"])
        if centercols[1].button("Initiate DataBase tables from Schema"):
            app_session.initiate_db()
        # try:
        #     summary_df = app_session.generate_summary()
        #     centercols[1].dataframe(summary_df)
        # finally:
        #     st_state_changer("DBSettings")



# if db not selected/initiated, config window to pop up

# general menu options as root:
# view, update
# further down/away should be the settings/config section

# view: popups "view holdings summary", "check table", these should have button to make them stick even if new is opened
#   check table should be selectable, along with other potential options
#   chart for visual display should be among the options, also for holding summary
#   filtering and date/etc settings should be available

# update: popups for "add trade", "add cash movement", "add account", update prices (manual vs api), update rates (manual vs api)
#   these should have their own forms of course. Potentially dynamically generated

# settings/config:
#   db name and path and scheme setup
#   creeate new db
#   save/undo actions
#   edit tables
#



# Views: quick summary
# col1, col2, col3 = st.columns(3)


def run_streamlit_ui():
    raise NotImplemented