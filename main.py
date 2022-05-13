import os
from steelseries import ScreenSync
from gui import ScreenSyncApp
from threading import Thread
from logger import Logger

try:
    os.unlink("application.log")
except:
    pass

logger = Logger(7,"application.log")

if __name__ == "__main__":
    logger.info("Starting application")
    ss = ScreenSync(logger)
    t_ss = Thread(target=ss.run, args=())
    t_ss.setDaemon(True)
    t_ss.start()
    app = ScreenSyncApp(ss, logger)
    app.start()