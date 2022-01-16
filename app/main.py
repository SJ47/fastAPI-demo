import os
import psycopg

from typing import Optional, List
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body, Depends
from pydantic import BaseModel
from psycopg import cursor
from psycopg.rows import dict_row  # Used to return the column headers and convert rows to dicts
from sqlalchemy.orm import Session   
from . import models, schemas
from .database import engine, get_db
from dotenv import load_dotenv


load_dotenv()
models.Base.metadata.create_all(bind=engine)  # Actual code that creates our tables using SQLAlchemy
app = FastAPI()


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
@app.get("/posts", response_model=List[schemas.Post])  # We have to import List as we return a list of posts
def get_posts(db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    posts = db.query(models.Post).all()   # Grab all entries in the table.  
    return posts


# CREATE new post
@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)   # We should send back a 201 status but a 200 was being sent back so we use this to force a sending back of a 201.  response_model structures our response data.
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, (post.title, post.content, post.published))  # Remember to do this approach so as not to be open to SQL injection hijacking
    # new_post = cursor.fetchone()  # Gets what is returned from the execute statement above
    # conn.commit()   # Saves the data into your database
    # new_post = models.Post(title=post.title, content=post.content, published=post.published)
    new_post = models.Post(**post.dict())   # This is same as above line, but is useful to unpack from a dictionary in case we have lots of fields rather than typing them all out as above line.
    db.add(new_post)
    db.commit()
    db.refresh(new_post)  # Retrieves the new record just added to our database and put it into our variable new_post (similar to SQL statement RETURNING * so we get our ID and created at DATE)
    return new_post    # return a copy of our new post to the user with the ID attached as way of confirmation.


# GET one post by ID
@app.get("/posts/{id}", response_model=schemas.Post)   # Remember: all params are returned as type string, even if its an integer
def get_post(id: int, db: Session = Depends(get_db)):    # This will use FastAPI to for the ID to an integer so we do not need to manually convert from string to int ourselves.  Also Response for the status code response.
    # cursor.execute("""SELECT * FROM posts WHERE id = %s """, (str(id),))  # Remember to pass in directly, but use %s and pass in ID to stop SQL injection also cast to string for it to work.  Also the comma after str(id) stops an error??
    # post = cursor.fetchone()   # Grab the post found by ID
    post = db.query(models.Post).filter(models.Post.id == id).first()  # find the record with the ID equal to the id passed in by the user.  Similar to the WHERE statement above.

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")  # This way means lines above not needed and response passed into function not needed.
    
    return post


# DELETE one post by ID
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)   # 204 to say item deleted ok
def delete_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute(""" DELETE FROM posts WHERE id = %s RETURNING * """ , (str(id),))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    post = db.query(models.Post).filter(models.Post.id == id)
    
    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")  # Raise a 404 if post not found

    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)   # You should not send any data back for a DELETE, as a 204 just wants to send back the status code only.


# UPDATE one post by ID
@app.put("/posts/{id}", response_model=schemas.Post)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db)):   # Makes sure the request comes in with the right schema layout as defined in class Post
    # cursor.execute(""" UPDATE posts SET title = %s, content = %s, published = %s  WHERE id = %s RETURNING * """, (post.title, post.content, post.published, str(id)))
    # updated_post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)  # Find post with specific id

    post = post_query.first()  # Store that specific found post

    if post == None:  # If it does not exist, throw a 404 error
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")  # Raise a 404 if post not found

    post_query.update(updated_post.dict(), synchronize_session=False)  # unpack from a dictionary to save listing all the columns out manually
    db.commit()  # Commit change to database 
    return post_query.first()   # Grab the found record again with updated fields to return to the client