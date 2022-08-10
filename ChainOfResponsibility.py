########################################################################
# FYI, Python's built-in collection ChainMap implements this pattern   #
# https://realpython.com/python-chainmap/                              #
########################################################################

#region God class exception handler with if-elif-else statements
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import IntEnum


#region Infra classes
class LogLevel(IntEnum):
    DEBUG = 1
    INFO = 2
    WARN = 3
    ERROR = 4

class ILogger(ABC):
    @abstractmethod
    def log(self, message: str, log_level: LogLevel) -> None:
        pass

class Logger(ILogger):
    def log(self, message: str, log_level: LogLevel) -> None:
        pass

class IPluginLoader(ABC):
    @abstractmethod
    def try_load_from_plugin(self, module_name: str) -> bool:
        # Try import module from a plugins folder
        pass

class PluginLoader(IPluginLoader):
    def try_load_from_plugin(self, module_name: str) -> bool:
        return True
    
class IGracefulShutdown(ABC):
    @abstractmethod
    def shutdown(self) -> None:
        pass
    
class GracefulShutdown(IGracefulShutdown):
    def shutdown(self) -> None:
        pass
#endregion

class GodExceptionHandler:
    def __init__(self, plugin_loader: IPluginLoader, graceful_shutdown: IGracefulShutdown, logger: ILogger) -> None:
        self.__plugin_loader = plugin_loader
        self.__graceful_shutdown = graceful_shutdown
        self.__logger = logger
    
    def handle_exception(self, ex: BaseException) -> None:
        did_handle = False
        if isinstance(ex, ModuleNotFoundError):
            did_handle = self._handle_module_not_found_error(ex)
        elif isinstance(ex, KeyboardInterrupt):
            did_handle = self._handle_keyboard_interrupt(ex)
        elif isinstance(ex, NotImplementedError):
            did_handle = self._handle_not_implemented_error(ex)
        else:
            did_handle = self._handle_unexpected_exception(ex)
            
        if not did_handle:
            self.__graceful_shutdown.shutdown()
            
    def _handle_module_not_found_error(self, ex: ModuleNotFoundError) -> bool:
        if ex.name is None:
            self.__logger.log(f"ModuleNotFoundError without module name: {ex}", LogLevel.ERROR)
            return False
        
        return self.__plugin_loader.try_load_from_plugin(ex.name)
    
    def _handle_keyboard_interrupt(self, ex: KeyboardInterrupt) -> bool:
        self.__graceful_shutdown.shutdown()
        return True
    
    def _handle_not_implemented_error(self, ex: NotImplementedError) -> bool:
        self.__logger.log(f"NotImplemented error: {ex}", LogLevel.ERROR)
        self.__graceful_shutdown.shutdown()
        return True
    
    def _handle_unexpected_exception(self, ex: BaseException) -> bool:
        self.__logger.log(f"Unexpected exception: {ex}", LogLevel.ERROR)
        self.__graceful_shutdown.shutdown()
        return True
        

def service_logic() -> None:
    # Might raise exceptions
    pass

def bad_main() -> None:
    exception_handler = GodExceptionHandler(PluginLoader(), GracefulShutdown(), Logger())
    try:
        service_logic()
    except BaseException as e:
        exception_handler.handle_exception(e)
#endregion

#region Good exception handling with Chain of Responsibility pattern
@dataclass
class ExceptionHandlingContext:
    exception: BaseException
    is_handled: bool = False

class IExceptionHandler(ABC):
    @abstractmethod
    def handle(self, exception_handling_context: ExceptionHandlingContext) -> None:
        pass

class ModuleNotFoundErrorHandler(IExceptionHandler):
    def __init__(self, plugin_loader: IPluginLoader, logger: ILogger) -> None:
        self.__plugin_loader = plugin_loader
        self.__logger = logger
    
    def handle(self, exception_handling_context: ExceptionHandlingContext) -> None:
        if not isinstance(exception_handling_context.exception, ModuleNotFoundError):
            return
        
        if exception_handling_context.exception.name is None:
            self.__logger.log(f"ModuleNotFoundError without module name: {exception_handling_context.exception}", LogLevel.ERROR)
            return
        
        exception_handling_context.is_handled = self.__plugin_loader.try_load_from_plugin(exception_handling_context.exception.name)
        
class KeyboardInterruptHandler(IExceptionHandler):
    def __init__(self, graceful_shutdown: IGracefulShutdown) -> None:
        self.__graceful_shutdown = graceful_shutdown
    
    def handle(self, exception_handling_context: ExceptionHandlingContext) -> None:
        if not isinstance(exception_handling_context.exception, KeyboardInterrupt):
            return
        
        self.__graceful_shutdown.shutdown()
        exception_handling_context.is_handled = True

class NotImplementedErrorHandler(IExceptionHandler):
    def __init__(self, graceful_shutdown: IGracefulShutdown, logger: ILogger) -> None:
        self.__graceful_shutdown = graceful_shutdown
        self.__logger = logger
    
    def handle(self, exception_handling_context: ExceptionHandlingContext) -> None:
        if not isinstance(exception_handling_context.exception, NotImplementedError):
            return
        
        self.__logger.log(f"NotImplemented error: {exception_handling_context.exception}", LogLevel.ERROR)
        self.__graceful_shutdown.shutdown()
        exception_handling_context.is_handled = True

class UnexpectedExceptionHandler(IExceptionHandler):
    def __init__(self, graceful_shutdown: IGracefulShutdown, logger: ILogger) -> None:
        self.__graceful_shutdown = graceful_shutdown
        self.__logger = logger
    
    def handle(self, exception_handling_context: ExceptionHandlingContext) -> None:        
        self.__logger.log(f"Unexpected exception: {exception_handling_context.exception}", LogLevel.ERROR)
        self.__graceful_shutdown.shutdown()
        exception_handling_context.is_handled = True
        
class ChainExceptionHandler:
    def __init__(self, graceful_shutdown: IGracefulShutdown, *exception_handlers: IExceptionHandler) -> None:
        self.__graceful_shutdown = graceful_shutdown
        self.__exception_handlers = exception_handlers
    
    def handle_exception(self, exception: BaseException) -> None:
        handling_context = ExceptionHandlingContext(exception)
        
        for handler in self.__exception_handlers:
            handler.handle(handling_context)
            
            if handling_context.is_handled:
                break
        else:
            self.__graceful_shutdown.shutdown()

def good_main() -> None:
    graceful_shutdown = GracefulShutdown()
    logger = Logger()
    plugin_loader = PluginLoader()
    exception_handler = ChainExceptionHandler(
        graceful_shutdown,
        ModuleNotFoundErrorHandler(plugin_loader, logger),
        KeyboardInterruptHandler(graceful_shutdown),
        NotImplementedErrorHandler(graceful_shutdown, logger),
        UnexpectedExceptionHandler(graceful_shutdown, logger)
    )
    try:
        service_logic()
    except BaseException as e:
        exception_handler.handle_exception(e)
#endregion
