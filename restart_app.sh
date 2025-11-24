#!/bin/bash
pkill -f "streamlit run app.py"
sleep 1
python3 -m streamlit run app.py
