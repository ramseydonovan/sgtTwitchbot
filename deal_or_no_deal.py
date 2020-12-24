'''
DONDManager class maintains a deal or no deal game. 
'''
from random import sample
import point_utils

PRIZE_VALUES = [100, 200, 300, 600, 950, 1300]
ENTRENCE_FEE = 300

class DONDManager:

    def __init__(self, username):
        self.username = username
        self.cost = ENTRENCE_FEE
        self.game_title = 'Deal or No Deal'
        self.cases = []
        self.selected_cases = []
        self.game_over = False
        


    def start_game(self):
        # shuffle prize values
        self.cases = sample(PRIZE_VALUES, len(PRIZE_VALUES))
        start_message = '{} is now playing deal or no deal PogChamp PogChamp. You have the chance to win 1000 points SabaPing '.format(self.username)
        start_message += self.generate_cases_message()
        return start_message

    def process_input(self, value):
        try:
            case_number = int(value)
            case_value = self.cases[case_number - 1]
        except Exception as e:
            print(e)
            return 'Case number must be a number 1-{}'.format(len(PRIZE_VALUES))

        if (case_number - 1) in self.selected_cases:
            available_vals = [x for x in self.cases if x not in self.selected_cases]
            return 'Case {} has already been opened. Available values: {}'.format(case_number, ', '.join(available_vals))

        # open case 
        self.selected_cases.append(case_number - 1)

        message = 'Case number {} was worth {} points. '.format(case_number, case_value)

        if len(self.selected_cases) == len(self.cases) - 1:
            # signal to end game
            # give user points
            points = point_utils.get_points(self.username)
            winning_case_value = self.get_winning_value()
            points += winning_case_value
            
            point_utils.set_points(self.username, points)

            winnings = winning_case_value - ENTRENCE_FEE

            if winnings > 0:
                message += '{} won {} points! PogChamp'.format(self.username, winnings)
            elif winnings == 0:
                message += '{} broke even. Could have been worse Kappa'.format(self.username)
            else:
                message += '{} lost {} points. Better luck next time!'.format(self.username, winnings)

            message += '{} now has {} points. The game is over. Thanks for playing!'.format(self.username, points)
            self.game_over = True
        else:
            message += self.generate_cases_message()

        return message

    def get_winning_value(self):
        for case_num,case_val in enumerate(self.cases):
            if case_num not in self.selected_cases:
                return case_val

    def generate_cases_message(self):
        message = 'Select a brief case by typing "!case" followed by the "case number"   '
        for case_num,box in enumerate(self.cases):
            # if case is selected then display the value else display the case number
            if case_num in self.selected_cases:
                message += ' [{}]'.format(box)
            else:
                message += ' [{}]'.format(case_num + 1)

        message.replace('[0]', '[DarkMode]')

        return message
        


