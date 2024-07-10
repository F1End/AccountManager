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

    def test_parse_column_config(self):
        input_dict = {'accounts':
                      'id INTEGER PRIMARY KEY, short_name TEXT, provider TEXT, active INTEGER, change_date TEXT'}
        expected_output = {"short_name": "TEXT", "provider": "TEXT", "active": "INTEGER", "change_date": "DATE"}
        output = util.parse_column_config(input_dict, "accounts")
        self.assertEqual(expected_output, output)

    @patch("tools.util.parse_column_config")
    @patch("tools.util.st")
    def test_formfactory(self, streamlit_mock, parse_columns_mock):
        table_config = {'accounts':
                        'id INTEGER PRIMARY KEY, short_name TEXT, provider TEXT, active INTEGER, change_date TEXT'}
        table_name = "test_table"
        submit_text = "my_test_form"
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

        actual = util.formfactory(table_config, table_name, submit_text)

        expected_calls = []
        for key in ["short_name", "provider", "active"]:
            expected_calls.append(call(key))

        parse_columns_mock.assert_called_with(table_config, table_name)
        streamlit_mock.text_input.assert_has_calls(expected_calls)
        streamlit_mock.date_input.assert_called_with("change_date")
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
