# Python imagedocker-compose.yml
FROM python:3.8-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy  current directory contents into the container at /app
COPY requirements.txt /app

# Install packages
RUN pip install -r requirements.txt

# Copy  current directory contents into the container at /app
COPY . /app

# Port
EXPOSE 5000

CMD ["python", "run.py"]
