#region Bad god logger
from abc import ABC, abstractmethod
from collections import deque
from enum import IntEnum


class LogLevel(IntEnum):
    DEBUG = 1
    INFO = 2
    WARN = 3
    ERROR = 4

#region
class BadGodLogger:
    def log(self, message: str, log_level: LogLevel) -> None:
        formatted_message = f"[{log_level.name}] {message}"

        # stdout logging
        print(formatted_message)

        # File logging
        with open("log.txt", "a") as log_file: # 'a' means append mode
            log_file.write(formatted_message)

        # Imagine 3rd logger and 4th logger and so on...

def bad_main() -> None:
    logger = BadGodLogger()

    logger.log("First message", LogLevel.INFO)
    logger.log("second message", LogLevel.INFO)
#endregion

#region Improved logger but verbose
class ILogger(ABC):
    @abstractmethod
    def log(self, message: str, log_level: LogLevel) -> None:
        pass

class StdoutLogger(ILogger):
    def log(self, message: str, log_level: LogLevel) -> None:
        print(f"[{log_level.name}] {message}")

class FileLogger(ILogger):
    def log(self, message: str, log_level: LogLevel) -> None: 
        with open("log.txt", "a") as log_file: # 'a' means append mode
            log_file.write(f"[{log_level.name}] {message}")

class DatabaseLogger(ILogger):
    def log(self, message: str, log_level: LogLevel) -> None: 
        pass

def improved_main() -> None:
    loggers: list[ILogger] = [StdoutLogger(), FileLogger()]

    for logger in loggers:
        logger.log("First message", LogLevel.INFO)

    for logger in loggers:
        logger.log("Second message", LogLevel.INFO)
#endregion

#region Good logger using Composite design pattern
class ForEachLogger(ILogger): # The Composite implementation of the interface
    def __init__(self, *loggers: ILogger) -> None:
        self.__loggers = loggers

    def log(self, message: str, log_level: LogLevel) -> None: 
        for logger in self.__loggers:
            logger.log(message, log_level)

class HotColdLogger(ILogger): # Important logs go to how path, others to cold path
    def __init__(self, hot_path_logger: ILogger, cold_path_logger: ILogger) -> None:
        self.__hot_path_logger = hot_path_logger
        self.__cold_path_logger = cold_path_logger

    def log(self, message: str, log_level: LogLevel) -> None: 
        if log_level.value >= LogLevel.WARN.value:
            self.__hot_path_logger.log(message, log_level)
        else:
            self.__cold_path_logger.log(message, log_level)

def good_main() -> None:
    logger = HotColdLogger(
        hot_path_logger=ForEachLogger(
            StdoutLogger(),
            FileLogger()
        ),
        cold_path_logger=ForEachLogger(
            StdoutLogger(),
            FileLogger(),
            DatabaseLogger()
        )
    )

    logger.log("First message", LogLevel.INFO)
    logger.log("second message", LogLevel.INFO)
#endregion
