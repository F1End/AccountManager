import datetime
import unittest
from unittest.mock import Mock, MagicMock, patch, call

import pandas as pd
from streamlit.testing.v1 import AppTest

from tools import util
from tools import request_builder


class TestUtil(unittest.TestCase):

    # @patch("tools.util.st.session_state", new_callable=lambda: {})
    # def test_st_state_changer(self, streamlit_mock):
    #     state_mock = "mystate"
    #     streamlit_mock[state_mock] = False
    #     util.st_state_changer(state_mock)
    #     assert streamlit_mock[state_mock] is True
    #     util.st_state_changer(state_mock)
    #     assert streamlit_mock[state_mock] is False
    # #
    # def test_parse_column_config(self):
    #     input_dict = {'accounts':
    #                   'id INTEGER PRIMARY KEY, short_name TEXT, provider TEXT, active INTEGER, change_date TEXT'}
    #     expected_output = {"short_name": "TEXT", "provider": "TEXT", "active": "INTEGER", "change_date": "DATE"}
    #     output = util.parse_column_config(input_dict, "accounts")
    #     self.assertEqual(expected_output, output)

    def test_parse_column_config_foreign_key(self):
        input_dict = {"transactions": "tr_id INTEGER PRIMARY KEY, sec_id INTEGER, acc_id INTEGER, date TEXT, type TEXT, "
                                      "quantity INTEGER, unit_price REAL, total_price REAL, costs REAL, currency TEXT, "
                                      "recorded_date TEXT, FOREIGN KEY(sec_id) REFERENCES securities(sec_id), "
                                      "FOREIGN KEY(acc_id) REFERENCES accounts(id)"}
        expected_output = {"sec_id": "INTEGER", "acc_id": "INTEGER", "date": "DATE",
                           "type": "TEXT", "quantity": "INTEGER", "unit_price": "REAL",
                           "total_price": "REAL", "costs": "REAL", "currency": "TEXT", "recorded_date": "DATE",
                           "FOREIGN KEY(sec_id)": "REFERENCES securities(sec_id)",
                           "FOREIGN KEY(acc_id)": "REFERENCES accounts(id)"
                           }
        output = util.parse_column_config(input_dict, "transactions")
        self.assertEqual(expected_output, output)

    def test_restricted_column_options(self):
        # case: No foreign key requirement
        input_table_config_1 = {'short_name': 'TEXT', 'provider': 'TEXT', 'active': 'INTEGER', 'change_date': 'DATE'}
        expected_output_1 = {}
        output_1 = util.restricted_column_options(input_table_config_1)
        self.assertEqual(expected_output_1, output_1)

        # case: Foreign key(s) exists
        input_table_config_2 = {'sec_id': 'INTEGER', 'acc_id': 'INTEGER', 'date': 'DATE', 'type': 'TEXT',
                                'quantity': 'INTEGER', 'unit_price': 'REAL', 'total_price': 'REAL', 'costs': 'REAL',
                                'currency': 'TEXT', 'recorded_date': 'DATE',
                                'FOREIGN KEY(sec_id)': 'REFERENCES securities(sec_id)',
                                'FOREIGN KEY(acc_id)': 'REFERENCES accounts(id)'}
        expected_output_2 = {'sec_id': {'securities': 'sec_id'}, 'acc_id': {'accounts': 'id'}}
        output_2 = util.restricted_column_options(input_table_config_2)
        self.assertEqual(expected_output_2, output_2)

    def test_option_list_from_table_values(self):
        session_mngr_mock = MagicMock()
        table = "my_test_table"
        column = "test_column"

        # case: table is empty -> no optional values available
        session_mngr_mock.read.return_value = pd.DataFrame()
        expected_1 = [f"No selectable values found in table '{table}'"]
        output_1 = util.option_list_from_table_values(session_mngr_mock, table, column)
        self.assertEqual(expected_1, output_1)

        # case: There is one optional value
        columns = ["id", "short_name", "long_name", "test_column"]
        values = [1, "my_security", "security_long_name_here", "VALUE1"]
        session_mngr_mock.read.return_value = pd.DataFrame([values], columns=columns)
        expected_2 = {' - '.join(f"{value}" for value in values): values[-1]}
        output_2 = util.option_list_from_table_values(session_mngr_mock, table, column)
        self.assertEqual(expected_2, output_2)

        # case: Multiple optional values
        columns = ["id", "short_name", "long_name", "test_column"]
        values = [[1, "my_security", "security_long_name_here", "VALUE1"],
                  [2, "my_security_2", "security_long_name_here_2", "VALUE2"]]
        session_mngr_mock.read.return_value = pd.DataFrame(values, columns=columns)
        expected_3 = {}
        for value in values:
            key = ' - '.join(f"{val}" for val in value)
            expected_3[key] = value[-1]
        output_3 = util.option_list_from_table_values(session_mngr_mock, table, column)
        self.assertEqual(expected_3, output_3)

    @patch("tools.util.restricted_column_options")
    @patch("tools.util.parse_column_config")
    def test_build_form_configs(self, parse_columns_mock, restricted_col_opt_mock):
        session_mngr_mock = MagicMock()
        table_config = {'accounts':
                        'id INTEGER PRIMARY KEY, short_name TEXT, provider TEXT, sec_id TEXT, active INTEGER, change_date TEXT,'
                        'FOREIGN KEY(sec_id) REFERENCES securities(sec_id)'}
        session_mngr_mock.communicate_table_attributes.return_value = table_config
        table_name = "test_table"
        parsed_config = {"short_name": "TEXT",
                         "sec_id": "TEXT",
                         "provider": "TEXT",
                         "active": "INTEGER",
                         "change_date": "DATE",
                         "FOREIGN KEY(sec_id)": "REFERENCES securities(sec_id)"}
        parse_columns_mock.return_value = parsed_config
        restricted_col_opt_mock.return_value = {'sec_id': {'securities': 'sec_id'}}
        expected = (
            {"short_name": "TEXT",
             "sec_id": "TEXT",
             "provider": "TEXT",
             "active": "INTEGER",
             "change_date": "DATE",
             "FOREIGN KEY(sec_id)": "REFERENCES securities(sec_id)"},
            {'sec_id': {'securities': 'sec_id'}})

        output = util.build_form_configs(table_name, session_mngr_mock)

        parse_columns_mock.assert_called_with(table_config, table_name)
        restricted_col_opt_mock.assert_called_with(parsed_config)
        self.assertEqual(expected, output)

    @patch("tools.util.option_list_from_table_values")
    def test_build_val_column_selection(self, option_list_from_tbl_mock):
        restricted_value_columns = {'sec_id': {'securities': 'sec_id'}}
        column = "sec_id"
        session_mngr_mock = MagicMock()
        options_from_tbl = {"sec_1": "sec_id_1", "sec_2": "sec_id_2", "sec_3": "sec_id_3"}
        option_list_from_tbl_mock.return_value = options_from_tbl
        expected_display = ["sec_1", "sec_2", "sec_3"]

        output = util.build_val_column_selection(restricted_value_columns, column, session_mngr_mock)

        option_list_from_tbl_mock.assert_called_with(session_mngr_mock, "securities", "sec_id")
        self.assertEqual((options_from_tbl, expected_display), output)

    # @patch("tools.util.restricted_column_options")
    # @patch("tools.util.parse_column_config")
    @patch("tools.util.build_form_configs")
    @patch("tools.util.build_val_column_selection")
    @patch("tools.util.st")
    # @patch("tools.util.columns_value_options_from_db")
    def test_formfactory(self, streamlit_mock, build_val_mock, build_form_conf_mock):
        session_mngr_mock = MagicMock()
        table_name = "test_table"
        submit_text = "my_test_form"

        parsed_config = {"short_name": "TEXT",
                         "sec_id": "TEXT",
                         "provider": "TEXT",
                         "active": "INTEGER",
                         "change_date": "DATE",
                         "FOREIGN KEY(sec_id)": "REFERENCES securities(sec_id)"}
        restricted_value_columns = {'sec_id': {'securities': 'sec_id'}}
        build_form_conf_mock.return_value = parsed_config, restricted_value_columns

        sec_options = {"sec_1": "sec_id_1", "sec_2": "sec_id_2", "sec_3": "sec_id_3"}
        display_options = ["sec_1", "sec_2", "sec_3"]
        build_val_mock.return_value = sec_options, display_options

        text_input_return = "test_text_input_return"
        date_input_return = datetime.date(2024, 6, 6)
        selectbox_input_return = "sec_1"

        streamlit_mock.text_input.return_value = text_input_return
        streamlit_mock.date_input.return_value = date_input_return
        streamlit_mock.selectbox.return_value = selectbox_input_return
        streamlit_mock.form_submit_button.return_value = True

        expected = {"short_name": text_input_return,
                    "sec_id": sec_options[selectbox_input_return],
                    "provider": text_input_return,
                    "active": text_input_return,
                    "change_date": "2024-06-06"}

        actual = util.formfactory(table_name, submit_text, session_mngr_mock)

        expected_calls = []
        for key in ["short_name", "provider", "active"]:
            expected_calls.append(call(key))

        # Asserts
        streamlit_mock.text_input.assert_has_calls(expected_calls)
        build_form_conf_mock.assert_called_with(table_name, session_mngr_mock)
        build_val_mock.assert_called_with(restricted_value_columns, "sec_id", session_mngr_mock)
        streamlit_mock.date_input.assert_called_with("change_date")
        streamlit_mock.selectbox.assert_called_with("sec_id", display_options)
        streamlit_mock.form_submit_button.assert_called_with(submit_text)
        self.assertEqual(expected, actual)

    def test_restricted_column_options(self):
        test_config = {"id": "INTEGER PRIMARY KEY",
                       "short_name": "TEXT",
                       "FOREIGN KEY(sec_id)": "REFERENCES securities(sec_id)",
                       "FOREIGN KEY(acc_id)": "REFERENCES accounts(id)"}
        expected = {"sec_id": {"securities": "sec_id"},
                    "acc_id": {"accounts": "id"}}
        options = util.restricted_column_options(test_config)
        self.assertEqual(expected, options)

    def columns_value_options_from_db_side_effect(self, table_name, column_name, session_mngr):
        if column_name == "active":
            return [1, 0]
        else:
            return []

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
