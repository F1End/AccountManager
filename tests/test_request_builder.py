import unittest
from unittest.mock import Mock, MagicMock, patch, call
import os
import random
import datetime

import pandas as pd

import tools.request_builder
from tools import request_builder


class TestSessionManager_with_default_values(unittest.TestCase):

    @patch("tools.dbtools.dbManager")
    def setUp(self, dbmanager_mock) -> None:
        dbmanager_mock.return_value = Mock()
        self.session_mgr = request_builder.SessionManager()
        dbmanager_mock.assert_called_with(self.session_mgr.db_path)

    def test_default_values(self):
        default_config = os.path.join("config", "default_db.yaml")
        default_db_path = os.path.join("db", "accounts")
        self.assertEqual(self.session_mgr.default_db_config, default_config)
        self.assertEqual(self.session_mgr.db_path, default_db_path)

    @patch('yaml.safe_load')
    @patch('builtins.open')
    def test_db_scheme(self, mock_open, mock_yaml):
        mock_open.return_value.__enter__.return_value = "mocked_file"
        value = self.session_mgr.db_scheme()
        mock_open.assert_called_with(self.session_mgr.default_db_config)
        mock_yaml.assert_called_with("mocked_file")

    def test_create_tables_from_scheme_dict(self):
        scheme_mock = {'database': {'name': 'accounts_db', 'tables': {'accounts': {'columns': [{'name': 'id', 'type': 'INTEGER', 'primary_key': True}, {'name': 'short_name', 'type': 'TEXT'}, {'name': 'provider', 'type': 'TEXT'}, {'name': 'active', 'type': 'INTEGER'}, {'name': 'change_date', 'type': 'TEXT'}]}, 'securities': {'columns': [{'name': 'sec_id', 'type': 'INTEGER', 'primary_key': True}, {'name': 'short_name', 'type': 'TEXT'}, {'name': 'full_name', 'type': 'TEXT'}, {'name': 'type', 'type': 'TEXT'}, {'name': 'subtype', 'type': 'TEXT'}]}, 'transactions': {'columns': [{'name': 'tr_id', 'type': 'INTEGER', 'primary_key': True}, {'name': 'sec_id', 'type': 'INTEGER'}, {'name': 'acc_id', 'type': 'INTEGER'}, {'name': 'date', 'type': 'TEXT'}, {'name': 'type', 'type': 'TEXT'}, {'name': 'quantity', 'type': 'INTEGER'}, {'name': 'unit_price', 'type': 'REAL'}, {'name': 'total_price', 'type': 'REAL'}, {'name': 'costs', 'type': 'REAL'}, {'name': 'currency', 'type': 'TEXT'}]}, 'fx_rates': {'columns': [{'name': 'nominator', 'type': 'TEXT'}, {'name': 'denominator', 'type': 'TEXT'}, {'name': 'rate', 'type': 'REAL'}, {'name': 'date', 'type': 'TEXT'}, {'name': 'source', 'type': 'TEXT'}, {'name': 'entry_date', 'type': 'TEXT'}]}, 'prices': {'columns': [{'name': 'sec_id', 'type': 'INTEGER'}, {'name': 'date', 'type': 'TEXT'}, {'name': 'unit_price', 'type': 'REAL'}, {'name': 'source', 'type': 'TEXT'}, {'name': 'entry_date', 'type': 'TEXT'}]}, 'holdings': {'columns': [{'name': 'acc_id', 'type': 'INTEGER'}, {'name': 'sec_id', 'type': 'INTEGER'}, {'name': 'account', 'type': 'TEXT'}, {'name': 'security', 'type': 'TEXT'}, {'name': 'date', 'type': 'TEXT'}, {'name': 'type', 'type': 'TEXT'}, {'name': 'subtype', 'type': 'TEXT'}, {'name': 'quantity', 'type': 'INTEGER'}, {'name': 'unit_price', 'type': 'REAL'}, {'name': 'total_price', 'type': 'REAL'}]}}}}
        self.session_mgr.create_tables_from_scheme_dict(scheme_mock)
        expected_calls = []
        for table, columns in scheme_mock['database']['tables'].items():
            expected_calls.append(call(table, columns['columns']))
        self.session_mgr.db_manager.create_table.assert_has_calls(expected_calls)

    @patch("tools.request_builder.SessionManager.create_tables_from_scheme_dict")
    @patch("tools.request_builder.SessionManager.db_scheme")
    def test_initiate_db(self, db_scheme_mock, create_tables_mock):
        scheme_dict_mock = "scheme_dict_mock"
        db_scheme_mock.return_value = scheme_dict_mock
        self.session_mgr.initiate_db()
        db_scheme_mock.assert_called_with(self.session_mgr.default_db_config)
        create_tables_mock.assert_called_with(scheme_dict_mock)

    def test_add_entry(self):
        now = datetime.datetime.now()
        timestamp = now.isoformat()
        self.session_mgr.db_manager.to_dbtime.return_value = timestamp
        kwargs = {"val1": "value", "val2": 11, "val3": 35.59, "val4": "blah", "val5": False}
        type = "transactions"
        expected_tbl_name = self.session_mgr.tables[type]
        expected_values = [val for val in kwargs.values()]
        expected_columns = [col for col in kwargs.keys()]
        self.session_mgr.add_entry(type, kwargs)
        self.session_mgr.db_manager.update_table.assert_called_with(expected_tbl_name, expected_values, expected_columns)

    def test_add_entry_autotimestampp(self):
        now = datetime.datetime.now()
        timestamp = now.isoformat()
        self.session_mgr.db_manager.to_dbtime.return_value = timestamp
        kwargs = {"val1": "value", "val2": 11, "val3": 35.59, "val4": "blah", "val5": False}
        type = "transactions"
        expected_tbl_name = self.session_mgr.tables[type]
        expected_values = [val for val in kwargs.values()] + [timestamp]
        timestamp_col = ["change_time"]
        expected_columns = [col for col in kwargs.keys()] + timestamp_col
        self.session_mgr.add_entry(type, kwargs, timestamp_col)
        self.session_mgr.db_manager.to_dbtime.assert_any_call()
        self.session_mgr.db_manager.update_table.assert_called_with(expected_tbl_name, expected_values, expected_columns)

    def test_update_positions(self):
        input_id = 1
        input_filter = {'acc_id': 1}
        date = datetime.datetime(2024, 6, 1)
        mock_transactions_dict = data = {
            'tr_id': [1, 2, 3, 4, 5, 6],
            'sec_id': [11, 11, 102, 103, 102, 11],
            'acc_id': [1, 1, 1, 1, 1, 1],
            'date': ['2023-01-10', '2023-02-15', '2023-03-20', '2023-04-25', '2023-05-30', '2023-06-15'],
            'type': ['buy', 'buy', 'buy', 'buy', 'buy', 'sell'],
            'quantity': [10, 20, 5, 15, 10, -25],
            'unit_price': [100.0, 105.0, 110.0, 115.0, 120.0, 125.0],
            'total_price': [1000.0, 2100.0, 550.0, 1725.0, 1200.0, 3125.0],
            'costs': [10.0, 20.0, 5.0, 15.0, 10.0, 25.0],
            'currency': ['USD', 'USD', 'USD', 'USD', 'USD', 'USD'],
            'recorded_date': ['2023-01-11', '2023-02-16', '2023-03-21', '2023-04-26', '2023-05-31', '2023-06-16']
        }
        mock_transactions_df = pd.DataFrame(mock_transactions_dict)
        expected_dbtime_calls = [call(date)] * 3
        self.session_mgr.db_manager.to_dbtime.return_value = "mock_dbtime"
        expected_update_table_calls = [call(self.session_mgr.tables["positions"], ['mock_dbtime', 1, 11, 5]),
                                       call(self.session_mgr.tables["positions"], ['mock_dbtime', 1, 102, 15]),
                                       call(self.session_mgr.tables["positions"], ['mock_dbtime', 1, 103, 15])]
        self.session_mgr.db_manager.read_table.return_value = mock_transactions_df
        expected_df = pd.DataFrame(mock_transactions_dict)
        self.session_mgr.update_positions(input_id, date)
        self.session_mgr.db_manager.to_dbtime.assert_has_calls(expected_dbtime_calls)
        self.session_mgr.db_manager.read_table.assert_called_with(self.session_mgr.tables["transactions"], filters=input_filter)
        self.session_mgr.db_manager.update_table.assert_has_calls(expected_update_table_calls)

    def test_communicate_table_attributes(self):
        db_return_value = pd.DataFrame({'type': {0: 'table', 1: 'table', 2: 'table', 3: 'table', 4: 'table', 5: 'table', 6: 'table', 7: 'table'},
                                        'name': {0: 'accounts', 1: 'securities', 2: 'transactions', 3: 'fx_rates', 4: 'prices', 5: 'positions', 6: 'holdings', 7: 'types'},
                                        'tbl_name': {0: 'accounts', 1: 'securities', 2: 'transactions', 3: 'fx_rates', 4: 'prices', 5: 'positions', 6: 'holdings', 7: 'types'},
                                        'rootpage': {0: 2, 1: 3, 2: 4, 3: 5, 4: 6, 5: 7, 6: 8, 7: 9},
                                        'sql': {0: 'CREATE TABLE accounts (id INTEGER PRIMARY KEY, short_name TEXT, provider TEXT, active INTEGER, change_date TEXT)', 1: 'CREATE TABLE securities (sec_id INTEGER PRIMARY KEY, isin_or_fx TEXT, short_name TEXT, full_name TEXT, type TEXT, subtype TEXT, recorded_date TEXT)', 2: 'CREATE TABLE transactions (tr_id INTEGER PRIMARY KEY, sec_id INTEGER, acc_id INTEGER, date TEXT, type TEXT, quantity INTEGER, unit_price REAL, total_price REAL, costs REAL, currency TEXT, recorded_date TEXT)', 3: 'CREATE TABLE fx_rates (nominator TEXT, denominator TEXT, rate REAL, date TEXT, source TEXT, entry_date TEXT)', 4: 'CREATE TABLE prices (sec_id INTEGER, date TEXT, unit_price REAL, source TEXT, entry_date TEXT)', 5: 'CREATE TABLE positions (date TEXT, acc_id INTEGER, sec_id INTEGER, quantity INTEGER)', 6: 'CREATE TABLE holdings (acc_id INTEGER, sec_id INTEGER, account TEXT, security TEXT, date TEXT, type TEXT, subtype TEXT, quantity INTEGER, unit_price REAL, total_price REAL)', 7: 'CREATE TABLE types (category TEXT, option TEXT)'}, 'tbl_scheme': {0: 'id INTEGER PRIMARY KEY, short_name TEXT, provider TEXT, active INTEGER, change_date TEXT', 1: 'sec_id INTEGER PRIMARY KEY, isin_or_fx TEXT, short_name TEXT, full_name TEXT, type TEXT, subtype TEXT, recorded_date TEXT', 2: 'tr_id INTEGER PRIMARY KEY, sec_id INTEGER, acc_id INTEGER, date TEXT, type TEXT, quantity INTEGER, unit_price REAL, total_price REAL, costs REAL, currency TEXT, recorded_date TEXT', 3: 'nominator TEXT, denominator TEXT, rate REAL, date TEXT, source TEXT, entry_date TEXT', 4: 'sec_id INTEGER, date TEXT, unit_price REAL, source TEXT, entry_date TEXT', 5: 'date TEXT, acc_id INTEGER, sec_id INTEGER, quantity INTEGER', 6: 'acc_id INTEGER, sec_id INTEGER, account TEXT, security TEXT, date TEXT, type TEXT, subtype TEXT, quantity INTEGER, unit_price REAL, total_price REAL', 7: 'category TEXT, option TEXT'}
                                        })
        self.session_mgr.db_manager.get_table_attributes.return_value = db_return_value
        expected_schema = {'accounts': 'id INTEGER PRIMARY KEY, short_name TEXT, provider TEXT, active INTEGER, change_date TEXT',
                           'securities': 'sec_id INTEGER PRIMARY KEY, isin_or_fx TEXT, short_name TEXT, full_name TEXT, type TEXT, subtype TEXT, recorded_date TEXT',
                           'transactions': 'tr_id INTEGER PRIMARY KEY, sec_id INTEGER, acc_id INTEGER, date TEXT, type TEXT, quantity INTEGER, unit_price REAL, total_price REAL, costs REAL, currency TEXT, recorded_date TEXT',
                           'fx_rates': 'nominator TEXT, denominator TEXT, rate REAL, date TEXT, source TEXT, entry_date TEXT',
                           'prices': 'sec_id INTEGER, date TEXT, unit_price REAL, source TEXT, entry_date TEXT',
                           'positions': 'date TEXT, acc_id INTEGER, sec_id INTEGER, quantity INTEGER',
                           'holdings': 'acc_id INTEGER, sec_id INTEGER, account TEXT, security TEXT, date TEXT, type TEXT, subtype TEXT, quantity INTEGER, unit_price REAL, total_price REAL',
                           'types': 'category TEXT, option TEXT'}
        schema = self.session_mgr.communicate_table_attributes()
        self.assertEqual(schema, expected_schema)
        random_key = random.sample(sorted(expected_schema), 1)[0]
        random_schema = {random_key: expected_schema[random_key]}
        print(f"Random key test on 'communicate_table_attributes': {random_key}")
        specified_table_schema = self.session_mgr.communicate_table_attributes(random_key)
        self.assertEqual(random_schema, specified_table_schema)








if __name__ == '__main__':
    unittest.main()
