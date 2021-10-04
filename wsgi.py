#!/usr/bin/python3

from index import app
import logging

if __name__ == "__main__":
    handler = logging.FileHandler('/var/log/size-adviser.error.log')
    handler.setLevel(logging.ERROR)
    app.logger.addHandler(handler)
        app.run()
