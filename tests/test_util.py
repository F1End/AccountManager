import unittest
from unittest.mock import Mock, MagicMock, patch, call

from streamlit.testing.v1 import AppTest

from tools import util

# def test_st_state_changer():
#     app = AppTest.from_file("tools.util.py")
#     app.session_state["mystate"] == False
#     # app.run()
#     util.st_state_changer("mystate")
#     assert app.session_state["mystate"] == True
#
class TestUtil(unittest.TestCase):

    @patch("st.session_state")
    def test_st_state_changer(self, streamlit_mock):
        streamlit_mock.session_state.__getitem__.side_effect = {"mystate": False}
        state_mock = "mystate"
        util.st_state_changer(state_mock)
        assert state_mock[state_mock] == True

# mocked_session_state = MagicMock()
# def test_st_state_changer():
#     with patch("app.session_state") as mocked_session_state:
#         at = AppTest.from_file("tools.util.py")
