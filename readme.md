##Reunion Social API Assignment
##Description
This project is an API assignment for `Backend Engineer` role, built using Python and Flask as the backend technology, and MongoDB as the database. The MongoDB is hosted in the cloud (MongoDB Atlas) for simplicity.

## Tech Stack
* Backend: `Python, Flask`
* Database: `MongoDB` Framework: `Flask-mongoengine`
* Testing Framework: `Pytest`
* Hosting Service: `Vercel`


## Docker Instructions
* Install Docker if you don't have it already
* Clone the repo
* Run `docker build -t reunion/assignment .` in the root directory
* we are using name `reunion/assignment` for the image, you can change it to whatever you want
* Run `docker run -p 5000:5000 reunion/assignment` to run the image on port `5000`
* you can stop the docker container by running `docker stop <container_id>`
* you the get the container id by running `docker ps`

## Testing Instructions
* Go to the root directory of the project, if you are using docker, run `docker run -it reunion/assignment bash` to get into the container
* Run `pytest -v` to run the tests