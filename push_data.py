import os
import sys
import json 
from dotenv import load_dotenv
import psycopg2
from networksecurity.exception.exception import CustomException
import certifi
load_dotenv()
import pandas as pd
import numpy as np
from io import StringIO
from networksecurity.logging.logging import logging

try:
    ca=certifi.where()
    db_host = os.getenv("DB_HOST")
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_port = os.getenv("DB_PORT")
    
except Exception as e:
    raise CustomException(e,sys)

class NetworkDataExtraction:
    def __init__(self):
        try:
          self.conn=psycopg2.connect(
            host=db_host,
            database=db_name,   
            user=db_user,       
            password=db_password,
            port=db_port,
            connect_timeout=5
           )
        except Exception as e:
            raise CustomException(e,sys)
    def csv_to_postgress(self,file_path):
         try:
            cur=self.conn.cursor()
            cur.execute("""
                    CREATE TABLE IF NOT EXISTS phishing_data (
                        having_ip_address INT,
                        url_length INT,
                        shortining_service INT,
                        having_at_symbol INT,
                        double_slash_redirecting INT,
                        prefix_suffix INT,
                        having_sub_domain INT,
                        sslfinal_state INT,
                        domain_registeration_length INT,
                        favicon INT,
                        port INT,
                        https_token INT,
                        request_url INT,
                        url_of_anchor INT,
                        links_in_tags INT,
                        sfh INT,
                        submitting_to_email INT,
                        abnormal_url INT,
                        redirect INT,
                        on_mouseover INT,
                        rightclick INT,
                        popupwidnow INT,
                        iframe INT,
                        age_of_domain INT,
                        dnsrecord INT,
                        web_traffic INT,
                        page_rank INT,
                        google_index INT,
                        links_pointing_to_page INT,
                        statistical_report INT,
                        result INT
                    );
                    """)
            
            buffer = StringIO()
            data=pd.read_csv(file_path)
            data.columns = [col.lower() for col in data.columns]
            data.to_csv(buffer, index=False, header=False)
            buffer.seek(0)
            cur.copy_expert("COPY phishing_data FROM STDIN WITH CSV", buffer)
            self.conn.commit()
            cur.close()
            self.conn.close()
            logging.info("inset complete")
         except Exception as e:
            raise CustomException(e,sys)

if __name__=="__main__":
    try:
        obj1=NetworkDataExtraction()
        obj1.csv_to_postgress(file_path='Network_Data/phisingData.csv')
    
    except Exception as e:
        raise CustomException(e,sys)
    