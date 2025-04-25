# core/command_bus.py
class CommandBus:
    def __init__(self):
        self._handlers = {}

    def register(self, command_type, handler):
        self._handlers[command_type] = handler

    def handle(self, command):
        handler = self._handlers[type(command)]
        return handler.handle(command)
