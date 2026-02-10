FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Cache Buster: v2 (This line forces a rebuild)
RUN echo "Installing fresh AI tools..."
COPY . .
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
