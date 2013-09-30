class RechargeException(Exception):
    def __init__(self, msg):
        self.msg = msg

        super(RechargeException, self).__init__(msg)


class TokenInvalidError(RechargeException):
    pass


class TokenExpireError(RechargeException):
    pass
