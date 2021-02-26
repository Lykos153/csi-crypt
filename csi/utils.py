from functools import wraps


def log_request_and_reply(f: callable=None, fields: list[str]=[]):
    def _decorate(f):
        @wraps(f)
        def logging_wrapper(self, *args, **kwargs):
            self.logger.debug(f"Received request: {f.__name__}\n{args[0]}")
            # for field in fields:
            #     self.logger.debug("{}: {}".format(field, getattr(args[0], field, "[not found]")))
            reply = f(self, *args, **kwargs)
            self.logger.debug(f"Replying:\n{reply}")
            return reply

        return logging_wrapper

    if f:
        return _decorate(f)
    else:
        return _decorate

