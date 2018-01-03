import logging
from pprint import pformat
from logging import INFO, DEBUG, WARNING


logging.basicConfig(level=WARNING)
logger = logging.getLogger(__name__)

isEnabledFor = logger.isEnabledFor

debug = logger.debug
info = logger.info
warning = logger.warning
