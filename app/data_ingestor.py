'''
data_ingestor.py
'''
from csv import DictReader

# constants for dictionary keys
STATE = 'LocationDesc'
QUESTION = 'Question'
DATA_VALUE = 'Data_Value'
STRATIF1 = 'Stratification1'
STRATIFCAT1 = 'StratificationCategory1'

class DataIngestor:
    '''
    class that reads from csv file
    '''
    def __init__(self, csv_path: str):
        '''
            read the csv file line by line so that we do not load the entire file into memory
            at once

            we create a dictionary of states, where each state is a key and the value is another
            dictionary of questions, where each question is a key and the value is another
            dictionary where the key is a string tuple of stratification category 1 and
            stratification 1 and the value is a list of data values
        '''
        self.state_data = {}

        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = DictReader(file)
            for line in reader:
                state = line[STATE]
                question = line[QUESTION]
                data_value = line[DATA_VALUE]
                stratcat1 = line[STRATIFCAT1]
                strat1 = line[STRATIF1]

                if state not in self.state_data:
                    self.state_data[state] = {}
                if question not in self.state_data[state]:
                    self.state_data[state][question] = {}

                if str((stratcat1, strat1)) not in self.state_data[state][question]:
                    self.state_data[state][question][str((stratcat1, strat1))] = []
                self.state_data[state][question][str((stratcat1, strat1))].append(float(data_value))

        self.questions_best_is_min = [
            'Percent of adults aged 18 years and older who have an overweight classification',
            'Percent of adults aged 18 years and older who have obesity',
            'Percent of adults who engage in no leisure-time physical activity',
            'Percent of adults who report consuming fruit less than one time daily',
            'Percent of adults who report consuming vegetables less than one time daily'
        ]

        self.questions_best_is_max = [
            'Percent of adults who achieve at least 150 minutes a week of moderate-intensity \
aerobic physical activity or 75 minutes a week of vigorous-intensity aerobic activity \
(or an equivalent combination)',
            'Percent of adults who achieve at least 150 minutes a week of moderate-intensity \
aerobic physical activity or 75 minutes a week of vigorous-intensity aerobic physical \
activity and engage in muscle-strengthening activities on 2 or more days a week',
            'Percent of adults who achieve at least 300 minutes a week of moderate-intensity \
aerobic physical activity or 150 minutes a week of vigorous-intensity aerobic \
activity (or an equivalent combination)',
            'Percent of adults who engage in muscle-strengthening activities on 2 or more \
days a week',
        ]
