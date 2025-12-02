#!/bin/bash

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

pip install --upgrade pip
pip install streamlit pandas numpy scikit-learn networkx matplotlib transformers torch requests Pillow

if [ ! -f "$PROJECT_DIR/m_and_a.db" ]; then
    python "$PROJECT_DIR/utils/df_gen.py"
    sqlite3 "$PROJECT_DIR/m_and_a.db" < "$PROJECT_DIR/m_and_a_sqlite_compatible.sql"
fi

streamlit run "$PROJECT_DIR/app.py"