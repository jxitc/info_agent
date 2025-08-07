import openai
import os
api_key = os.getenv('OPENAI_API_KEY')
print(f'OPENAI api_key={api_key}')
client = openai.OpenAI(api_key=api_key)
print('OPENAI api key setup succesfully')
                    
