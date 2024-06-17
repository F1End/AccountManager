import unittest
from unittest.mock import Mock, MagicMock, patch
import os

import pandas as pd

from tools import dbtools


class test_dbManager(unittest.TestCase):

    @patch('sqlite3.connect')
    def setUp(self, connect_mock):
        conn_mock = Mock()
        cursor_mock = Mock()
        conn_mock.cursor.return_value = cursor_mock
        connect_mock.return_value = conn_mock

        self.test_path = os.path.join("my_database.db")
        self.db_manager =  dbtools.dbManager(self.test_path)

        connect_mock.assert_called_with(self.test_path)
        self.assertEqual(self.db_manager.conn, conn_mock)
        self.assertEqual(self.db_manager.cursor, cursor_mock)

    def test_init(self):
        self.assertEqual(self.db_manager.db, self.test_path)

    def test_create_db(self):
        db_name = 'my_db.db'
        self.db_manager.create_db(db_name)

        self.db_manager.cursor.execute.assert_called_with(f'CREATE DATABASE IF NOT EXISTS {db_name}')
        self.db_manager.conn.commit.assert_any_call()

    def test_create_table(self):
        table_name = 'my_table'
        columns = [{"name": "col1", "type": "INTEGER", "primary_key": True},
                   {"name": "col2", "type": "TEXT"},
                   {"name": "col3", "type": "INTEGER"}]
        # expected = f"CREATE TABLE IF NOT EXIST {table_name} " \
        #            "col1 INTEGER PRIMARY KEY, " \
        #            "col2 TEXT, " \
        #            "col3 INTEGER"
        expected_sql = f"CREATE TABLE IF NOT EXISTS {table_name} (col1 INTEGER PRIMARY KEY, col2 TEXT, col3 INTEGER)"
        # expected_iterable = ["col1 INTEGER PRIMARY KEY", "col2 TEXT", "col3 INTEGER"]
        self.db_manager.create_table(table_name, columns)
        self.db_manager.cursor.execute.assert_called_with(expected_sql)
        self.db_manager.conn.commit.assert_any_call()

    def test_check_db(self):
        pass

    def create_table_from_schema(self):
        pass

    def test_update_table(self):
        input = ["val1", "val2", "val3", "val4"]
        table = "my_table"
        # expected = f"""INSERT INTO {table} VALUES ("val1", "val2", "val3", "val4")"""
        expected = f"""INSERT INTO my_table (?,?,?,?)"""
        self.db_manager.update_table(table, input)
        self.db_manager.cursor.execute.assert_called_with(expected, input)
        self.db_manager.conn.commit.assert_any_call()

    def test_update_table_with_cols(self):
        input_val = ["val1", "val2", "val3", "val4"]
        input_cols = ["col1", "col2", "col3", "col4"]
        table = "my_table"
        # expected = f"""INSERT INTO {table} VALUES ("val1", "val2", "val3", "val4")"""
        expected = f"""INSERT INTO my_table(col1, col2, col3, col4) (?,?,?,?)"""
        self.db_manager.update_table(table, input_val, input_cols)
        self.db_manager.cursor.execute.assert_called_with(expected, input_val)
        self.db_manager.conn.commit.assert_any_call()

    # @patch("pandas")
    def test_read_table_no_cols(self):
        table = 'my_table'
        expected_query = f"SELECT * FROM {table}"
        fetch_answer = [("SP500", 5, 511.12, "EUR"),
                        ("N100", 15, 99.41, "USD"),
                        ("D2027/4", 30, 10000.00, "HUF")]
        self.db_manager.cursor.fetchall.return_value = fetch_answer
        self.db_manager.cursor.description = [["Instrument"], ["Quantity"], ["Price"], ["Currency"]]
        columns = ["Instrument", "Quantity", "Price", "Currency"]
        expected_df = pd.DataFrame(fetch_answer, columns=columns)
        df = self.db_manager.read_table(table)
        self.db_manager.cursor.execute.assert_called_with(expected_query, [])
        self.db_manager.cursor.fetchall.assert_any_call()
        pd.testing.assert_frame_equal(expected_df, df)

    def test_read_table_cols(self):
        table = 'my_table'
        columns_input = ["Instrument", "Quantity", "Price", "Currency"]
        expected_query = f"SELECT Instrument, Quantity, Price, Currency FROM {table}"
        fetch_answer = [("SP500", 5, 511.12, "EUR"),
                        ("N100", 15, 99.41, "USD"),
                        ("D2027/4", 30, 10000.00, "HUF")]
        self.db_manager.cursor.fetchall.return_value = fetch_answer
        self.db_manager.cursor.description = [["Instrument"], ["Quantity"], ["Price"], ["Currency"]]
        columns = ["Instrument", "Quantity", "Price", "Currency"]
        expected_df = pd.DataFrame(fetch_answer, columns=columns)
        df = self.db_manager.read_table(table, columns=columns_input)
        self.db_manager.cursor.execute.assert_called_with(expected_query, [])
        self.db_manager.cursor.fetchall.assert_any_call()
        pd.testing.assert_frame_equal(expected_df, df)

    def test_read_table_filters(self):
        table = 'my_table'
        expected_query = f"SELECT * FROM {table} WHERE CURRENCY in(?) AND INSTRUMENT in(?)"
        fetch_answer = [("SP500", 5, 511.12, "EUR"),
                        ("N100", 15, 99.41, "USD"),
                        ("D2027/4", 30, 10000.00, "HUF")]
        self.db_manager.cursor.fetchall.return_value = fetch_answer
        self.db_manager.cursor.description = [["Instrument"], ["Quantity"], ["Price"], ["Currency"]]
        columns = ["Instrument", "Quantity", "Price", "Currency"]
        filter_dict = {"CURRENCY": "USD", "INSTRUMENT": "SP500"}
        expected_df = pd.DataFrame(fetch_answer, columns=columns)
        df = self.db_manager.read_table(table, filters=filter_dict)
        self.db_manager.cursor.execute.assert_called_with(expected_query, ["USD", "SP500"])
        self.db_manager.cursor.fetchall.assert_any_call()
        pd.testing.assert_frame_equal(expected_df, df)

    def test__run_custom_query_commit(self):
        sql = "SELECT * FROM MY TABLE"
        self.db_manager._run_custom_query(sql)
        self.db_manager.cursor.execute.assert_called_with(sql)
        self.db_manager.conn.commit.assert_any_call()

    def test__run_custom_query_fetch(self):
        sql = "SELECT * FROM MY TABLE"
        expected_return = "mock_return"
        self.db_manager.cursor.fetchall.return_value = expected_return
        answer = self.db_manager._run_custom_query(sql, fetch_return=True)
        self.db_manager.cursor.execute.assert_called_with(sql)
        self.db_manager.cursor.fetchall.assert_any_call()
        self.assertEqual(answer, expected_return)

    def test_get_table_attributes(self):
        returned_rows = {"current data": [('table', 'accounts', 'accounts', 2, 'CREATE TABLE   (id INTEGER PRIMARY KEY, short_name TEXT, provider TEXT, active INTEGER, change_date TEXT)'), ('table', 'securities', 'securities', 3, 'CREATE TABLE securities (sec_id INTEGER PRIMARY KEY, isin_or_fx TEXT, short_name TEXT, full_name TEXT, type TEXT, subtype TEXT, recorded_date TEXT)'), ('table', 'transactions', 'transactions', 4, 'CREATE TABLE transactions (tr_id INTEGER PRIMARY KEY, sec_id INTEGER, acc_id INTEGER, date TEXT, type TEXT, quantity INTEGER, unit_price REAL, total_price REAL, costs REAL, currency TEXT, recorded_date TEXT)'), ('table', 'fx_rates', 'fx_rates', 5, 'CREATE TABLE fx_rates (nominator TEXT, denominator TEXT, rate REAL, date TEXT, source TEXT, entry_date TEXT)'), ('table', 'prices', 'prices', 6, 'CREATE TABLE prices (sec_id INTEGER, date TEXT, unit_price REAL, source TEXT, entry_date TEXT)'), ('table', 'positions', 'positions', 7, 'CREATE TABLE positions (date TEXT, acc_id INTEGER, sec_id INTEGER, quantity INTEGER)'), ('table', 'holdings', 'holdings', 8, 'CREATE TABLE holdings (acc_id INTEGER, sec_id INTEGER, account TEXT, security TEXT, date TEXT, type TEXT, subtype TEXT, quantity INTEGER, unit_price REAL, total_price REAL)'), ('table', 'types', 'types', 9, 'CREATE TABLE types (category TEXT, option TEXT)')]}
        returned_headers = (('type', None, None, None, None, None, None), ('name', None, None, None, None, None, None), ('tbl_name', None, None, None, None, None, None), ('rootpage', None, None, None, None, None, None), ('sql', None, None, None, None, None, None))
        self.db_manager.cursor.fetchall.return_value = returned_rows
        self.db_manager.cursor.description = returned_headers
        filtered_headers = [description[0] for description in returned_headers]
        expected_df = pd.DataFrame(returned_rows, columns=filtered_headers)
        answer = self.db_manager.get_table_attributes()
        pd.testing.assert_frame_equal(answer, expected_df)
        self.db_manager.cursor.execute.assert_called_with("SELECT *  FROM sqlite_master")
        self.db_manager.cursor.fetchall.assert_any_call()







if __name__ == '__main__':
    unittest.main()
