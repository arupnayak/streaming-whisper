FROM python:3.10-slim-bullseye

# Set the working directory
WORKDIR /

# Copy the current directory contents into the container at /app
COPY ./requirements.txt /requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install -r /requirements.txt

# Copy the current directory contents into the container at /app
COPY . /

# Set the command to run the uvicorn server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]

# expose the port
EXPOSE 80