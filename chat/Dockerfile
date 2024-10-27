# Base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 

# Set work directory
WORKDIR /code/chat

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Copy and set permissions for start script
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Expose port
EXPOSE 8000

# Start the Django server using the custom script
CMD ["/start.sh"]
