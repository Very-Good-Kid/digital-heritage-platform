# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv

load_dotenv()

print("DATABASE_URL from env:", os.environ.get('DATABASE_URL'))

from config import config
print("\nCurrent config database URI:", config['default'].SQLALCHEMY_DATABASE_URI)

from app import app
print("\nApp config database URI:", app.config['SQLALCHEMY_DATABASE_URI'])
