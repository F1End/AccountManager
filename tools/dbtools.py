"""File for creating and managing db"""
import os
import sqlite3


class dbManager:
    def __init__(self, db_path: os.path) -> None:
        self.db = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def create_db(self, db_path: os.path):
        self.cursor.execute(f"""CREATE DATABASE IF NOT EXISTS {db_path}""")
        self.conn.commit()

    def check_db(self, db_scheme: dict):
        raise NotImplemented

    def read_schema(self):
        raise NotImplemented

    def create_table(self, table_name: str, columns: dict):
        raise NotImplemented

    def create_table_from_schema(self):
        raise NotImplemented

    def update_table(self):
        raise NotImplemented

    def read_table(self):
        raise NotImplemented

    def remove_table(self):
        raise NotImplemented

    def save_db(self):
        raise NotImplemented
