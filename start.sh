#!/bin/bash
# 1. Start the FastAPI backend in the background
# The '&' at the end is what allows it to run while we start the next thing
uvicorn app.api.main:app --host 0.0.0.0 --port 8000 &

# 2. Start the Streamlit frontend
# We use port 7860 because that is what Hugging Face expects
streamlit run frontend/streamlit_app.py --server.port 7860 --server.address 0.0.0.0