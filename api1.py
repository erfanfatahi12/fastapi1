import jwt
from enum import unique
from fastapi import FastAPI,HTTPException,status
from fastapi.param_functions import Depends
from fastapi.security import  OAuth2PasswordBearer , OAuth2PasswordRequestForm, oauth2
from passlib.hash import bcrypt
from pydantic.fields import Schema
from tortoise import fields
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model

app = FastAPI()

JWT_SECRET='myjwtsecret'



class User(Model):
    id= fields.IntField(pk=True)
    username=fields.CharField(50,unique=True)
    password_hash=fields.CharField(128)


    def verify_password(self,password):
        return bcrypt.verify(password, self.password_hash)

User_Pydantic=pydantic_model_creator(User, name='User')
UserIn_Pydantic=pydantic_model_creator(User, name='UserIn',exclude_readonly=True)

oauth2_schime = OAuth2PasswordBearer(tokenUrl='token')

async def authenticate_user(username:str,password:str):
    user=await User.get(username=username)
    if not user:
        return False 
    if not user.verify_password(password):
        return False
    return user

@app.post('/api/auth/api_key')
async def generate_token(from_data: OAuth2PasswordRequestForm=Depends()):
    user = await authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='invalid username or password')
    
    user_obj= await User_Pydantic.from_tortoise_orm(user)

    thoken=jwt.encode(user_obj.dict(), JWT_SECRET)
    return{'access_token':thoken,'thoken_tipe':'bearer'}

async def get_user_current(token: str = Depends(oauth2_schime)):
    try:
        payload= jwt.decode(thken,JWT_SECRET,algorithms=['HS256'])
        user = await User.get(id=payload.get('id'))
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='invalid username or password')
    
    return await User_Pydantic.from_tortoise_orm(user)



@app.post('/users',response_model=User_Pydantic)
async def create_user(user:UserIn_Pydantic):
    user_obj=User(username=user.username,password_hash=bcrypt.hash(user.password_hash))
    await user_obj.save()
    return await User_Pydantic.from_tortoise_orm(user_obj)

@app.get('/users/me' , response_model=User_Pydantic)
async def get_user(user:User_Pydantic = Depends(get_user_current)):
    return user

@app.put('/api/users/reset_password')
async def reset_password():
    return None

        
register_tortoise(
    app,
    db_url='sqlite://db.sqlite3',
    modules={'models':['api1']},
    generate_schemas=True,
    add_exception_handlers=True,
        
)
    