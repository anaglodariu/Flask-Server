'''
task_runner.py
'''
from queue import Queue
from threading import Thread, Event, Condition
from os import cpu_count, environ, makedirs
import json
from app.my_logging import CustomLogging

class ThreadPool:
    '''
    class that defines a ThreadPool
    '''
    def __init__(self):
        '''
        implement a ThreadPool of TaskRunners
        '''

        # get the value of environment variable TP_NUM_OF_THREADS is defined,
        # otherwise use what the hardware concurrency allows with
        # the cpu_count() function
        self.num_threads = environ.get('TP_NUM_OF_THREADS', cpu_count())

        # declare the job queue, the event to signal the shutdown of the thread pool,
        # the condition variable to signal the availability of a job in the queue
        self.job_queue = Queue()
        self.shutdown_event = Event()
        self.job_available = Condition()

        # The pool of threads:
        # create self.num_threads number of threads
        self.threads = [TaskRunner(self.shutdown_event, self.job_available, self.job_queue)
        for _ in range(self.num_threads)]

        # create a results directory if it does not exist already
        makedirs("results", exist_ok=True)

        # create a shutdown flag attribute for the ThreadPool
        self.shutdown_flag = False

    def start(self):
        '''
        This will start all TaskRunners
        '''
        for thread in self.threads:
            thread.start()

    def submit(self, job):
        '''
        a job was submitted to the ThreadPool
        so it will be added to the job queue

        notifies the TaskRunners that a job is available
        and the job queue is not empty
        '''
        self.job_queue.put(job)
        with self.job_available:
            self.job_available.notify()

    def shutdown(self):
        '''
        when the server get a shutdown request, the shutdown method is called:
        - first self.job_queue.join() will block until all jobs in the queue are processed,
        so until the last self.job_queue.task_done() is called
        - then the shutdown_event is set to notify all threads that they should shutdown
        - the job_available condition variable is notified to wake up all threads that might
        be waiting at the wait_for() method for jobs
        '''
        # set the shutdown flag to True so that from now on
        # no more jobs will be submitted to the ThreadPool
        self.shutdown_flag = True
        self.job_queue.join()
        self.shutdown_event.set()

        # notify all threads that they should shutdown and stop waiting
        # for jobs
        with self.job_available:
            self.job_available.notify_all()

        # wait for all threads to finish
        for thread in self.threads:
            thread.join()

class TaskRunner(Thread):
    '''
    class for defining a TaskRunner
    '''
    def __init__(self, terminate, job_available, queue):
        '''
        initialize the necessary data structures shared by the
        threads
        '''
        super().__init__()
        self.terminate = terminate
        self.job_available = job_available
        self.queue = queue

    def run(self):
        '''
        each TaskRunner will run this method
        '''
        while True:
            with self.job_available:
                # the wait_for() method waits until the queue is not empty or
                # the termination flag is set
                self.job_available.wait_for(
                    lambda: not self.queue.empty() or self.terminate.is_set()
                )
                # if the termination event is set, the thread will exit the loop
                if self.terminate.is_set():
                    break

            # get the job from the queue
            # the condition variable is used to signal that the queue is not empty
            # because the get() method blocks if the queue is empty
            job = self.queue.get()

            # depending on the type of operation needed for the job
            if 'global_operation' in job:
                res = job['operation'](job['data'], job['global_operation'](job['global_data']))
            else:
                res = job['operation'](job['data'])

            # write the result to a file
            try:
                with open(f"results/job_id_{job['job_id']}.json", 'w', encoding='utf-8') as file:
                    json.dump(res, file)
            except OSError as error:
                # create a log message
                CustomLogging().get_logger().error("Failed to write to file: %s", error)
                exit(1)

            # signal to the queue that the job is done
            self.queue.task_done()
