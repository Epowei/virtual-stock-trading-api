import os
import requests
from django.conf import settings

class FinnhubService:
    def __init__(self):
        self.api_key = settings.FINNHUB_API_KEY
        self.base_url = "https://finnhub.io/api/v1"
    
    def get_quote(self, symbol):
        """
        Get real-time quote data for a stock
        """
        endpoint = f"{self.base_url}/quote"
        params = {
            'symbol': symbol.upper(),
            'token': self.api_key
        }
        
        try:
            response = requests.get(endpoint, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error getting quote: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Exception getting quote: {str(e)}")
            return None
    
    def get_company_profile(self, symbol):
        """
        Get general information of a company
        """
        endpoint = f"{self.base_url}/stock/profile2"
        params = {
            'symbol': symbol.upper(),
            'token': self.api_key
        }
        
        try:
            response = requests.get(endpoint, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error getting company profile: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Exception getting company profile: {str(e)}")
            return None