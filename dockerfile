# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Expose port 3000 for the Flask app
EXPOSE 5000

# Set the Flask app to run when the container launches
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV REUNION_DB=mongodb+srv://saipraveenkondapalli0:0Ul0zHoeuB87yxgL@cluster0.v80uxg8.mongodb.net/reunion?retryWrites=true
ENV SECRET_KEY=QAZSDFeWQbGtwqQPOTZx
# Run the Flask app when the container launches

RUN pytest -v


# Run the Flask app when the container launches
CMD ["flask", "run"]




