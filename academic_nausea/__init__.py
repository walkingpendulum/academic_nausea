import nltk; nltk.download('stopwords', quiet=True)

from .main import calculate
from .main import process_document
from .main import detect_fraud
from .table import DatabaseHandler
