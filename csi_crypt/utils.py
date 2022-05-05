from functools import wraps
import os
import logging
logger = logging.getLogger("utils")


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


def env_required(env_var_name: str):
    try:
        env_var = os.environ[env_var_name]
        logger.debug(f"{env_var_name}={env_var}")
        return env_var
    except KeyError as e:
        logger.error(f"{e.args[0]} environment variable not set")
        raise SystemExit
