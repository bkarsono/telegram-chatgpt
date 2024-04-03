import os
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

TOKEN: Final = os.getenv('TOKEN')
BOT_USERNAME: Final = '@track_stats_bot'
client = OpenAI(api_key=os.getenv('KEY'))
prompt_list: list[dict] = [{'role': 'system', 'content': 'You are Avatar Aang, the last airbender. I am fire lord Ozai.'},
                           {'role': 'user', 'content': "So you're the avatar."},
                           {'role': 'system', 'content': 'Your reign of terror ends here, Ozai'}]

# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text('Hello! Thanks for chatting with me!')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text('Usage: ')

async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text('Added.')

# Responses
def handle_response(text: str) -> str:
  response: str = get_bot_response(text, prompt_list)
  return response

# Messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
  message_type: str = update.message.chat.type
  text: str = update.message.text
  print(f'User({update.message.chat.id}) in {message_type}: "{text}"')
  if message_type == 'group':
    if BOT_USERNAME in text:
      new_text: str = text.replace(BOT_USERNAME, '').strip()
      response: str = handle_response(new_text)
    else:
      return
  else:
    response: str = handle_response(text)
  print('Bot: ', response)
  await update.message.reply_text(response)

# Util
def get_api_response(prompt: list[dict]) -> str | None:
  text: str | None = None
  try:
    response = client.chat.completions.create(
      model='gpt-3.5-turbo',
      messages=prompt,
    )
    choices: dict = response.choices[0]
    text = choices.message
  except Exception as e:
    print('ERROR:', e)
  return text

def update_list(role: str, message: str, pl: list[dict]):
  pl.append({'role': role, 'content': message})

def create_prompt(message: str, pl: list[dict]) -> list[dict]:
  update_list('user', message, pl)
  return pl

def get_bot_response(message: str, pl: list[dict]) -> str:
  prompt: list[dict] = create_prompt(message, pl)
  bot_response: str = get_api_response(prompt)
  if bot_response:
    update_list('system', bot_response.content, pl)
    print(pl)
    bot_response = bot_response.content
  else:
    bot_response = 'Something went wrong...'
  return bot_response

# Errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
  print(f'Update {update} caused error {context.error}')

# main
def main():
  print('Starting bot...')
  app = Application.builder().token(TOKEN).build()

  # Commands
  app.add_handler(CommandHandler('start', start_command))
  app.add_handler(CommandHandler('help', help_command))
  app.add_handler(CommandHandler('add', add_command))

  # Messages
  app.add_handler(MessageHandler(filters.TEXT, handle_message))

  # Errors
  app.add_error_handler(error)

  print('Polling...')
  app.run_polling(poll_interval=3)

if __name__ == '__main__':
  main()