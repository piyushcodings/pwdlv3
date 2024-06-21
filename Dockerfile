# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# Install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg && apt-get install curl -y

# Create a virtual environment and activate it
RUN python -m venv /opt/venv

# Ensure the virtual environment is used
ENV PATH="/opt/venv/bin:$PATH"

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 7680 available to the world outside this container
EXPOSE 7680

COPY ./defaults.linux.json ./defaults.json

RUN chmod +x ./setup.sh
RUN ./setup.sh
RUN chmod +x ./bin/*


RUN mkdir webdl

# Run gunicorn when the container launches
#RUN python ./beta/api/api.py
#RUN echo "from beta.api.api import app" > ./run.py
#RUN echo "app.run(host='0.0.0.0',port=7680)" >> ./run.py
#CMD ["python", "run.py", "&"]

CMD ["gunicorn", "--workers", "8", "--bind", "0.0.0.0:7680", "app:app"]
