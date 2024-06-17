import sys
import os.path as path

from streamlit.web import cli as stcli

from tools import request_builder



if __name__ == '__main__':
    sys.argv = ["streamlit", "run", path.join("tools", "ui_st.py")]
    sys.exit(stcli.main())
    # test = request_builder.SessionManager()
    # test2 = test.db_scheme()
    # print(test2)
