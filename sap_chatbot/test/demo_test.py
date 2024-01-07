import logging
import unittest

from datetime import datetime

from pojo.message_pojo import MessagePojo
from src.app.app_handler import AppHandler


class MyTestCase(unittest.TestCase):
    message_template = MessagePojo()

    def test_something(self):
        message = self.message_template.to_json()

        message["chunkSize"] = 256
        message["chunkOverlap"] = 32
        message["kValue"] = 3

        logfile = f"./var/log/{datetime.now().strftime('%Y%m%d')}.txt"

        application = AppHandler(message, logfile)
        status = application.main()

        self.assertEqual(status, True)  # add assertion here


if __name__ == '__main__':
    unittest.main()
