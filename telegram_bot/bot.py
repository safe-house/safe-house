import logging
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

valve_state = True
VALVE = range(1)


def start(update, context):
    reply_keyboard = [['Close Valve', 'Sensors State']]
    update.message.reply_text(
        'Hi!\n\n'
        'This is SafeHouse Bot.\n\n'
        'I will send you notifications in case something happen in your House.',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard))

    return VALVE


def rotate_valve(update, context):
    global valve_state
    if valve_state:
        valve_state = False
        reply_keyboard = [['Open Valve', 'Sensors State']]
        update.message.reply_text('Valve was closed',
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard))
    else:
        valve_state = True
        reply_keyboard = [['Close Valve', 'Sensors State']]
        update.message.reply_text('Valve was opened',
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard))

    return VALVE


def valve_ver(update, context):
    if valve_state:
        reply_keyboard = [['Yes', 'Cancel']]
        update.message.reply_text('Do you really want to close valve?',
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard))
    else:
        reply_keyboard = [['Yes', 'Cancel']]
        update.message.reply_text('Do you really want to open valve?',
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard))

    return VALVE


def cancel(update, context):
    if valve_state:
        reply_keyboard = [['Close Valve', 'Sensors State']]
        update.message.reply_text('Cancelled', reply_markup=ReplyKeyboardMarkup(reply_keyboard))
    else:
        reply_keyboard = [['Open Valve', 'Sensors State']]
        update.message.reply_text('Cancelled', reply_markup=ReplyKeyboardMarkup(reply_keyboard))
    return VALVE


def sensors_state(update, context):
    update.message.reply_text('Kitchen: Good, Last seen: 2 min ago \n\n Bathroom: Good, Last seen: 3 min ago')

    return VALVE


def help(update, context):
    update.message.reply_text(
        'Hi!\n\n'
        'This is SafeHouse Bot.\n\n'
        'I will send you notifications in case something happen in your House.')


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    updater = Updater(token='970539780:AAElJ4Gr1-BBcmBKHAL31yVg-SLYebt8Km8', use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            VALVE: [MessageHandler(Filters.regex('^(Close Valve|Open Valve)$'), valve_ver),
                    MessageHandler(Filters.regex('^(Sensors State)$'), sensors_state),
                    MessageHandler(Filters.regex('^(Yes)$'), rotate_valve),
                    MessageHandler(Filters.regex('^(Cancel)$'), cancel)],

        },

        fallbacks=[CommandHandler('start', start)]
    )
    updater.dispatcher.add_handler(CommandHandler('help', help))
    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()