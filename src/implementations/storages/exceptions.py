__all__ = ["NotFoundError", "AlreadyExistsError"]


class NotFoundError(Exception):
    pass


class AlreadyExistsError(Exception):
    pass
