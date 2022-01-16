from app.database import Base
from pydantic import BaseModel
from datetime import datetime

# Set a class called Post which extends the BaseModel from pydantic.  
# This is to set up our schema to ensure our body of data received in a post request 
# from the client is in the format we expect and doesn't include unwanted data.
# In SQLAlchemy, it will check if the table exists.  If it does, it will do nothing.  If it does not exist, it will create the table.
# Note, that if we amend table properties and the table exists, it will not update those properties in our database if the table already exists.
# For changes to your schema on tables already existing, you should use something called Alembic (or drop the table and recreate it).

# PostBase and PostCreate handle the shape of data send by the user to us
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True   # Optional field will default to true if not provided by the user
    # rating: Optional[int] = None   # Optional field and will default to None if not provided by the user

# Inherit the PostBase class but nothing additional is added
class PostCreate(PostBase):
    pass


# Define what how our response schema should be restricted for sending specific data back to our client
# PostBase and PostCreate handle the shape of data we send back to the user
class Post(PostBase):
    id: int
    created_at: datetime   # Extra validation here to ensure we pass back a valid datetime.  Note to import at top the datetime.

    class Config:   # Required to tell Pydantic to convert the SQLAlchemy model to a Pydantic Model
        orm_mode = True