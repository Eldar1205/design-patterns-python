from abc import ABC, abstractmethod
from typing import Final, Protocol


class HttpRequest:
    pass

class HttpResponse:
    def __init__(self, status_code: int):
        self.status_code: Final[int] = status_code

class IHttpRequestHandler(ABC):
    @abstractmethod
    def handle(self, request: HttpRequest) -> HttpResponse:
        pass

class OkHttpRequestHandler(IHttpRequestHandler):
    def handle(self, request: HttpRequest) -> HttpResponse: 
        return HttpResponse(200)

#region Bad extensions of basic implementation using inheritence
class LoggingOkHttpRequestHandler(OkHttpRequestHandler):
    def handle(self, request: HttpRequest) -> HttpResponse:
        with open("log.txt", "a") as log_file: # 'a' means append mode
            log_file.write("Http request handler begin")
            response = super().handle(request) # super() call invokes OkHttpRequestHandler implementation
            log_file.write("Http request handler end")

        return response

class ExceptionHandlingLoggingOkHttpRequestHandler(LoggingOkHttpRequestHandler):
    def handle(self, request: HttpRequest) -> HttpResponse:
        try:
            return super().handle(request) # super() call invokes LoggingOkHttpRequestHandler implementation
        except:
            return HttpResponse(500)
#endregion

#region Good implementation using Decorator pattern
class LoggerHttpRequestHandlerDecorator(IHttpRequestHandler):
    def __init__(self, inner_implementation: IHttpRequestHandler):
        self.__inner_implementation = inner_implementation

    def handle(self, request: HttpRequest) -> HttpResponse:
        with open("log.txt", "a") as log_file: # 'a' means append mode
            log_file.write("Http request handler begin")
            response = self.__inner_implementation.handle(request) # super() call replaced with self.__inner_implementation
            log_file.write("Http request handler end")

        return response

class ExceptionHandlingHttpRequestHandlerDecorator(IHttpRequestHandler):
    def __init__(self, inner_implementation: IHttpRequestHandler):
        self.__inner_implementation = inner_implementation

    def handle(self, request: HttpRequest) -> HttpResponse:
        try:
            return self.__inner_implementation.handle(request) # super() call replaced with self.__inner_implementation
        except:
            return HttpResponse(500)

def main():
    my_handler = ExceptionHandlingHttpRequestHandlerDecorator(LoggerHttpRequestHandlerDecorator(OkHttpRequestHandler()))
#endregion