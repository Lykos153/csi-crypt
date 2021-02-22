from functools import wraps


def log_request_and_reply(f: callable=None, fields: list[str]=[]):
    def _decorate(f):
        @wraps(f)
        def logging_wrapper(self, *args, **kwargs):
            self.logger.debug("Received request: {}".format(f.__name__))
            for field in fields:
                self.logger.debug("{}: {}".format(field, getattr(args['request'], field, "[not found]")))
            reply = f(self, *args, **kwargs)
            self.logger.debug("Replying: {}".format(reply))
            return reply

        return logging_wrapper

    if f:
        return _decorate(f)
    else:
        return _decorate

