import sys,os
import certifi
import psycopg2
from dotenv import load_dotenv
from networksecurity.logging.logging import logging
from networksecurity.exception.exception import CustomException
from networksecurity.utils.read_write import load_object_pkl
from networksecurity.utils.sql_related import connect_to_postgres
load_dotenv()
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI,File,UploadFile,Request
from fastapi.responses import Response
from starlette.responses import RedirectResponse
from uvicorn import run as app_run
import pandas as pd
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="templates")

db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_port = os.getenv("DB_PORT")

# connect to the PostgreSQL database

conn=connect_to_postgres()
app=FastAPI()
origins=["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/",tags=["Authentication"])
async def index():
    return RedirectResponse(url="/docs")

@app.post("/predict",tags=["Prediction"])
async def predict(request:Request,file:UploadFile=File(...)):
    try:
        #contents=await file.read()
        #df=pd.read_csv(StringIO(contents.decode("utf-8")))
        df=pd.read_csv(file.file)
        model=load_object_pkl("final_model/final_model.pkl")
        preprocessor=load_object_pkl("final_model/final_preprocessor.pkl")

        df=preprocessor.transform(df.iloc[:, :-1])
        pred=model.predict(df)
        df=pd.DataFrame(df)
        df["predicted_label"]=pred
        
        table_html=df.to_html(classes="table table-striped")
        print(table_html)
        return templates.TemplateResponse("result.html",{"request":request,"table_html":table_html,"pred":pred})
    except Exception as e:
        raise CustomException(e,sys)

if __name__=="__main__":
    try:
        app_run(app,host="0.0.0",port=8080)
    
    except Exception as e:
        raise CustomException(e,sys)
    