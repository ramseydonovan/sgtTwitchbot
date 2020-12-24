'''
GameManager class stores an active game and deletes the game when over. 
'''
import deal_or_no_deal
import point_utils

GAME_TITLES = {
    'deal': 'Deal or No Deal'
}

class GameManager:

    def __init__(self):
        self.active_games = []


    
    def select_game(self, game_title, username):
        message = ''

        if self.check_active_games():
            message = 'A game is currently active. Only one game can be active at a time.'
            return message

        if game_title == 'deal':
            game_manager = deal_or_no_deal.DONDManager(username)
            points = point_utils.get_points(username)
            
            if points >= game_manager.cost:
                points -= game_manager.cost
                point_utils.set_points(username, points)
            else:
                return 'This game cost {} points. Need more points!'.format(game_manager.cost)

            self.active_games.append(game_manager)
            message = game_manager.start_game()
        else:
            message = 'Invalid game choice.'

        return message


    def enter_game_input(self, value):
        message = self.active_games[0].process_input(value)
        if self.active_games[0].game_over == True:
            self.active_games = []
        return message


    def check_game_is_active(self, game_key):
        return True if (len(self.active_games) > 0) and (self.active_games[0].game_title == GAME_TITLES.get(game_key)) else False


    def check_active_games(self):
        return True if len(self.active_games) > 0 else False

