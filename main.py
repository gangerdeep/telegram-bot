import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = "8479220656:AAH-Cu-2fP0xSN_eO4y4EiISCjKk5WsENyE"
ADMIN_ID = 6415960307

users = {}  # {user_id: username}


# ✅ START COMMAND
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # ✅ ADMIN PANEL
    if user.id == ADMIN_ID:
        await update.message.reply_text(
            f"👋🏻 Hello Admin {user.first_name}"
        )
        return

    # ✅ SAVE USER
    users[user.id] = user.username if user.username else "No Username"

    keyboard = [
        [InlineKeyboardButton("🎭 Download Reels", callback_data="reels")],
        [InlineKeyboardButton("✨ Download Thumbnail", callback_data="thumb")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🤖 This bot helps you download Instagram reels and thumbnails\n"
        "🔗 Made by (IG) : sandeep._.op"
    )

    await update.message.reply_text(
        "Select option 👇",
        reply_markup=reply_markup
    )

    # 🔔 Notify Admin
    await context.bot.send_message(
        ADMIN_ID,
        f"🆕 New User Started Bot\n\n"
        f"👤 Name: {user.first_name}\n"
        f"🆔 {user.id}\n"
        f"📛 Username: @{user.username}"
    )


# ✅ BUTTON HANDLER
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["action"] = query.data

    if query.data == "reels":
        msg = await query.message.reply_text("🎭 Send Reel URL:")
    else:
        msg = await query.message.reply_text("✨ Send Thumbnail URL:")

    context.user_data["msg_id"] = msg.message_id
    context.user_data["chat_id"] = msg.chat_id


# ✅ MAIN MESSAGE HANDLER
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message

    # 🔁 FORWARD USER MESSAGE TO ADMIN
    if user.id != ADMIN_ID:
        try:
            await message.forward(ADMIN_ID)
        except:
            pass

    # 🔁 ADMIN REPLY SYSTEM
    if user.id == ADMIN_ID and message.reply_to_message:
        try:
            replied = message.reply_to_message

            if replied.forward_from:
                uid = replied.forward_from.id
            else:
                return

            if message.text:
                await context.bot.send_message(uid, message.text)

            elif message.photo:
                await context.bot.send_photo(
                    uid,
                    message.photo[-1].file_id,
                    caption=message.caption
                )

            elif message.video:
                await context.bot.send_video(
                    uid,
                    message.video.file_id,
                    caption=message.caption
                )

            elif message.animation:
                await context.bot.send_animation(
                    uid,
                    message.animation.file_id,
                    caption=message.caption
                )

            elif message.sticker:
                await context.bot.send_sticker(
                    uid,
                    message.sticker.file_id
                )

        except:
            await message.reply_text("❌ Reply Failed")

        return

    # ✅ CHECK ACTION SELECTED
    action = context.user_data.get("action")
    if not action:
        return

    # ✅ CHECK INSTAGRAM LINK
    text = message.text
    if not text or "instagram.com" not in text:
        await message.reply_text(
            "❌ Please send valid Instagram URL\n"
            "🔗 Send the link after using /start bot in it otherwise an error appear!"
        )
        return

    msg_id = context.user_data.get("msg_id")
    chat_id = context.user_data.get("chat_id")

    api_url = f"https://undress-task-id.vercel.app/?url={text}"

    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg_id,
            text="⏳ Processing..."
        )

        response = requests.get(api_url)
        data = response.json()

        video_url = data.get("video")
        thumb_url = data.get("thumbnail")

        await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)

        if action == "reels" and video_url:
            await message.reply_video(video_url, caption="✅ Reel Downloaded")

        elif action == "thumb" and thumb_url:
            await message.reply_photo(thumb_url, caption="✅ Thumbnail Downloaded")

        else:
            await message.reply_text("❌ Download failed")

    except:
        await message.reply_text("⚠️ Error aaya API se")


# ✅ USER LIST COMMAND
async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not users:
        await update.message.reply_text("❌ No users yet")
        return

    text = "👥 USER LIST\n\n"

    for uid, uname in users.items():
        text += f"👤 @{uname}\n🆔 {uid}\n\n"

    await update.message.reply_text(text)


# ✅ BROADCAST COMMAND
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("Usage: /broadcast Your message")
        return

    msg = " ".join(context.args)

    count = 0
    for uid in users:
        try:
            await context.bot.send_message(uid, msg)
            count += 1
        except:
            pass

    await update.message.reply_text(f"✅ Sent to {count} users")


# ✅ MAIN
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("list", list_users))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_messages))

    print("Bot Running...")
    app.run_polling()


if __name__ == "__main__":
    main()