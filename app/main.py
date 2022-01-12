from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange

app = FastAPI()

# Set a class called Post which extends the BaseModel from pydantic.  
# This is to set up our schema to ensure our body of data received in a post request 
# from the client is in the format we expect and doesn't include unwanted data.
class Post(BaseModel):
    title: str
    content: str
    published: bool = True   # Optional field will default to true if not provided by the user
    rating: Optional[int] = None   # Optional field and will default to None if not provided by the user

# Test sample post
my_posts=[{
    "id": 1,
    "title": "title of post 1",
    "content": "content of post 1"
    },
    {
    "id": 2,
    "title": "Favourite foods post 2",
    "content": "I love pizza"
    }
]

### FUNCTIONS
# Find a post
def find_post(id):
    for post in my_posts:
        if post["id"] == id:
            return post


def find_index_post(id):
    for i, post in enumerate(my_posts):
        if post["id"] == id:
            return i   # return the index of the found post


### ROUTES
# Remember, order matters when matching routes
@app.get("/")
def root():
    return {"message": "Welcome to my API"}


# GET all posts
@app.get("/posts")
def get_posts():
    return {"data": my_posts}


# CREATE new post
@app.post("/posts", status_code=status.HTTP_201_CREATED)   # We should send back a 201 status but a 200 was being sent back so we use this to force a sending back of a 201.
# def create_posts(payload: dict = Body(...)):   # This approach will take anything in the body without any schema layout checking.
# Set variable new_post to type of Post setup earlier as a pydantic class.  FastAPI will check it meets our needs or will throw an error.
def create_posts(post: Post):
    post_dict = post.dict()  # This is actually stored as a pydantic model.  Convert to Dict if you need to have data as a dict.
    post_dict["id"] = randrange(0, 10000000)   # Add unique ID for the new post
    my_posts.append(post_dict)    # Append new post with ID to our internal array list
    return {"data": post_dict}    # return a copy of our new post to the user with the ID attached as way of confirmation.


# GET one post by ID
@app.get("/posts/{id}")   # Remember: all params are returned as type string, even if its an integer
def get_post(id: int, response: Response):    # This will use FastAPI to for the ID to an integer so we do not need to manually convert from string to int ourselves.  Also Response for the status code response.
    post = find_post(id)
    if not post:
        # response.status_code = status.HTTP_404_NOT_FOUND   # We are setting the status code ourselves to send back.  Using status method imported from FastAPI for easier lookup.
        # return {"message": f"post with id: {id} was not found"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")  # This way means lines above not needed and response passed into function not needed.
    return {"post by ID": post}


# DELETE one post by ID
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)   # 204 to say item deleted ok
def delete_post(id: int):
    # Find the index position of the array element in the array with the matching ID
    index = find_index_post(id)

    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")  # Raise a 404 if post not found

    my_posts.pop(index)   # Remove from the post array
    return Response(status_code=status.HTTP_204_NO_CONTENT)   # You should not send any data back for a DELETE, as a 204 just wants to send back the status code only.


# UPDATE one post by ID
@app.put("/posts/{id}")
def update_post(id: int, post: Post):   # Makes sure the request comes in with the right schema layout as defined in class Post
    # Find the index position of the array element in the array with the matching ID
    index = find_index_post(id)

    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")  # Raise a 404 if post not found

    post_dict = post.dict()  # This is actually stored as a pydantic model.  Convert to Dict if you need to have data as a dict.
    post_dict["id"] = id   # Add id to the post_dict
    my_posts[index] = post_dict
    return{"data": post_dict}