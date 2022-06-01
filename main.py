from steelseries import ScreenSync
from gui import ScreenSyncApp
from threading import Thread
from logger import Logger

logger = Logger.rotating_file_logger("ScreenSync","application.log")

if __name__ == "__main__":
    logger.info("Starting application")
    ss = ScreenSync(logger)
    t_ss = Thread(target=ss.run, daemon=True, args=())
    t_ss.start()
    app = ScreenSyncApp(ss, logger)
    app.start()