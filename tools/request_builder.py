"""File that sticks together other components"""
import os
import yaml
import logging
from typing import Optional
import sqlite3

from tools import dbtools


class SessionManager:
    def __init__(self, db_path: Optional[os.path] = None) -> None:
        self.default_db_path = os.path.join("config", "default_db.yaml")
        self.default_db_name = "accounts"

    def initiate_db(self, db_name: Optional[str] = None, db_scheme: Optional[dict] = None):
        if not db_name:
            db_name = self.default_db_name
        if not db_scheme:
            db_scheme = self.db_scheme(self.default_db_path)

    def db_scheme(self, db_scheme_path: Optional[os.path] = None) -> dict:
        print(os.getcwd())
        if not db_scheme_path:
            db_scheme_path = self.default_db_path
        with open(db_scheme_path) as file:
            schema = yaml.safe_load(file)
        return schema

# test = SessionManager()
# test2 = test.db_scheme()
# print(test2)

