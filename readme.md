# Reunion Social API Assignment
## Description
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


## API END POINTS
* `/api/authenticate`        - POST - Authenticate a user
* `/api/user`                - GET - Get authenticated user details
* `/api/follow/<id>`         - POST - Follow a user
* `/api/unfollow/<id>`       - POST - Unfollow a user
* `/api/all_posts`           - GET - Get all posts
* `/api/posts`               - POST - Create a post
* `/api/posts/<id>`          - GET - Get a post
* `/api/posts/<id>`          - DELETE - Delete a post
* `/api/like/<id>`           - POST - Like a post
* `/api/unlike/<id>`         - POST - Unlike a post
* `/api/comment/<id>`        - POST - Comment on a post


## Footnotes
* There are 5 DUMMY users in the database you can use any of them to login
:
  * Emails:
      * `john@example.com` 
      * `alice@example.com`
      * `bob@example.com`
      * `mike@example.com`
      * `jane@example.com`
    
      * All of them share the same password `password123`
* There are about 17 Posts preloaded in the database, you can check their details at api endpoint `/api/all_posts`


## Contact Me
* Email: `saipraveenkondapalli@gmail.com`
* website : https://bit.ly/s_p_k


    