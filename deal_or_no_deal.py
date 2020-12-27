'''
DONDManager class maintains a deal or no deal game. 
'''
from random import sample
import point_utils

PRIZE_VALUES = [50, 75, 100, 200, 300, 400, 500, 600, 700, 800, 950, 1300]
ENTRENCE_FEE = 300
TURNS_BEFORE_OFFER = 3

class DONDManager:

    def __init__(self, username):
        self.username = username
        self.cost = ENTRENCE_FEE
        self.game_title = 'Deal or No Deal'
        self.cases = []
        self.selected_cases = []
        self.game_over = False
        self.turns_before_offer = TURNS_BEFORE_OFFER
        self.first_case = -1
        self.final_turn = False
        


    def start_game(self):
        # shuffle prize values
        self.cases = sample(PRIZE_VALUES, len(PRIZE_VALUES))
        start_message = '{} is now playing deal or no deal PogChamp PogChamp. You have the chance to win 1000 points SabaPing Select the case that you want to keep. '.format(self.username)
        start_message += self.generate_cases_message()
        return start_message

    def process_input(self, command, value):
        
        if command == 'case':
            message = self.process_case_input(value)
        elif command == 'deal' or command == 'nodeal':
            message = self.process_deal_input(command)
        elif command == 'swap' or command == 'noswap':
            message = self.process_swap_input(command)
        else:
            message = 'Invalid command in deal_or_no_deal'

        return message


    def process_case_input(self, value):
        # validate case input
        if self.turns_before_offer == 0:
            return 'type "!deal" to accept the offer or !nodeal to keep going. The current offer is {}'.format(self.generate_offer())

        try:
            case_number = int(value)
            case_value = self.cases[case_number - 1]
        except Exception as e:
            print(e)
            return 'Case number must be a number 1-{}'.format(len(PRIZE_VALUES))

        # check if case has already been opened
        if (case_number - 1) in self.selected_cases:
            available_vals = self.get_remaining_cases()
            return 'Case {} has already been opened. Available values: {}'.format(case_number, ', '.join(available_vals))

        # if this is the first case then store it, else open the case
        if self.first_case == -1:
            self.first_case = case_number - 1
            message = 'Your case is case number {}! '.format(case_number)
        else:
            # open case
            self.selected_cases.append(case_number - 1)
            message = 'Case number {} was worth {} points. '.format(case_number, case_value)
            self.turns_before_offer = self.turns_before_offer - 1

        # check if there are no more cases available
        if len(self.selected_cases) == len(self.cases) - 1:
            # signal to end game
            winning_case_value = self.get_winning_value()
            message = self.end_game(winning_case_value)
        elif self.turns_before_offer == 0:
            message += self.generate_offer_message()
        else:
            message += self.generate_cases_message()

        return message


    def process_deal_input(self, value):
        if self.turns_before_offer != 0:
            message = 'You must select {} more case(s) before the next offer. '.format(self.turns_before_offer)
            message += self.generate_cases_message()
            return message

        if value == 'deal':
            amount_won = self.generate_offer()
            message = self.end_game(amount_won)
        elif value == 'nodeal':
            if len(self.selected_cases) >= len(self.cases) - TURNS_BEFORE_OFFER:
                self.turns_before_offer = 1
                # custom message for the final turn
                if len(self.selected_cases) == len(self.cases) - 2:
                    message = 'Do you want to swap your case? !swap or !noswap'
                    self.final_turn = True
                else:
                    message = '{} has selected NO DEAL KomodoHype '.format(self.username)
                    message += self.generate_cases_message()
            else:
                self.turns_before_offer = TURNS_BEFORE_OFFER
                message = '{} has selected NO DEAL KomodoHype '.format(self.username)
                message += self.generate_cases_message()

        return message


    def process_swap_input(self, value):
        if self.final_turn != True:
            return 'Cannot swap cases until the final turn.'

        if value == 'swap':
            remaining_case_indexes = [i for i,x in enumerate(self.cases) if i not in self.selected_cases]
            self.first_case = [x for x in remaining_case_indexes if x != self.first_case][0]

        message = self.end_game(self.cases[self.first_case])

        return message


    def end_game(self, amount_won):
        message = ''
        points = point_utils.get_points(self.username)
        points += amount_won
        point_utils.set_points(self.username, points)
        winnings = amount_won - ENTRENCE_FEE

        if winnings > 0:
            message += '{} won {} points! PogChamp'.format(self.username, winnings)
        elif winnings == 0:
            message += '{} broke even. Could have been worse Kappa'.format(self.username)
        else:
            message += '{} lost {} points. Better luck next time!'.format(self.username, winnings)

        message += '{} now has {} points. The game is over. Thanks for playing!'.format(self.username, points)
        self.game_over = True

        return message


    def generate_offer(self):
        # get a list of the remaining cases
        remaining_cases = self.get_remaining_cases()

        # calculate the expected value
        num_remaining = len(remaining_cases)
        expected_value = sum([x * (1/num_remaining) for x in remaining_cases])
        negotiation_percentage = .15
        expected_value = expected_value - (expected_value * negotiation_percentage)

        return round(expected_value)


    def get_remaining_cases(self):
        remaining_cases = [x for i,x in enumerate(self.cases) if i not in self.selected_cases]
        return remaining_cases


    def get_winning_value(self):
        for case_num,case_val in enumerate(self.cases):
            if case_num not in self.selected_cases:
                return case_val

    def generate_offer_message(self):
        offer = self.generate_offer()
        message = '*Ring* *Ring* ... yes ... you sure that is the offer? Ok I will tell them. We are offering you {} points. Deal or no deal?! Type "!deal" or "!nodeal"'.format(offer)
        return message
    

    def generate_cases_message(self):
        message = '{} case(s) remaining before the next offer. Select a brief case by typing "!case" followed by the "case number"   '.format(self.turns_before_offer)
        for case_num,box in enumerate(self.cases):
            # if case is selected then display the value else display the case number
            if case_num == self.first_case:
                message += ' [*your case*]'
            elif case_num in self.selected_cases:
                message += ' [{}]'.format(box)
            else:
                message += ' [{}]'.format(case_num + 1)

        message.replace('[0]', '[DarkMode]')

        return message
        


