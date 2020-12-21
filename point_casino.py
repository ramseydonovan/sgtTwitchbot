'''
NOT TO BE USED FOR MONENTARY VALUE

PointCasino class
'''
import point_utils
import random

class PointCasino:

    def __init__(self, username, wager):
        self.username = username
        self.wager = wager
        self.gamble_percentage = 51
        self.winnings = 0
        self.points = point_utils.get_points(username)
        self.roll = self.roll_die()
        self.win = self.evaluate_roll(self.roll, self.gamble_percentage)
        self.bonus_roll = self.roll_die()
        self.messages = []


    def roll_die(self):
        roll = random.randrange(100) + 1
        return roll


    def evaluate_roll(self, roll, gamble_percentage):
        return False if roll < gamble_percentage else True


    def generate_gamble_message(self, bonus=False):
        if self.win == True:
            self.messages.append('{} rolled a {}! You win {} points. {} now has {} total points.'.format(self.username, self.roll, self.wager, self.username, self.points))
            if bonus:
                self.messages.append(' You hit a BABY BACK BONUS! Bonus roll was {}'.format(self.bonus_roll))
        else:
            self.messages.append('{} rolled a {}. You lost {} points. {} now has {} total points.'.format(self.username, self.roll, self.wager, self.username, self.points))


    def apply_bonuses(self):
        '''
          Apply bonuses and roll a bonus roll.
          :param roll - the user's dice roll
          :param amount - the amount wagered
          :param win - true if the user's roll is a win
        '''
        # apply bonus multipliers
        if self.roll == 69 or self.roll == 100:
            self.winnings *= 2

        if self.roll == 97:
            self.winnings = self.winnings + (self.winnings/4)

        if self.roll == 98:
            self.winnings = self.winnings + (self.winnings/3)

        if self.roll == 99:
            self.winnings = self.winnings + (self.winnings/2)

        # handle bonus roll
        if self.bonus_roll == self.roll:
            if self.win:
                self.winnings *= 10
            else:
                self.winnings = self.wager * 5

        if self.win == True and self.bonus_roll > 89:
            self.winnings *= 2

        self.winnings = round(self.winnings)


    def gamble_points(self):
        # if gambling all set amount to the user's points
        if isinstance(self.wager, str):
            self.wager = self.points
        
        if self.wager < 1:
            message = "gambling amount must be positive"
            return [message]

        # check if the user has enough points
        if (self.points < 1) or (self.wager > self.points):
            message = "{} does not have enough points.".format(self.username)
            return [message]
        
        if self.win == True:
            self.winnings = self.wager
        
        self.apply_bonuses()

        # if there is a losing roll, there is still a chance that a bonus could
        # hit so set win to True
        bonus = False
        if self.winnings > self.wager:
            self.win = True
            bonus = True

        if self.win == True:
            self.points += self.winnings
        else:
            self.points -= self.wager

        self.generate_gamble_message(bonus)
        point_utils.set_points(self.username, self.points)

        if bonus == True:
            self.enter_bonus_zone()

        return self.messages


    def enter_bonus_zone(self):
        self.messages.append('{} has entered the BONUS ZONE PogChamp'.format(self.username))
        winner = True
        number_of_wins = 1
        number_of_rolls = 1
        while (winner == True or number_of_rolls < 4) and number_of_rolls < 11:
            roll = self.roll_die()
            win = self.evaluate_roll(roll, self.gamble_percentage)
            if win == True:
                 self.points += self.wager
                 bonus_message = 'BONUS role was {}. {} won {} BONUS points{}'.format(roll, self.username, self.wager, '!'*number_of_wins)
                 self.messages.append(bonus_message)
                 number_of_wins += 1
            else:
                bonus_message = 'BONUS role was {} for {}.'.format(roll, self.username)
                self.messages.append(bonus_message)
                winner = False
            number_of_rolls += 1

        point_utils.set_points(self.username, self.points)
        self.messages.append('{} has left the BONUS ZONE. {} now has {} points!'.format(self.username, self.username, self.points))



