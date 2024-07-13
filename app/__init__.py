'''
creates flask server and initializes the data ingestor and task runner
'''
from os import environ
from flask import Flask
from app.data_ingestor import DataIngestor
from app.task_runner import ThreadPool
from app.my_logging import CustomLogging

# if env variables is not set, open server
if 'NO_SERVER' not in environ:
    webserver = Flask(__name__)
    webserver.tasks_runner = ThreadPool()

    webserver.tasks_runner.start()


    webserver.data_ingestor = DataIngestor("./nutrition_activity_obesity_usa_subset.csv")

    webserver.job_counter = 1

    # make the logger an attribute of the webserver instance for easy access
    webserver.my_logger = CustomLogging().get_logger()

    from app import routes
