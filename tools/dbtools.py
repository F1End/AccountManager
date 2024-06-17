"""File for creating and managing db"""
import os
import sqlite3
from typing import Optional
from datetime import datetime

import pandas as pd


class dbManager:
    def __init__(self, db_path: os.path) -> None:
        self.db = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def _run_custom_query(self, sql: str, commit: bool = True, fetch_return: bool = False) -> Optional[tuple]:
        self.cursor.execute(sql)
        if commit:
            self.conn.commit()
        if fetch_return:
            data = self.cursor.fetchall()
            return data

    @staticmethod
    def to_dbtime(self, time: Optional[datetime] = None) -> str:
        if not time:
            time = datetime.now()
        return time.isoformat()

    @staticmethod
    def from_dbtime(self, time: str) -> datetime:
        return datetime.fromisoformat(time)

    def create_db(self, db_path: os.path):
        self.cursor.execute(f"""CREATE DATABASE IF NOT EXISTS {db_path}""")
        self.conn.commit()

    def check_db(self, db_scheme: dict):
        raise NotImplemented

    def create_table(self, table_name: str, columns: list[dict]):
        columns_def = [f"""{col["name"]} {col["type"]}{" PRIMARY KEY" if col.get("primary_key") else ""}""" for col in
                       columns]
        columns_def_str = ", ".join(columns_def)
        sql = f"""CREATE TABLE IF NOT EXISTS {table_name} ({columns_def_str})"""
        self.cursor.execute(sql)
        self.conn.commit()

    def create_db_from_schema(self):
        raise NotImplemented

    def update_table(self, table: str, values: list, cols: Optional[list] = None) -> None:
        columns = f"({', '.join([str(col) for col in cols])})" if cols else ""
        markers = ",".join("?" for val in values)
        sql = f"""INSERT INTO {table}{columns} ({markers})"""
        self.cursor.execute(sql, values)
        self.conn.commit()

    def read_table(self, table: str, columns: Optional[list] = None, filters: Optional[dict] = None) -> pd.DataFrame:
        columns = ', '.join(str(col) for col in columns) if columns else "*"
        sql = f"SELECT {columns} FROM {table}"
        filter_values = []
        if filters and len(filters) > 0:
            filter_columns = [f"{str(key)} in(?)" for key in filters.keys()]
            filter_statement = f" WHERE {(' AND ').join(filter_columns)}"
            sql += filter_statement
            filter_values = [str(val) for val in filters.values()]
        self.cursor.execute(sql, filter_values)
        rows = self.cursor.fetchall()
        header_columns = [description[0] for description in self.cursor.description]
        df = pd.DataFrame(rows, columns=header_columns)
        return df

    def get_table_attributes(self):
        sql = "SELECT *  FROM sqlite_master"
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        header_columns = [description[0] for description in self.cursor.description]
        df = pd.DataFrame(rows, columns=header_columns)
        return df

    def remove_from_table(self):
        raise NotImplemented

    def save_db(self):
        raise NotImplemented
