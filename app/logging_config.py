import logging


def setup(logging_format: str, logging_level: str = 'INFO'):
    logging.basicConfig(
        format=logging_format,
        level=logging_level
    )
