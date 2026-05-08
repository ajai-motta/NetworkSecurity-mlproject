import os
import sys
import json 
from dotenv import load_dotenv
import psycopg2
from networksecurity.exception.exception import CustomException
import pandas as pd
import numpy as np
from io import StringIO
from networksecurity.logging.logging import logging

from networksecurity.entity.config_entity import DataIngestionConfig
from sklearn.model_selection import train_test_split
from utils.sql_related import connect_to_postgres

