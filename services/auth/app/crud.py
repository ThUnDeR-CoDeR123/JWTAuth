from app.schemas import UserCreate, UserUpdate
from app.models import User
from app.database import get_db
from fastapi import Depends,HTTPException
from sqlalchemy.orm import Session


#Create
def CreateUser(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(email=user.email, password=user.password, full_name=user.full_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

#Read
def GetUserById(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


def GetUserByEmail(email: str, db: Session ):
    db_user = db.query(User).filter(User.email == email).first()
    print(db_user.email)
    if db_user.email is None:
        raise HTTPException(status_code=404, detail="User not found")
        
    return db_user

#Update
def UdateUser(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in user.dict(exclude_unset=True).items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)

    return db_user

#Delete
def DeleteUser(user_id: int, db: Session = Depends(get_db)):
    # Fetch the user from the database
    db_user = db.query(User).filter(User.id == user_id).first()
    
    if db_user is None:
        # User not found, raise a 404 error
        raise HTTPException(status_code=404, detail="User not found")
    
    # Delete the user
    db.delete(db_user)
    db.commit()
    
    # Return the deleted user data
    return db_user