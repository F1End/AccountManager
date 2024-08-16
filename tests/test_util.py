import datetime
import unittest
from unittest.mock import Mock, MagicMock, patch, call

import pandas as pd
from streamlit.testing.v1 import AppTest

from tools import util
from tools import request_builder


class TestUtil(unittest.TestCase):

    @patch("tools.util.st.session_state", new_callable=lambda: {})
    def test_st_state_changer(self, streamlit_mock):
        state_mock = "mystate"
        streamlit_mock[state_mock] = False
        util.st_state_changer(state_mock)
        assert streamlit_mock[state_mock] is True
        util.st_state_changer(state_mock)
        assert streamlit_mock[state_mock] is False
    #
    def test_parse_column_config(self):
        input_dict = {'accounts':
                      'id INTEGER PRIMARY KEY, short_name TEXT, provider TEXT, active INTEGER, change_date TEXT'}
        expected_output = {"short_name": "TEXT", "provider": "TEXT", "active": "INTEGER", "change_date": "DATE"}
        output = util.parse_column_config(input_dict, "accounts")
        self.assertEqual(expected_output, output)

    @patch("tools.util.parse_column_config")
    @patch("tools.util.st")
    @patch("tools.util.columns_value_options_from_db")
    def test_formfactory(self, col_values_mock, streamlit_mock, parse_columns_mock):
        session_mngr_mock = MagicMock()
        table_config = {'accounts':
                        'id INTEGER PRIMARY KEY, short_name TEXT, provider TEXT, active INTEGER, change_date TEXT'}
        session_mngr_mock.communicate_table_attributes.return_value = table_config
        table_name = "test_table"
        submit_text = "my_test_form"
        col_values_mock.return_value = []
        parse_columns_mock.return_value = {"short_name": "TEXT",
                                           "provider": "TEXT",
                                           "active": "INTEGER",
                                           "change_date": "DATE"}
        text_input_return = "test_text_input_return"
        date_input_return = datetime.date(2024, 6, 6)

        streamlit_mock.text_input.return_value = text_input_return
        streamlit_mock.date_input.return_value = date_input_return
        streamlit_mock.form_submit_button.return_value = True

        expected = {"short_name": text_input_return,
                    "provider": text_input_return,
                    "active": text_input_return,
                    "change_date": "2024-06-06"}

        actual = util.formfactory(table_name, submit_text, session_mngr_mock)

        expected_calls = []
        for key in ["short_name", "provider", "active"]:
            expected_calls.append(call(key))

        parse_columns_mock.assert_called_with(table_config, table_name)
        streamlit_mock.text_input.assert_has_calls(expected_calls)
        streamlit_mock.date_input.assert_called_with("change_date")
        streamlit_mock.form_submit_button.assert_called_with(submit_text)
        self.assertEqual(expected, actual)

    def columns_value_options_from_db_side_effect(self, table, col, session):
        if col == "active":
            return [1, 0]
        else:
            return []

    @patch("tools.util.parse_column_config")
    @patch("tools.util.st")
    @patch("tools.util.columns_value_options_from_db")
    def test_formfactory_with_options(self, col_values_mock, streamlit_mock, parse_columns_mock):
        session_mngr_mock = MagicMock()
        table_config = {'accounts':
                        'id INTEGER PRIMARY KEY, short_name TEXT, provider TEXT, active INTEGER, change_date TEXT'}
        session_mngr_mock.communicate_table_attributes.return_value = table_config
        table_name = "test_table"
        submit_text = "my_test_form"
        value_options = [1, 0]
        col_values_mock.side_effect = self.columns_value_options_from_db_side_effect
        parse_columns_mock.return_value = {"short_name": "TEXT",
                                           "provider": "TEXT",
                                           "active": "INTEGER",
                                           "change_date": "DATE"}
        text_input_return = "test_text_input_return"
        date_input_return = datetime.date(2024, 6, 6)
        select_box_return = 1

        streamlit_mock.text_input.return_value = text_input_return
        streamlit_mock.date_input.return_value = date_input_return
        streamlit_mock.selectbox.return_value = date_input_return
        streamlit_mock.form_submit_button.return_value = 1

        expected = {"short_name": text_input_return,
                    "provider": text_input_return,
                    "active": select_box_return,
                    "change_date": "2024-06-06"}

        actual = util.formfactory(table_name, submit_text, session_mngr_mock)

        expected_calls = []
        for key in ["short_name", "provider"]:
            expected_calls.append(call(key))

        parse_columns_mock.assert_called_with(table_config, table_name)
        streamlit_mock.text_input.assert_has_calls(expected_calls)
        streamlit_mock.date_input.assert_called_with("change_date")
        streamlit_mock.selectbox.assert_called_with(value_options)
        streamlit_mock.form_submit_button.assert_called_with(submit_text)
        self.assertEqual(expected, actual)

    def test_columns_value_options_from_db(self):
        session_mngr_mock = MagicMock()
        session_mngr_mock.tables = {"types": "types_test"}
        mock_df = pd.DataFrame({"category": ["some_settings", "types_col_values", "types_col_values",
                                             "types_col_values", "types_col_values"],
                                "option": ["some_option", "currency", "currency", "active", "active"],
                                "value": ["some_value", "USD", "HUF", "True", "False"]})
        session_mngr_mock.read.return_value = mock_df

        expected_options = ["USD", "HUF"]
        options = util.columns_value_options_from_db("types", "currency", session_mngr_mock)
        session_mngr_mock.read.assert_called_with("types_test")
        self.assertEqual(expected_options, options)

        expected_options = []
        options = util.columns_value_options_from_db("types", "quantity", session_mngr_mock)
        session_mngr_mock.read.assert_called_with("types_test")
        self.assertEqual(expected_options, options)



    @patch("tools.util.st")
    def test_show_any_tbl(self, streamlit_mock):
        selected_table = "some_table_name"
        # streamlit_mock.form.__enter__.return_value = MagicMock()
        form_context_manager_mock = MagicMock()
        streamlit_mock.form.return_value.__enter__.return_value = form_context_manager_mock
        streamlit_mock.selectbox.return_value = selected_table
        mock_col1 = MagicMock()
        mock_col2 = MagicMock()
        mock_col3 = MagicMock()
        streamlit_mock.columns.return_value = mock_col1, mock_col2, mock_col3

        form_context_manager_mock.assert_called_once()

    @patch('tools.util.append_table')
    @patch('tools.util.edit_table')
    @patch('tools.util.show_table')
    @patch('tools.util.st.selectbox')
    @patch('tools.util.st.form')
    @patch('tools.util.st.form_submit_button')
    @patch('tools.util.st.columns')
    @patch('tools.util.st.session_state', new_callable=dict)
    def test_show_any_tbl(self, mock_session_state, mock_columns, mock_submit_button, mock_form, mock_selectbox,
                          mock_show_table, mock_edit_table, mock_append_table):
        mock_session_mngr = MagicMock()
        mock_session_mngr.list_of_tables_in_db.return_value = ['table1', 'table2']

        mock_form.return_value.__enter__.return_value = 'browse_form'
        mock_selectbox.return_value = 'table1'

        col_mock = MagicMock()
        mock_columns.return_value = (col_mock, col_mock, col_mock)

        mock_session_state["Browse-Show"] = False
        mock_session_state["Browse-Edit"] = False
        mock_session_state["Browse-Add"] = False

        # Case 1: Show table only
        mock_submit_button.side_effect = [True, False, False]  # "Show table" button clicked
        util.show_any_tbl(mock_session_mngr)

        self.assertEqual(mock_session_state["Browse-Show"], 'table1')
        mock_show_table.assert_called_once_with(mock_session_mngr)
        mock_edit_table.assert_not_called()
        mock_append_table.assert_not_called()

        # Case 2: Edit table only
        mock_session_state["Browse-Show"] = False  # Reset for next test
        mock_submit_button.side_effect = [False, True, False]  # "Edit" button clicked
        util.show_any_tbl(mock_session_mngr)
        self.assertEqual(mock_session_state["Browse-Edit"], 'table1')
        mock_append_table.assert_not_called()
        mock_edit_table.assert_called_once_with(mock_session_mngr)
        mock_show_table.assert_called_once()

        # Case 3: Add new entry
        mock_session_state["Browse-Show"] = False # Reset for next test
        mock_session_state["Browse-Edit"] = False # Reset for next test
        mock_submit_button.side_effect = [False, False, True]  # "Add new entry" button clicked
        util.show_any_tbl(mock_session_mngr)

        self.assertEqual(mock_session_state["Browse-Add"], 'table1')
        mock_append_table.assert_called_once_with(mock_session_mngr)
        mock_show_table.assert_called_once()  # It was called once before, so no new call should be made
        mock_edit_table.assert_called_once()

        # Case 4: Turning all options off
        mock_session_state["Browse-Show"] = 'table1'  # Pre-set to 'table1'
        mock_session_state["Browse-Edit"] = 'table1' # Pre-set to 'table1'
        mock_submit_button.side_effect = [True, True, True]  # All buttons clicked again
        util.show_any_tbl(mock_session_mngr)

        # Check that "Browse-Show" was toggled off
        self.assertFalse(mock_session_state["Browse-Show"])
        mock_show_table.assert_called_once()
        mock_edit_table.assert_called_once()
        mock_append_table.assert_called_once()

    @patch("tools.util.st.dataframe")
    @patch("tools.util.st.session_state")
    def test_show_table(self, streamlit_session_state_mock, streamlit_df_mock):
        values = {"Browse-Show": "Mock_some_table_name"}
        streamlit_session_state_mock.__getitem__.side_effect = values.__getitem__
        session_mngr_mock = MagicMock()
        read_return_value = "Mock_read_return"
        session_mngr_mock.read.return_value = "Mock_read_return"

        util.show_table(session_mngr_mock)

        streamlit_session_state_mock.__getitem__.assert_called_with("Browse-Show")
        session_mngr_mock.read.assert_called_with(values["Browse-Show"])
        streamlit_df_mock.assert_called_with(read_return_value)

    @patch("tools.util.st.write")
    @patch("tools.util.formfactory")
    @patch("tools.util.st.session_state")
    def test_append_table(self, st_session_state_mock, formfactory_mock, st_write_mock):
        values = {"Browse-Add": "Mock_some_table_name"}
        st_session_state_mock.__getitem__.side_effect = values.__getitem__
        values_form_return = "Mock_some_values_to_append"
        formfactory_mock.return_value = values_form_return
        session_mngr_mock = MagicMock()

        util.append_table(session_mngr_mock)
        st_session_state_mock.__getitem__.assert_called_with("Browse-Add")
        formfactory_mock.assert_called_with(values["Browse-Add"], f"Adding entry to {values['Browse-Add']}",
                                            session_mngr_mock)
        st_write_mock.assert_called_with(values_form_return)
        session_mngr_mock.add_entry.assert_called_with(values["Browse-Add"], values_form_return)
