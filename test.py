from lib.message_handler import MessageHandler


if __name__ == "__main__":
    from lib.producer import producer
    BASE_DIR = 'C:\\Users\\isaac\\Desktop\\ALETHEIA\\samaritan'
    message_handler = MessageHandler(BASE_DIR, producer)
    res = message_handler.get_reply("0-GREETA-0")
    print(res)
