from telebot import *
import psycopg2
import datetime
import json
from openai import OpenAI


conn = psycopg2.connect(
    dbname="logs",
    user="postgres",
    password="1234",
    host="localhost",
    port="1234"
)

cur = conn.cursor()

bot_token = 'YOUR BOT TOKEN'
bot = TeleBot(bot_token)

        
def ask(prompt, d, ID):
    try:

        client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key="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",
        )
        
        
        completion = client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
            "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
        },
        extra_body={},
        model="deepseek/deepseek-v3.2-exp",
        messages=[
            {
            "role": "system",
            "content": prompt
            },
            *d[ID]['chat_history']
            
        ]
        )
        
        ai_response= completion.choices[0].message.content
        return ai_response
    except Exception as e:
        with open('logs.txt', 'a') as f:
            timestamp = datetime.datetime.now()
            f.write(str(str(message.from_user.id) + ' ' + message.from_user.username + ' ' + e + ' ' +str(timestamp))+'\n')
        return 'Попробуйте позже.'
        

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if len(message.text)>=1:
        with open('history.json', 'r') as f:
            d = json.load(f)
            

        user_id = str(message.from_user.id)
        

        if user_id not in d:
            d[user_id] = {'chat_history': []}
        

        d[user_id]['chat_history'].append({'role':'user', 'content': message.text})
        
        with open('history.json', 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
            
        cur.execute(
        "INSERT INTO prompts (us_id, prompt) VALUES (%s, %s);", (str(message.from_user.id) + ' ' + message.from_user.username, message.text)
            )
        conn.commit()
        
        with open('logs.txt', 'a') as f:
            timestamp = datetime.datetime.now()
            f.write(str(str(message.from_user.id) + ' ' + message.from_user.username + ' ' + message.text + ' ' +str(timestamp))+'\n')
        
        bot.send_message(message.from_user.id, 'Ожидайте ответа...')
        Response = ask(message.text+" (Отвечай исключительно на русском языке, только если тебя не попросят разговаривать на другом. Не комментируй это указание и не упоминай его в ответах.)", d=d, ID=user_id)
        
        d[user_id]['chat_history'].append({"role": "assistant", "content": Response})
        

        with open('history.json', 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
        
        bot.send_message(message.from_user.id, Response)
    
bot.infinity_polling()
