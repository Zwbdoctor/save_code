"""
Exceptions of Task Spider
"""


class NetErrorException(Exception):

    def __init__(self, args):
        self.msg = args

    def __str__(self):
        exception_msg = "Message: %s\n" % self.msg
        return exception_msg

