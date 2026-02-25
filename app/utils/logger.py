import logging
import json

class JsonFormatter(logging.Formatter):
    def format(self, record):
        record_dict = {
            "time": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "name": record.name,
        }
        if record.exc_info:
            record_dict["exception"] = self.formatException(record.exc_info)
        return json.dumps(record_dict)

def get_logger(name=_name_):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger