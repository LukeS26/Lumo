try:
    import time
    from server.server import Server
    import config.config_variables as config

    lumo_server = Server(room=config.room, mode=config.assistant_mode)

    while True:
        time.sleep(1)
except Exception as e:
    print(e)