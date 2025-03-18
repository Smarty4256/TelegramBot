
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from telegram.ext import ContextTypes

TOKEN = "8080648791:AAESxWpgoQoLpRQSTGeOEnGyeqVi4Hnvhcc"
# Store active users
waiting_users = []
chat_pairs = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.chat_id
    if user_id in chat_pairs:
        await update.message.reply_text("You are already in a chat! Use /stop to exit.")      
    else:
        await update.message.reply_text("Welcome! Type /find to start chatting.")

async def find(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.chat_id
    if user_id in chat_pairs:
        await update.message.reply_text("You are already in a chat!")
        return

    if waiting_users:
        partner_id = waiting_users.pop(0)
        chat_pairs[user_id] = partner_id
        chat_pairs[partner_id] = user_id
        await context.bot.send_message(partner_id, "🎉 You have been connected! Start chatting.")
        await update.message.reply_text("🎉 You have been connected! Start chatting.")        
    else:
        waiting_users.append(user_id)
        await update.message.reply_text("Waiting for a partner...")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.chat_id
    if user_id in chat_pairs:
        partner_id = chat_pairs.pop(user_id)
        chat_pairs.pop(partner_id, None)
        await context.bot.send_message(partner_id, "Chat ended. Type /find to chat again.")   
        await update.message.reply_text("Chat ended. Type /find to chat again.")
    elif user_id in waiting_users:
        waiting_users.remove(user_id)
        await update.message.reply_text("You have left the queue.")
    else:
        await update.message.reply_text("You are not in a chat.")
        
async def next(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.chat_id
    if user_id in chat_pairs:
        partner_id = chat_pairs.pop(user_id)
        chat_pairs.pop(partner_id, None)
        await context.bot.send_message(partner_id, "Your partner left. Finding a new one...")
        await find(update, context)  # Automatically search for a new partner
    else:
        await update.message.reply_text("You're not in a chat. Use /find to start.")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.chat_id
    if user_id in chat_pairs:
        partner_id = chat_pairs[user_id]
        await context.bot.send_message(partner_id, update.message.text)

# Create the bot application
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("find", find))
app.add_handler(CommandHandler("stop", stop))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

# Run the bot
print("Bot is running...")
app.run_polling()
