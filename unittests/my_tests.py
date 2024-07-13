'''
my_tests.py
to test it use command: python3 -m unittest -v unittests/my_tests.py
for the unittests I used a sample.csv file
'''

import unittest
from os import environ
# environment variable set in order to avoid the code from __init__.py to run
# because of the import of the DataIngestor class
environ['NO_SERVER'] = 'true'

from app.data_ingestor import DataIngestor
import app.operations as op

# constants to avoid repetition
# QUESTION1 and 2 are of type best is min
QUESTION1 = 'Percent of adults aged 18 years and older who have an overweight classification'
QUESTION2 = 'Percent of adults aged 18 years and older who have obesity'

class TestWebserver(unittest.TestCase):
    '''
    test the webserver
    '''
    def setUp(self):
        '''
        setup the test
        '''
        self.sample_data = DataIngestor('unittests/sample.csv')

    def test_states_mean(self):
        '''
        test the states mean
        '''
        data, _ = op.get_job_data_for_question(QUESTION1, self.sample_data.state_data)
        result = op.states_means()(data)
        self.assertEqual(result, {'Alabama': 30.0, 'Alaska': 33.4})

    def test_state_mean(self):
        '''
        test the state mean
        '''
        data = op.get_job_data_for_state(QUESTION1, 'Alabama', self.sample_data.state_data)
        result = op.state_mean()(data)
        self.assertEqual(result, {'Alabama': 30.0})

    def test_best5(self):
        '''
        test the best 5
        '''
        data, _ = op.get_job_data_for_question(QUESTION2, self.sample_data.state_data)
        result = op.best5()(data)
        self.assertEqual(result, {'Oregon': 20.6, 'Texas': 20.8, 'Ohio': 29.9, 'Alabama': 35.6,
        'Indiana': 45.6})

    def test_worst5(self):
        '''
        test the worst 5
        '''
        data, _ = op.get_job_data_for_question(QUESTION2, self.sample_data.state_data)
        result = op.worst5()(data)
        self.assertEqual(result, {'Idaho': 55.6, 'Indiana': 45.6, 'Alabama': 35.6, 'Ohio': 29.9,
        'Texas': 20.8})

    def test_global_mean1(self):
        '''
        test the global mean
        '''
        _, data = op.get_job_data_for_question(QUESTION1, self.sample_data.state_data, True, False)
        result = op.global_mean()(data)
        self.assertEqual(result, {'global_mean': 31.7})

    def test_global_mean2(self):
        '''
        test the global mean
        '''
        _, data = op.get_job_data_for_question(QUESTION2, self.sample_data.state_data, True, False)
        result = op.global_mean()(data)
        self.assertEqual(result, {'global_mean': 34.68333333333333})

    def test_diff_from_mean(self):
        '''
        test the diff from mean
        '''
        data, global_data = op.get_job_data_for_question(QUESTION1, self.sample_data.state_data,
        True, True)
        result = op.diff_from_mean()(data, op.global_mean()(global_data))
        self.assertEqual(result, {'Alabama': 1.6999999999999993, 'Alaska': -1.6999999999999993})

    def test_state_diff_from_mean(self):
        '''
        test the state diff from mean
        '''
        data = op.get_job_data_for_state(QUESTION1, 'Alabama', self.sample_data.state_data)
        _, global_data = op.get_job_data_for_question(QUESTION1, self.sample_data.state_data,
        True, False)
        result = op.diff_from_mean()(data, op.global_mean()(global_data))
        self.assertEqual(result, {'Alabama': 1.6999999999999993})

    def test_mean_by_category(self):
        '''
        test the mean by category
        '''
        data = op.get_job_data_for_categories(QUESTION1, self.sample_data.state_data)
        result = op.category_means()(data)
        self.assertEqual(result, {"('Alabama', 'Total', 'Total')": 30.0,
        "('Alaska', 'Total', 'Total')": 33.4})

    def test_state_mean_by_category(self):
        '''
        test the state mean by category
        '''
        data = op.get_job_data_for_categ_per_state(QUESTION1, 'Alabama',
        self.sample_data.state_data)
        result = op.state_mean_by_category()(data)
        self.assertEqual(result, {'Alabama': {"('Total', 'Total')": 30.0}})
