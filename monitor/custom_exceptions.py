class RechargeException(Exception):
    pass


class TokenInvalidError(RechargeException):
    pass


class TokenExpireError(RechargeException):
    pass
