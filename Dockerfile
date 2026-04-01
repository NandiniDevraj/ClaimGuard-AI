FROM python:3.11

WORKDIR /app

# Install system dependencies for spaCy and NLP
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_lg

# Copy the rest of your code
COPY . .

# IMPORTANT: Convert Windows line endings to Linux (just in case)
RUN sed -i 's/\r$//' start.sh

# Give the container permission to run the script
RUN chmod +x start.sh

# Use the script to launch both apps
CMD ["./start.sh"]