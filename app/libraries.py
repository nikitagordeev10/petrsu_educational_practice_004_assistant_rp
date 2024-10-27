from pprint import pprint
import telebot
import telepot
from telegram.ext import Updater, MessageHandler
import time
from wget import download
import os
from os import system
import docx
import io
import pandas as pd
from telebot import types
import re
import pandas as pd
import psycopg2
from contextlib import closing
import psycopg2
from datetime import datetime
import textract
import docx
from docx import Document
import codecs
import re
import json

from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

from config import *