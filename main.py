import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Constants
START, MAIN_MENU, MAKE_SALE, ADD_EXPENSE = range(4)
ITEMS = {"Cake": 5000, "Bread": 2000, "Cookies": 3000}

# Temporary storage
user_sales = {}
user_expenses = {}

# Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_sales[user_id] = []
    user_expenses[user_id] = []

    buttons = [["Open Shift"]]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await update.message.reply_text("Welcome to RoyalBakes POS. Tap to begin:", reply_markup=reply_markup)
    return MAIN_MENU

# Main menu
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        ["Make Sale", "Add Expense"],
        ["View Summary", "Close Shift"]
    ]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await update.message.reply_text("Select an option:", reply_markup=reply_markup)
    return MAIN_MENU

# Make sale
async def make_sale(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    item_buttons = [[item] for item in ITEMS.keys()]
    reply_markup = ReplyKeyboardMarkup(item_buttons, resize_keyboard=True)
    await update.message.reply_text("Select item to sell:", reply_markup=reply_markup)
    return MAKE_SALE

async def handle_sale(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    item = update.message.text
    if item in ITEMS:
        user_sales[user_id].append((item, ITEMS[item]))
        await update.message.reply_text(f"{item} sold for {ITEMS[item]} RWF.")
    return await menu(update, context)

# Add expense
async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send the expense name and amount (e.g. Sugar 1500):")
    return ADD_EXPENSE

async def handle_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    try:
        parts = update.message.text.strip().split()
        name = " ".join(parts[:-1])
        amount = int(parts[-1])
        user_expenses[user_id].append((name, amount))
        await update.message.reply_text(f"Added expense: {name} - {amount} RWF")
    except:
        await update.message.reply_text("Format not recognized. Use: Sugar 1500")
    return await menu(update, context)

# Summary
async def view_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    sales = user_sales.get(user_id, [])
    expenses = user_expenses.get(user_id, [])
    sales_total = sum([s[1] for s in sales])
    expense_total = sum([e[1] for e in expenses])
    summary = f"Sales:\n"
    for s in sales:
        summary += f" - {s[0]}: {s[1]} RWF\n"
    summary += f"Total Sales: {sales_total} RWF\n\nExpenses:\n"
    for e in expenses:
        summary += f" - {e[0]}: {e[1]} RWF\n"
    summary += f"Total Expenses: {expense_total} RWF"
    await update.message.reply_text(summary)
    return await menu(update, context)

# Cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Shift closed. Goodbye!")
    return ConversationHandler.END

# Main setup
def main():
    import os
    TOKEN = os.getenv("BOT_TOKEN")  # or paste your token directly for local test
    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU: [
                MessageHandler(filters.Regex("^(Open Shift)$"), menu),
                MessageHandler(filters.Regex("^(Make Sale)$"), make_sale),
                MessageHandler(filters.Regex("^(Add Expense)$"), add_expense),
                MessageHandler(filters.Regex("^(View Summary)$"), view_summary),
                MessageHandler(filters.Regex("^(Close Shift)$"), cancel),
            ],
            MAKE_SALE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_sale)],
            ADD_EXPENSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_expense)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    app.run_polling()

if __name__ == "__main__":
    main()
