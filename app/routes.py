'''
route.py
'''
import os
import json
from flask import request, jsonify
from app import webserver
import app.operations as op

# constants
STATE = 'state'
QUESTION = 'question'

def shutting_down():
    '''
    function that returns the value of the shutdown flag from the thread pool
    that becomes true when the server gets a graceful shutdown request
    '''
    return webserver.tasks_runner.shutdown_flag

def type_of_question(question):
    '''
    get type of question: best is min or best is max question
    '''
    if question in webserver.data_ingestor.questions_best_is_min:
        return 'min'
    return 'max'

# Example endpoint definition
@webserver.route('/api/post_endpoint', methods=['POST'])
def post_endpoint():
    '''
    example of a post endpoint
    '''
    if request.method == 'POST':
        # Assuming the request contains JSON data
        data = request.json

        # Process the received data
        # For demonstration purposes, just echoing back the received data
        response = {"message": "Received data successfully", "data": data}

        # Sending back a JSON response
        return jsonify(response)

    # Method Not Allowed
    return jsonify({"error": "Method not allowed"}), 405

#/api/graceful_shutdown get method
@webserver.route('/api/graceful_shutdown', methods=['GET'])
def graceful_shutdown():
    '''
    server gets a get request that signals the shutdown of the thread pool
    the shutdown method in ThreadPool class will be called
    '''
    webserver.tasks_runner.shutdown()

    # create log message
    webserver.my_logger.info("Thread pool shutdown initiated")

    return jsonify({"status": "success"})

@webserver.route('/api/jobs', methods=['GET'])
def get_jobs():
    '''
    server gets a get request that returns the status of all the jobs
    submitted to the thread pool until then
    '''

    result = {}
    result['status'] = 'done'
    result['data'] = []

    for job in range(1, webserver.job_counter):
        # verify whether there is a file for the job_id
        job_id = f"job_id_{job}"
        if os.path.exists(f"results/{job_id}.json"):
            result['data'].append({job_id: "done"})
        else:
            result['data'].append({job_id: "running"})

    # create log message
    webserver.my_logger.info("Get jobs request")

    return jsonify(result)

@webserver.route('/api/num_jobs', methods=['GET'])
def get_num_jobs():
    '''
    server gets get request that returns the number of jobs left to process
    by the thread pool
    '''

    cnt = 0

    for job in range(1, webserver.job_counter):
        # verify whether there is a file for the job_id

        job_id = f"job_id_{job}"

        if not os.path.exists(f"results/{job_id}.json"):
            # stop counting when the first job that is not done is found
            break

        cnt += 1

    # create log message
    webserver.my_logger.info("Get number of jobs left to process request")

    return jsonify({"num_jobs": webserver.job_counter - cnt - 1})

@webserver.route('/api/get_results/<job_id>', methods=['GET'])
def get_response(job_id):
    '''
    server gets a get request that returns the result of a job
    '''

    # if the job_counter is smaller or equal than the job_id, return invalid job_id
    if int(job_id) >= webserver.job_counter:
        # create log message
        webserver.my_logger.error("Invalid job_id %s", job_id)
        return jsonify({'status': 'error', 'reason': 'Invalid job_id'})

    # if the job_counter is bigger than the job_id but the job is not done, return running status
    # we verify if the job is done by checking if the file for the job_id is in the results folder

    # verify if the file of the corresponding job_id exists
    if os.path.exists(f"results/job_id_{job_id}.json"):
        try:
            # open the file and load the data
            with open(f"results/job_id_{job_id}.json", 'r', encoding='utf-8') as file:
                try:
                    data = json.load(file)

                    # create log message
                    webserver.my_logger.info("Job_id_%s processed successfully", job_id)

                    return jsonify({'status': 'done', 'data': data})
                except json.JSONDecodeError:
                    # if not all the data was written to the file,
                    # the json.load will raise an error because the data will
                    # not be in json format

                    # create log message
                    webserver.my_logger.error("Error reading job_id_%s.json", job_id)

                    return jsonify({'status': 'running'})
        except (FileNotFoundError, PermissionError, IOError):
            # if opening the file raises an error, the job is still running

            # create log message
            webserver.my_logger.error("Error opening job_id_%s.json", job_id)

            return jsonify({'status': 'running'})

    # if the file does not exist, the job is still running
    # create log message
    webserver.my_logger.info("File job_id_%s.json does not exist yet", job_id)

    return jsonify({'status': 'running'})

@webserver.route('/api/states_mean', methods=['POST'])
def states_mean_request():
    '''
    extracts the data needed for solving the post request
    creates a job and submits it to the thread pool
    '''

    if shutting_down():
        # if the the thread pool is shutting down, it will not accept any more jobs
        return jsonify({'job_id': -1, 'reason': 'Shutting down'})

    # Get request data
    data = request.json

    # extract the question from the request
    question = data[QUESTION]

    # get the data for the job based on the question
    data_for_job, _ = op.get_job_data_for_question(question, webserver.data_ingestor.state_data)

    # create the job as a dictionary
    job = {
        'job_id': webserver.job_counter,
        'operation': op.states_means(),
        'data': data_for_job
    }

    # submit job
    webserver.tasks_runner.submit(job)

    # create log message
    webserver.my_logger.info("States mean request submitted as job with id %d",
    webserver.job_counter)

    # Increment job_id counter
    webserver.job_counter += 1

    # Return associated job_id
    return jsonify({"job_id": webserver.job_counter - 1})

@webserver.route('/api/state_mean', methods=['POST'])
def state_mean_request():
    '''
    extracts de data needed for solving the post request
    creates a job and submits it to the thread pool
    '''

    if shutting_down():
        # if the the thread pool is shutting down, it will not accept any more jobs
        return jsonify({'job_id': -1, 'reason': 'Shutting down'})

    # get request data
    data = request.json

    # extract the question and state from the request
    question = data[QUESTION]
    state = data[STATE]

    # get the data for the job based on the question and state
    data_for_job = op.get_job_data_for_state(question, state, webserver.data_ingestor.state_data)

    # if the data_for_job contains a status key, it means that the state or question is invalid
    if 'status' in data_for_job:
        # create a log message
        webserver.my_logger.error("State mean request failed with error %s",
        {data_for_job['status']})
        return jsonify(data_for_job)

    # create job as a dictionary
    job = {
        'job_id': webserver.job_counter,
        'operation': op.state_mean(),
        'data': data_for_job
    }

    # submit job to the thread pool
    webserver.tasks_runner.submit(job)

    # create log message
    webserver.my_logger.info("State mean request submitted as job with id %d",
    webserver.job_counter)

    # Increment job_id counter
    webserver.job_counter += 1

    # Return associated job_id
    return jsonify({"job_id": webserver.job_counter - 1})

@webserver.route('/api/best5', methods=['POST'])
def best5_request():
    '''
    extracts de data needed for solving the post request
    creates a job and submits it to the thread pool
    '''

    if shutting_down():
        # if the the thread pool is shutting down, it will not accept any more jobs
        return jsonify({'job_id': -1, 'reason': 'Shutting down'})

    # get request data
    data = request.json

    # extract the question from the request
    question = data[QUESTION]

    # get the data for the job based on the question
    data_for_job, _ = op.get_job_data_for_question(question, webserver.data_ingestor.state_data)

    # based on the type of question, we will use the best5 or worst5 operation
    # the types of questions are defined in the data_ingestor.py file
    question_type = type_of_question(question)

    if question_type == 'min':
        operation = op.best5()
    else:
        operation = op.worst5()

    # create job as a dictionary
    job = {
        'job_id': webserver.job_counter,
        'operation': operation,
        'data': data_for_job
    }

    # submit job to the thread pool
    webserver.tasks_runner.submit(job)

    # create log message
    webserver.my_logger.info("Best5 request submitted as job with id %d",
    webserver.job_counter)

    # Increment job_id counter
    webserver.job_counter += 1

    # Return associated job_id
    return jsonify({"job_id": webserver.job_counter - 1})

@webserver.route('/api/worst5', methods=['POST'])
def worst5_request():
    '''
    extracts de data needed for solving the post request
    creates a job and submits it to the thread pool
    '''

    if shutting_down():
        # if the the thread pool is shutting down, it will not accept any more jobs
        return jsonify({'job_id': -1, 'reason': 'Shutting down'})

    # get request data
    data = request.json

    # extract the question from the request
    question = data[QUESTION]

    # get the data for the job based on the question
    data_for_job, _ = op.get_job_data_for_question(question, webserver.data_ingestor.state_data)

    # based on the type of question, we will use the best5 or worst5 operation
    question_type = type_of_question(question)
    if question_type == 'min':
        operation = op.worst5()
    else:
        operation = op.best5()

    # create job as a dictionary
    job = {
        'job_id': webserver.job_counter,
        'operation': operation,
        'data': data_for_job
    }

    # submit job to the thread pool
    webserver.tasks_runner.submit(job)

    # create log message
    webserver.my_logger.info("Worst5 request submitted as job with id %d",
    webserver.job_counter)

    # Increment job_id counter
    webserver.job_counter += 1

    # Return associated job_id
    return jsonify({"job_id": webserver.job_counter - 1})

@webserver.route('/api/global_mean', methods=['POST'])
def global_mean_request():
    '''
    extracts de data needed for solving the post request
    creates a job and submits it to the thread pool
    '''

    if shutting_down():
        # if the the thread pool is shutting down, it will not accept any more jobs
        return jsonify({'job_id': -1, 'reason': 'Shutting down'})

    # get request data
    data  = request.json

    # extract the question from the request
    question = data[QUESTION]

    # get global data needed for the job
    _, data_for_job = op.get_job_data_for_question(question, webserver.data_ingestor.state_data,
    global_data=True, normal_data=False)

    # create job as a dictionary
    job = {
        'job_id': webserver.job_counter,
        'operation': op.global_mean(),
        'data': data_for_job
    }

    # submit job to the thread pool
    webserver.tasks_runner.submit(job)

    # create log message
    webserver.my_logger.info("Global mean request submitted as job with id %d",
    webserver.job_counter)

    # Increment job_id counter
    webserver.job_counter += 1

    # Return associated job_id
    return jsonify({"job_id": webserver.job_counter - 1})

@webserver.route('/api/diff_from_mean', methods=['POST'])
def diff_from_mean_request():
    '''
    extracts de data needed for solving the post request
    creates a job and submits it to the thread pool
    '''

    if shutting_down():
        # if the the thread pool is shutting down, it will not accept any more jobs
        return jsonify({'job_id': -1, 'reason': 'Shutting down'})

    # get request data
    data = request.json

    # extract the question from the request
    question = data[QUESTION]

    # get the data for each state and the global data needed for the job
    data_for_job, data_for_global = op.get_job_data_for_question(question,
    webserver.data_ingestor.state_data, global_data=True)

    # create job as a dictionary
    job = {
        'job_id': webserver.job_counter,
        'operation': op.diff_from_mean(),
        'data': data_for_job,
        'global_operation': op.global_mean(),
        'global_data': data_for_global
    }

    # submit job to the thread pool
    webserver.tasks_runner.submit(job)

    # create log message
    webserver.my_logger.info("Diff from mean request submitted as job with id %d",
    webserver.job_counter)

    # Increment job_id counter
    webserver.job_counter += 1

    return jsonify({"job_id": webserver.job_counter - 1})

@webserver.route('/api/state_diff_from_mean', methods=['POST'])
def state_diff_from_mean_request():
    '''
    extracts de data needed for solving the post request
    creates a job and submits it to the thread pool
    '''

    if shutting_down():
        # if the the thread pool is shutting down, it will not accept any more jobs
        return jsonify({'job_id': -1, 'reason': 'Shutting down'})

    # get request data
    data = request.json

    # extract the question and state from the request
    question = data[QUESTION]
    state = data[STATE]

    # get the data for the job based on the question and state
    data_for_job = op.get_job_data_for_state(question, state, webserver.data_ingestor.state_data)

    # if the data_for_job contains a status key, it means that the state or question is invalid
    if 'status' in data_for_job:
        # create log message
        webserver.my_logger.error("State diff from mean request failed with error %s",
        data_for_job['status'])
        return jsonify(data_for_job)

    # get the global data needed for the job
    _, data_for_global = op.get_job_data_for_question(question, webserver.data_ingestor.state_data,
    global_data=True, normal_data=False)

    # create job as a dictionary
    job = {
        'job_id': webserver.job_counter,
        'operation': op.diff_from_mean(),
        'data': data_for_job,
        'global_operation': op.global_mean(),
        'global_data': data_for_global
    }

    # submit job to the thread pool
    webserver.tasks_runner.submit(job)

    # create log message
    webserver.my_logger.info("State diff from mean request submitted as job with id %d",
    webserver.job_counter)

    # Increment job_id counter
    webserver.job_counter += 1

    # Return associated job_id
    return jsonify({"job_id": webserver.job_counter - 1})

@webserver.route('/api/mean_by_category', methods=['POST'])
def mean_by_category_request():
    '''
    extracts de data needed for solving the post request
    creates a job and submits it to the thread pool
    '''

    if shutting_down():
        # if the the thread pool is shutting down, it will not accept any more jobs
        return jsonify({'job_id': -1, 'reason': 'Shutting down'})

    # get request data
    data = request.json

    # extract the question from the request
    question = data[QUESTION]

    # get the data for the job based on the question
    data_for_job = op.get_job_data_for_categories(question, webserver.data_ingestor.state_data)

    # if the data_for_job contains a status key, it means that the state or question is invalid
    if 'status' in data_for_job:
        # create log message
        webserver.my_logger.error("Mean by category request failed with error %s",
        data_for_job['status'])
        return jsonify(data_for_job)

    # create job as a dictionary
    job = {
        'job_id': webserver.job_counter,
        'operation': op.category_means(),
        'data': data_for_job
    }

    # submit job to the thread pool
    webserver.tasks_runner.submit(job)

    # create log message
    webserver.my_logger.info("Mean by category request submitted as job with id %d",
    webserver.job_counter)

    # Increment job_id counter
    webserver.job_counter += 1

    return jsonify({"job_id": webserver.job_counter - 1})

@webserver.route('/api/state_mean_by_category', methods=['POST'])
def state_mean_by_category_request():
    '''
    extracts de data needed for solving the post request
    creates a job and submits it to the thread pool
    '''
    if shutting_down():
        # if the the thread pool is shutting down, it will not accept any more jobs
        return jsonify({'job_id': -1, 'reason': 'Shutting down'})

    # get request data
    data = request.json

    # extract the question and state from the request
    question = data[QUESTION]
    state = data[STATE]

    # get the data for the job based on the question and state
    data_for_job = op.get_job_data_for_categ_per_state(question, state,
    webserver.data_ingestor.state_data)

    # if the data_for_job contains a status key, it means that the state or question is invalid
    if 'status' in data_for_job:
        # create log message
        webserver.my_logger.error("State mean by category request failed with error %s",
        data_for_job['status'])
        return jsonify(data_for_job)

    # create job as a dictionary
    job = {
       'job_id': webserver.job_counter,
       'operation': op.state_mean_by_category(),
       'data': data_for_job
    }

    # submit job to the thread pool
    webserver.tasks_runner.submit(job)

    # Increment job_id counter
    webserver.job_counter += 1

    # create log message
    webserver.my_logger.info("State mean by category request submitted as job with id %d",
    webserver.job_counter)

    return jsonify({"job_id": webserver.job_counter - 1})

# You can check localhost in your browser to see what this displays
@webserver.route('/')
@webserver.route('/index')
def index():
    '''
    index function
    '''
    routes = get_defined_routes()
    msg = "Hello, World!\n Interact with the webserver using one of the defined routes:\n"

    # Display each route as a separate HTML <p> tag
    paragraphs = ""
    for route in routes:
        paragraphs += f"<p>{route}</p>"

    msg += paragraphs
    return msg

def get_defined_routes():
    '''
    get all the routes defined in the webserver
    '''
    routes = []
    for rule in webserver.url_map.iter_rules():
        methods = ', '.join(rule.methods)
        routes.append(f"Endpoint: \"{rule}\" Methods: \"{methods}\"")
    return routes
