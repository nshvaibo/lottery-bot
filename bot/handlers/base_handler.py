"""Base handler class used for case specific handlers"""
from telebot.handler_backends import State, StatesGroup


class BaseHandler:
    # States corresponding to this handler
    class States(StatesGroup):
        """Add states in BaseHandler.__init__()"""
        pass
