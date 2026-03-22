from bs4 import BeautifulSoup
import pandas as pd
import requests

class NBAScraping():
    def __init__(self, url):
        self.url = url
        
        self.headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
        }
    
    def extract_data(self):
        ...
    
    def parse_data(self):
        ...
    
    def upload_product(self):
        ...