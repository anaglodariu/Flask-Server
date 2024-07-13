'''
operations.py
'''
from ast import literal_eval

def state_mean():
    '''
    calculates the mean of the values for a certain state
    '''

    return lambda data: {key: sum(values) / len(values) for key, values in data.items()}

def global_mean():
    '''
    calculates the global mean of the values for all the states
    '''

    return lambda data: {key: sum(values) / len(values) for key, values in data.items()}

def states_means():
    '''
    calculates the mean of the values for each state and sorts them in ascending order
    '''

    return lambda data: dict(
        sorted(
            {key: sum(values) / len(values) for key, values in data.items()}.items(),
            key=lambda item: item[1]
        )
    )

def category_means():
    '''
    calculates the mean of the values for each key made of the state, stratification category
    and stratification and sorts them in ascending order
    '''

    return lambda data: dict(
        sorted(
            {key: sum(values) / len(values) for key, values in data.items()}.items(),
            key=lambda item: item[0]
        )
    )

def state_mean_by_category():
    '''
    for a state key calculates for each stratification category and stratification key the mean
    of the values and sorts them in ascending order
    '''

    return lambda data: {state: dict(
        sorted(
            {key: sum(values) / len(values) for key, values in categories.items()}.items(),
            key=lambda item: item[0]
        )
    ) for state, categories in data.items()}


def diff_from_mean():
    '''
    function that returns a lambda function that has as input:
        - a dictionary with the key being the state and the value a list of data values
        - the global mean for all states

    lambda function calculates the difference between the global mean and the mean of the values
    for each state
    '''

    return lambda data, global_data: dict(
        sorted(
            {key: global_data['global_mean'] - sum(values) / len(values)
            for key, values in data.items()}.items(),
            key=lambda item: item[1],
            reverse=True
        )
    )

def best5():
    '''
    returns a lambda function that has as input a dictionary with the key being the state and
    the value a list of data values and calculates the mean of the data values for each state key,
    sorts them in ascending order and gets the first 5 states with the lowest mean
    '''

    return lambda data: dict(
            sorted(
                {key: sum(values) / len(values) for key, values in data.items()}.items(),
                key=lambda item: item[1]
            )[:5]
        )

def worst5():
    '''
    returns a lambda function that has as input a dictionary with the key being the state and
    the value a list of data values and calculates the mean of the data values for each state key,
    sorts them in descending order and gets the first 5 states with the highest mean
    '''

    return lambda data: dict(
            sorted(
                {key: sum(values) / len(values) for key, values in data.items()}.items(),
                key=lambda item: item[1], reverse=True
            )[:5]
        )

def get_job_data_for_question(question, data, global_data = False, normal_data = True):
    '''
    function that extracts the data needed for the job when the request to the server contains a
    question

    if the request needs the mean for every state than normal_data should be True, the function
    will return a dictionary with the key being the state and the value a list of data values
    for the question

    if the request needs the mean for all the states than global_data should be True, the function
    will return a dictionary with the key being 'global_mean' and the value a list of all data the
    values for the question for all the states

    in the for loop, the function will get all the data values for the question for the given state
    irrespective of the stratification category and stratification

    for each stratification category and stratification key, the value is a list of data values
    so the lists will be concatenated in one list
    '''

    data_for_job = {}
    data_for_global = {'global_mean': []}
    for state in data:
        if question in data[state]:
            values_for_question = data[state][question].values()
            list_of_values = [item for list in values_for_question for item in list]
            if normal_data:
                data_for_job[state] = list_of_values
            if global_data:
                data_for_global['global_mean'].extend(list_of_values)

    return data_for_job, data_for_global

def get_job_data_for_state(question, state, data):
    '''
    function that extracts the data needed for the job when the request to the server contains a
    question and a state

    function returns a dictionary with the key being the state and the value a list of data values

    the function will get all the data values for the question for the given state
    irrespective of the stratification category and stratification

    for each stratification category and stratification key, the value is a list of data values
    so the lists will be concatenated in one list
    '''

    data_for_job = {}
    if state in data:
        if question in data[state]:
            values_for_question = data[state][question].values()
            data_for_job[state] = [item for list in values_for_question for item in list]
        else:
            # when given question is not in the csv file
            return {"status": "Invalid question"}
    else:
        # when given state is not in the csv file
        return {"status": "Invalid state"}

    return data_for_job

def get_job_data_for_categories(question, data):
    '''
    function returns a dictionary with the key being a tuple of the state, stratification category
    and stratification and the value a list of data values
    '''

    data_for_job = {}
    for state in data:
        if question in data[state]:
            for str_categories in data[state][question]:
                # categories is a tuple made string, so we need to convert it back to a tuple
                try:
                    tuple_categories = literal_eval(str_categories)
                except (ValueError, SyntaxError):
                    return {"status": "Invalid syntax for categories key"}

                # if the tuple is not empty, we will create a new key for the dictionary
                if tuple_categories[0] != '' and tuple_categories[1] != '':
                    new_key = str((state, tuple_categories[0], tuple_categories[1]))
                    data_for_job[new_key] = data[state][question][str_categories]
    return data_for_job

def get_job_data_for_categ_per_state(question, state, data):
    '''
    function that returns a dictionary with the key being the state and the value a dictionary with
    the key being a tuple of the stratification category and stratification and the value a list of
    data values
    '''

    data_for_job = {}
    if state in data:
        data_for_job[state] = data[state][question]
    else:
        return {"status": "Invalid state"}
    return data_for_job
