# Use an official Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy all necessary files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Streamlit port
EXPOSE 8501

# Command to run your application
CMD ["streamlit", "run", "bhashabridge.py", "--server.port=8501", "--server.address=0.0.0.0"]
