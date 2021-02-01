import json
class Config():
    def __init__(self):
        self.load_config()
        
    def load_config(self):
            with open('config.json') as f:
                self.config =  json.load(f)

