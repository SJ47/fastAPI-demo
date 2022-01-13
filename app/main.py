import os
from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body

from pydantic import BaseModel
from random import randrange

import psycopg
from psycopg import cursor
from psycopg.rows import dict_row   # Used to return the column headers and convert rows to dicts

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# Set a class called Post which extends the BaseModel from pydantic.  
# This is to set up our schema to ensure our body of data received in a post request 
# from the client is in the format we expect and doesn't include unwanted data.
class Post(BaseModel):
    title: str
    content: str
    published: bool = True   # Optional field will default to true if not provided by the user
    # rating: Optional[int] = None   # Optional field and will default to None if not provided by the user


try:
    # Load up env variables
    HOST=os.getenv("HOST")
    DBNAME=os.getenv("DBNAME")
    DBUSER=os.getenv("DBUSER")  # Using DBUSER instead of USER and USER uses the USER variable in the system environment (the logged in user to the OS)
    PASSWORD=os.getenv("PASSWORD")

    # Setup database connection 
    conn = psycopg.connect(host=HOST, dbname=DBNAME, user=DBUSER, password=PASSWORD, row_factory=dict_row)
    cursor = conn.cursor()
    print("Database connection was successfull!")
    
except Exception as error:
    print("Connecting to database failed")
    print("Error: ", error)


### ROUTES
# Remember, order matters when matching routes
@app.get("/")
def root():
    return {"message": "Welcome to my API"}


# GET all posts
@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    return {"data": posts}


# CREATE new post
@app.post("/posts", status_code=status.HTTP_201_CREATED)   # We should send back a 201 status but a 200 was being sent back so we use this to force a sending back of a 201.
def create_posts(post: Post):
    cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, (post.title, post.content, post.published))  # Remember to do this approach so as not to be open to SQL injection hijacking
    new_post = cursor.fetchone()  # Gets what is returned from the execute statement above
    conn.commit()   # Saves the data into your database
    
    return {"data": new_post}    # return a copy of our new post to the user with the ID attached as way of confirmation.


# GET one post by ID
@app.get("/posts/{id}")   # Remember: all params are returned as type string, even if its an integer
def get_post(id: int):    # This will use FastAPI to for the ID to an integer so we do not need to manually convert from string to int ourselves.  Also Response for the status code response.
    cursor.execute("""SELECT * FROM posts WHERE id = %s """, (str(id),))  # Remember to pass in directly, but use %s and pass in ID to stop SQL injection also cast to string for it to work.  Also the comma after str(id) stops an error??
    post = cursor.fetchone()   # Grab the post found by ID
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")  # This way means lines above not needed and response passed into function not needed.
    
    return {"post by ID": post}


# DELETE one post by ID
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)   # 204 to say item deleted ok
def delete_post(id: int):
    cursor.execute(""" DELETE FROM posts WHERE id = %s RETURNING * """ , (str(id),))
    deleted_post = cursor.fetchone()
    conn.commit()

    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")  # Raise a 404 if post not found

    return Response(status_code=status.HTTP_204_NO_CONTENT)   # You should not send any data back for a DELETE, as a 204 just wants to send back the status code only.


# UPDATE one post by ID
@app.put("/posts/{id}")
def update_post(id: int, post: Post):   # Makes sure the request comes in with the right schema layout as defined in class Post
    cursor.execute(""" UPDATE posts SET title = %s, content = %s, published = %s  WHERE id = %s RETURNING * """, (post.title, post.content, post.published, str(id)))
    updated_post = cursor.fetchone()
    conn.commit()

    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")  # Raise a 404 if post not found

    return{"data": updated_post}