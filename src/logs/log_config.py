import logging

import coloredlogs

FIELD_STYLES = dict(
    asctime=dict(color='green'),
    name=dict(color='blue'),
    filename=dict(color='magenta'),
    pathname=dict(color='magenta'),
    lineno=dict(color='yellow'),
    levelname=dict(color='cyan', bold=True),
    processName=dict(color='green', bold=True),
)
"""Mapping of log format names to default font styles."""

LEVEL_STYLES = dict(
    debug=dict(color='blue'),
    info=dict(color='green'),
    warning=dict(color='yellow'),
    error=dict(color='red'),
    critical=dict(background='red', bold=True),
)

basic_format = '{asctime} - {module:^10} - {name:^15} - {filename}[line:{lineno}] - [{levelname}]: {message}'

basic_format_colored = coloredlogs.ColoredFormatter(
    fmt=basic_format,
    style='{',
    level_styles=LEVEL_STYLES,
    field_styles=FIELD_STYLES
)

n = 0
m = 0


def __console_handle(logger: logging.Logger):
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(basic_format_colored)
    logger.addHandler(console_handler)


def __file_handle(logger, filename):
    file_handler = logging.FileHandler(filename, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter(basic_format, style='{'))
    logger.addHandler(file_handler)
