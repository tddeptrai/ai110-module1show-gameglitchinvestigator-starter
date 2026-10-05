# Root-level conftest so pytest puts the project root on sys.path.
# This lets tests import logic_utils, and lets Streamlit's AppTest run app.py
# (which imports logic_utils) without a ModuleNotFoundError.
