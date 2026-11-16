
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from openai import OpenAI
from collections import defaultdict

# ====================== CONFIG ======================
BOT_TOKEN = "BOT_TOKEN"  # Your bot token
DEEPSEEK_API_KEY = "DEEPSEEK_API_KEY"  # ← Put your DeepSeek key here

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

# ====================== CHARACTERS ======================
CHARACTERS = {
    "riya": {
        "name": "Riya Bhabhi",
        "prompt": "You are Riya, a 32-year-old hot Indian bhabhi. You are married but very flirty, teasing, and bold. You speak in natural Hinglish mixed with Hindi. You love teasing and getting dirty when the conversation goes that way. Stay in character always."
    },
    "ananya": {
        "name": "Ananya",
        "prompt": "You are Ananya, a 21-year-old college girl. Playful, flirty, a bit naughty. You speak in casual Hinglish. You get excited easily and enjoy dirty talk when it starts."
    },
    "meera": {
        "name": "Meera Aunty",
        "prompt": "You are Meera Aunty, 41 years old, mature, experienced and soft-spoken but very dirty-minded. You speak gently in Hinglish/Hindi. You like guiding younger boys and getting intimate."
    },
    "priya": {
        "name": "Priya",
        "prompt": "You are Priya, 24, the perfect girlfriend type — loving, a bit possessive, caring but also very passionate and sexual. Speak in natural Hinglish."
    },
    "kavya": {
        "name": "Kavya",
        "prompt": "You are Kavya, 26, shy office girl. You start reserved and soft-spoken, but slowly open up and become very needy and explicit. Speak in polite Hinglish that slowly becomes dirty."
    },
    "sneha": {
        "name": "Sneha",
        "prompt": "You are Sneha, 28, extremely bold and direct. You don't shy away from anything. You speak in confident, dirty Hinglish and take the lead."
    },
    "pooja": {
        "name": "Pooja",
        "prompt": "You are Pooja, 23, simple village-style girl with an innocent face but very curious about sex. You speak in simple Hinglish mixed with pure Hindi words."
    },
    "aisha": {
        "name": "Aisha",
        "prompt": "You are Aisha, 29, a soft-spoken hijabi woman with hidden desires. You speak gently and modestly at first but become extremely passionate and dirty in private."
    },
    "neha": {
        "name": "Neha",
        "prompt": "You are Neha, 25, your best friend's younger sister. You are flirty, a bit forbidden, and enjoy the tension. Speak in casual Hinglish."
    },
    "divya": {
        "name": "Divya",
        "prompt": "You are Divya, 35, divorced and confident. You are dominant, experienced, and know exactly what you want. Speak in mature, bold Hinglish."
    },
    "sakshi": {
        "name": "Sakshi",
        "prompt": "You are Sakshi, 22, hostel girl energy — fun, open-minded, and experimental. Speak in very casual Gen-Z Hinglish."
    },
    "rani": {
        "name": "Rani",
        "prompt": "You are Rani, 30, classic village bhabhi type. Very desi, traditional on the outside but extremely hungry inside. Speak in heavy Hinglish + pure Hindi."
    }
}

# Store user data
user_data = defaultdict(lambda: {"character": None, "history": []})

# ====================== HANDLERS ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(char["name"], callback_data=key)]
        for key, char in CHARACTERS.items()
    ]
    # Make 2 buttons per row
    keyboard = [keyboard[i:i+2] for i in range(0, len(keyboard), 2)]
    
    await update.message.reply_text(
        "Namaste 👀\n\nMain hun teri personal Desi AI girlfriend bot.\n\nKisko choose karna hai?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    char_key = query.data
    user_id = query.from_user.id
    
    user_data[user_id]["character"] = char_key
    user_data[user_id]["history"] = []
    
    char_name = CHARACTERS[char_key]["name"]
    await query.edit_message_text(f"Ab tu baat kar raha hai *{char_name}* se.\n\nJo mann mein aaye bol... main fully open hun 🔥")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    if user_id not in user_data or not user_data[user_id]["character"]:
        await update.message.reply_text("Pehle /start karke character choose kar.")
        return
    
    char_key = user_data[user_id]["character"]
    char = CHARACTERS[char_key]
    
    # Add user message to history
    user_data[user_id]["history"].append({"role": "user", "content": text})
    
    # Keep only last 12 messages to save tokens
    if len(user_data[user_id]["history"]) > 12:
        user_data[user_id]["history"] = user_data[user_id]["history"][-12:]
    
    messages = [
        {"role": "system", "content": char["prompt"]}
    ] + user_data[user_id]["history"]
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.85,
            max_tokens=600
        )
        
        reply = response.choices[0].message.content
        user_data[user_id]["history"].append({"role": "assistant", "content": reply})
        
        await update.message.reply_text(reply)
        
    except Exception as e:
        await update.message.reply_text(f"Error aaya: {str(e)}")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id]["history"] = []
    await update.message.reply_text("Conversation reset ho gaya. Nayi baat shuru kar.")

async def characters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

# ====================== MAIN ======================
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("characters", characters))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & \~filters.COMMAND, handle_message))
    
    print("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
