from telegram.ext import Updater, MessageHandler, Filters
import os

TOKEN = "8544638957:AAEe5Rb9ctd5tjLyuXJPFTRfwKOTPvGGKbc"
ADMIN_ID = 6415960307


TOKEN = os.environ.get("8544638957:AAEe5Rb9ctd5tjLyuXJPFTRfwKOTPvGGKbc")

# ---------------- ADMIN HANDLER ----------------
def admin_handler(update, context):
    user = update.message.from_user

    if user.id != ADMIN_ID:
        return

    # ✅ Admin /start command
    if update.message.text == "/start":
        update.message.reply_text("⭐ Bot is running Successfully")
        return

    # ✅ Admin replying to user
    if not update.message.reply_to_message:
        return

    try:
        ref = update.message.reply_to_message
        text = ref.caption or ref.text

        user_id = int(text.split("🆔 User ID:")[1].split("`")[1])

        if update.message.text:
            context.bot.send_message(chat_id=user_id, text=update.message.text)

        elif update.message.photo:
            context.bot.send_photo(
                chat_id=user_id,
                photo=update.message.photo[-1].file_id,
                caption=update.message.caption
            )

        elif update.message.video:
            context.bot.send_video(
                chat_id=user_id,
                video=update.message.video.file_id,
                caption=update.message.caption
            )

        elif update.message.voice:
            context.bot.send_voice(
                chat_id=user_id,
                voice=update.message.voice.file_id
            )

    except Exception as e:
        update.message.reply_text("❌ User ID read error")

# ---------------- USER HANDLER ----------------
def user_handler(update, context):
    user = update.message.from_user

    if user.id == ADMIN_ID:
        return

    username = f"@{user.username}" if user.username else "Not set"

    header = (
        "📩 New Message\n\n"
        f"👤 Name: {user.first_name}\n"
        f"👁️‍🗨️ User name : {username}\n"
        "🆔 User ID:\n"
        f"`{user.id}`\n\n"
    )

    if update.message.text:
        context.bot.send_message(
            chat_id=ADMIN_ID,
            text=header + "💬 Message:\n" + update.message.text,
            parse_mode="Markdown"
        )

    elif update.message.photo:
        context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=update.message.photo[-1].file_id,
            caption=header + "🖼 Photo",
            parse_mode="Markdown"
        )

    elif update.message.video:
        context.bot.send_video(
            chat_id=ADMIN_ID,
            video=update.message.video.file_id,
            caption=header + "🎥 Video",
            parse_mode="Markdown"
        )

    elif update.message.voice:
        context.bot.send_voice(
            chat_id=ADMIN_ID,
            voice=update.message.voice.file_id,
            caption=header + "🎙 Voice",
            parse_mode="Markdown"
        )

# ---------------- MAIN ----------------
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # 👑 Admin handler first
    dp.add_handler(MessageHandler(
        Filters.user(user_id=ADMIN_ID) &
        (Filters.text | Filters.photo | Filters.video | Filters.voice),
        admin_handler
    ))

    # 👤 User handler
    dp.add_handler(MessageHandler(
        ~Filters.user(user_id=ADMIN_ID) &
        (Filters.text | Filters.photo | Filters.video | Filters.voice),
        user_handler
    ))

    print("🤖 Silent Relay Bot Running...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

