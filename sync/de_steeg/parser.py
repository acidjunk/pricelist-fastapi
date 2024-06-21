import structlog

logger = structlog.get_logger(__name__)


class Parser():
    def __init__(self, data):
        self.parsed = False

    def parse(self):
       self.parsed = True