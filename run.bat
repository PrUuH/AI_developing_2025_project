@echo off
setlocal

set PROJECT_DIR=%~dp0
set VENV_DIR=%PROJECT_DIR%.venv


if not exist "%VENV_DIR%" (
    python -m venv "%VENV_DIR%"
)

call "%VENV_DIR%\Scripts\activate.bat"

pip install --upgrade pip
pip install streamlit pandas numpy scikit-learn networkx matplotlib transformers torch requests Pillow

if not exist "%PROJECT_DIR%m_and_a.db" (
    python "%PROJECT_DIR%utils\df_gen.py"
    sqlite3 "%PROJECT_DIR%m_and_a.db" < "%PROJECT_DIR%m_and_a_sqlite_compatible.sql"
)

streamlit run "%PROJECT_DIR%app.py"

pause