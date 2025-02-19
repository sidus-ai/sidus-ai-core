import logging
from logging.handlers import RotatingFileHandler

import sidusai


def build_logging(name: str, filename: str = None, max_bytes: int = 1048576, backup_count: int = 1, level=logging.INFO):
    """
    Build logging object by params
    :param level: Logging level
    :param backup_count: Archive logging
    :param max_bytes: Max log file size. Default 1Mb
    :param filename: log filename
    :param name: Logger name
    :return:
    """

    log = logging.getLogger(name)

    handlers = [logging.StreamHandler()]
    if filename is not None:
        sidusai.utils.make_dir_if_not_exist(filename)

        _log_file_handler = RotatingFileHandler(
            filename=filename,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding=None,
            delay=False,
        )

        handlers.append(_log_file_handler)

    logging.basicConfig(
        level=level,
        handlers=handlers,
    )

    return log
