import logging
from pprint import pformat

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
debug = logger.debug
info = logger.info
warning = logger.warning