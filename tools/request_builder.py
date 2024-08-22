"""File that sticks together other components"""
import os
import yaml
import logging
from typing import Optional
import sqlite3
import datetime

import pandas as pd

from tools import dbtools


class SessionManager:
    def __init__(self, db_path: Optional[os.path] = None, init_db_manager: bool = True) -> None:
        self.default_db_config = os.path.join("config", "default_db.yaml")
        self.default_db_name = "accounts"
        self.default_db_path = "db"
        self.tables = {"accounts": "accounts",
                       "securities": "securities",
                       "transactions": "transactions",
                       "holdings": "holdings",
                       "positions": "positions",
                       "prices": "prices",
                       "aggregates": "aggregates",
                       "fx_rates": "fx_rates",
                       "types": "types"
                       }
        self.db_path = self.default_db_path if db_path else os.path.join(self.default_db_path,
                                                                         self.default_db_name)
        self.db_manager = dbtools.dbManager(self.db_path) if init_db_manager else None
        # self.db_manager = dbmanager_instance

    def initiate_db(self, db_path: Optional[str] = None, db_scheme: Optional[dict] = None) -> None:
        if not self.db_manager or (self.db_path != db_path and db_path):
            self.db_path = db_path if db_path else self.db_path
            self.db_manager = dbtools.dbManager(self.db_path)
        scheme_dict = self.db_scheme(db_scheme) if db_scheme\
            else self.db_scheme(self.default_db_config)
        self.create_tables_from_scheme_dict(scheme_dict)

    def db_scheme(self, db_scheme_path: Optional[os.path] = None) -> dict:
        if not db_scheme_path:
            db_scheme_path = self.default_db_config
        with open(db_scheme_path) as file:
            schema = yaml.safe_load(file)
        return schema

    def create_tables_from_scheme_dict(self, scheme_dict: dict) -> bool:
        for table, columns in scheme_dict['database']['tables'].items():
            self.db_manager.create_table(table, columns['columns'])

    def add_entry(self, type: str, kwargs: dict, auto_timestamp_col: Optional[str] = None) -> None:
        table_name = self.tables[type]
        columns = [col for col in kwargs.keys()]
        values = [val for val in kwargs.values()]
        if auto_timestamp_col:
            timestamp_column = [self.db_manager.to_dbtime()]
            columns += auto_timestamp_col
            values += timestamp_column
        self.db_manager.update_table(table_name, values, columns)

    def communicate_table_attributes(self, type: Optional[str] = None) -> dict:
        raw_schema = self.db_manager.get_table_attributes()
        raw_schema["tbl_scheme"] = raw_schema.apply(lambda row: row["sql"][(row["sql"].find("(") + 1):-1], axis=1)
        schema = raw_schema[["tbl_name", "tbl_scheme"]].copy()
        if type:
            table_name = self.tables[type]
            schema = schema.loc[schema["tbl_name"] == table_name]
        schema = {key: value for d in schema.set_index("tbl_name").to_dict().values() for key, value in d.items()}
        return schema

    def list_of_tables_in_db(self) -> list:
        scheme_dict = self.communicate_table_attributes()
        return [key for key in scheme_dict.keys()]

    def update_positions(self, acc_id: int, for_date: datetime,
                         from_transaction_date: Optional[datetime] = None,
                         from_latest_holding: Optional[datetime] = None):
        table = self.tables["transactions"]
        filters = {"acc_id": acc_id}
        if from_transaction_date:
            filters["date"] = dbtools.dbManager.to_dbtime(from_transaction_date)
        transactions = self.db_manager.read_table(table, filters=filters)
        aggregated = transactions.groupby('sec_id').agg({'quantity': 'sum'}).reset_index()
        for index, row in aggregated.iterrows():
            values = [self.db_manager.to_dbtime(for_date), acc_id, int(row['sec_id']), int(row["quantity"])]
            self.db_manager.update_table(self.tables["positions"], values)

    def read(self, table: str, columns: Optional[list] = None, filters: Optional[dict] = None) -> pd.DataFrame:
        df = self.db_manager.read_table(table=table, columns=columns, filters=filters)
        return df

    def generate_summary(self) -> pd.DataFrame:
        raise NotImplemented

    def generate_chart(self):
        raise NotImplemented

    def browse_data(self) -> pd.DataFrame:
        raise NotImplemented

    def get_closest_price(self):
        raise NotImplemented

    def add_sec_info(self):
        raise NotImplemented

    def aggregate_accounts(self, date, account):
        raise NotImplemented
        # collect open positions
        # get prices
        # get FX rates
        # aggregate

    def get_holdings(self, date: datetime.datetime) -> pd.DataFrame:
        raise NotImplemented

    def insert_custom_value(self):
        raise NotImplemented

    def generate_chart(self):
        raise NotImplemented

    def set_db(self):
        raise NotImplemented

    def filter_df(self, input_df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplemented
