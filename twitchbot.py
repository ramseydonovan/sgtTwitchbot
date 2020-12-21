'''
twitch bot 

requires variables to be set in a .env file, see main 
'''
import sys
import irc.bot
import requests
import threading
import time
import json
import point_utils
import point_casino
import os
from dotenv import load_dotenv


class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self, username, client_id, token, channel):
        self.client_id = client_id
        self.token = token
        self.channel = '#' + channel

        # True if drink command is enabled, false if disabled
        self.drink_enabled = False

        # used for gamble command, any number greater than or equal to this is a win
        self.gamble_percentage = 51

        # map command name to timeout in minutes
        self.command_timeouts = {
            'drink': 15
        }

        # holds commands that have time before they can be executed again
        self.commands_in_timeout = {}

        # Get the channel id, we will need this for v5 API calls
        url = 'https://api.twitch.tv/kraken/users?login=' + channel
        headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get(url, headers=headers).json()

        self.channel_id = r['users'][0]['_id']
        
        print (r)
        sys.stdout.flush()

        # Create IRC bot connection
        server = 'irc.chat.twitch.tv'
        port = 6667
        print ('Connecting to ' + server + ' on port ' + str(port) + '...')
        sys.stdout.flush()
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, 'oauth:'+token)], username, username)
        

    def on_welcome(self, c, e):
        print ('Joining ' + self.channel)

        # You must request specific capabilities before you can use them
        # c.cap('REQ', ':twitch.tv/membership')
        # c.cap('REQ', ':twitch.tv/tags')
        # c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)


    def on_pubmsg(self, c, e):

        # If a chat message starts with an exclamation point, try to run it as a command
        if e.arguments[0][:1] == '!':
            cmd = e.arguments[0].split(' ')[0][1:]
            print ('Received command: ' + cmd)
            print (e)
            sys.stdout.flush()

            self.do_command(e, cmd)
        return


    def get_request(self):
        # get channel data from twitch api
        url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id
        headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        return requests.get(url, headers=headers).json()


    def put_command_in_timeout(self, cmd):
        self.commands_in_timeout[cmd] = time.time()


    def update_commands_in_timeout(self, cmd):
        # Remove command from timeout if it's timeout has ended
        if cmd in self.commands_in_timeout.keys():
            last_called = self.commands_in_timeout[cmd]
            cmd_timeout = self.command_timeouts[cmd]
            # convert seconds to minutes
            if (round((time.time() - last_called) / 60)) >= cmd_timeout:
                self.commands_in_timeout.pop(cmd)


    def get_time_remaining_in_timeout(self, cmd):
        last_called = self.commands_in_timeout[cmd]
        time_passed = time.time() - last_called
        # convert seconds to minutes
        time_passed = round(time_passed/60)
        time_remaining = self.command_timeouts[cmd] - time_passed
        return time_remaining

    def drink_command(self, username):
        if not self.drink_enabled:
            message = 'Donovan is being responsible for some reason. "drink" command is currently disabled D:'
            return message

        try:
            points = point_utils.get_points(username)
        except KeyError as exception:
            message = "No points yet. Your time will come."
            return message

        drink_cost = 50

        if points < drink_cost:
            message = "You need at least {} points to me drink!".format(drink_cost)
            return message

        points -= drink_cost

        point_utils.set_points(username, points)

        self.put_command_in_timeout('drink')

        message = '{} has purchased a drink token!'.format(username)

        return message


    def do_command(self, e, cmd):
        c = self.connection
        username = e.source.split('!')[0]

        # remove command from timeout dict if the timeout has passed
        self.update_commands_in_timeout(cmd)

        # If command is in time out then dont run command and output message instead
        if cmd in self.commands_in_timeout.keys():
            time_remaining = self.get_time_remaining_in_timeout(cmd)
            message = '{} command has {} mintues remaining before it can be called again.'.format(cmd, time_remaining)
            c.privmsg(self.channel, message)

        # Poll the API to get current game.
        elif cmd == "game":
            r = self.get_request()
            c.privmsg(self.channel, r['display_name'] + ' is currently playing ' + r['game'])

        # Poll the API the get the current status of the stream
        elif cmd == "title":
            r = self.get_request()
            c.privmsg(self.channel, r['display_name'] + ' channel title is currently ' + r['status'])

        # Provide basic information to viewers for specific commands
        elif cmd == "drink":
            message = self.drink_command(username)                
            c.privmsg(self.channel, message)

        elif cmd == 'enable_drink':
            if username == 'sgtsavior14':
                self.drink_enabled = True
                message = 'drink command has been enabled! 50 points to make Donovan drink (!drink)'
                c.privmsg(self.channel, message)

        elif cmd == 'disable_drink':
            if username == 'sgtsavior14':
                self.drink_enabled = False
                self.commands_in_timeout.pop('drink', None)
                message = 'Look at this lightweight... smh. Drink command is now disabled.'
                c.privmsg(self.channel, message)

        elif cmd == 'refund':
            if username == 'sgtsavior14':
                message = ''
                try:
                    cmd_args = e.arguments[0].split()
                    refund_username = cmd_args[1]
                    refund_amount = int(cmd_args[2])
                    points = point_utils.get_points(refund_username)
                    points += refund_amount
                    point_utils.set_points(refund_username, points)
                    message = '{} has been refunded {} points'.format(refund_username, refund_amount)
                except:
                    message = "Invalid refund command! Example: !refund username 50"

                c.privmsg(self.channel, message)

        elif cmd == "schedule":
            message = "This is an example bot, replace this text with your schedule text."            
            c.privmsg(self.channel, message)

        # Show the number of points a user has
        elif cmd == "points":
            try:
                points = point_utils.get_points(username)
                message = "{} has {} points!".format(username, points)
            except KeyError as exception:
                message = "No points yet. Your time will come."
            
            c.privmsg(self.channel, message)

        elif cmd == "gamble":
            message = ''
            amount = ''
            try:
                amount_str = e.arguments[0].split()[1]
                if amount_str != 'all':
                    amount = int(amount_str)
                else:
                    amount = amount_str
            except:
                message = "Invalid gamble command! Example: !gamble 5"
            
            # if no error message then gamble points
            bonus = False
            if not message:
                casino = point_casino.PointCasino(username, amount)
                message = casino.gamble_points()

            if isinstance(message, list):
                if len(message) > 1:
                    padded_msg = ''
                    for msg in message[:-1]:
                        padded_msg += (msg + ' ---- ')
                    message = padded_msg + message[-1]
                else:
                    message = message[0]
            
            c.privmsg(self.channel, message)
            print (message)
            sys.stdout.flush()


        # The command was not recognized
        else:
            c.privmsg(self.channel, "Did not understand command: " + cmd)

def launch_irc_bot(twitch_bot):
    twitch_bot.start()

def launch_chatters_bot(channel, client_id, channel_id):
    '''
    Update active viewers points every minute
    '''

    while True:
        # check if stream is live, if not then skip 
        twitch_api_stream_url = "https://api.twitch.tv/kraken/streams/" + channel_id
        headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        streamer_request = requests.get(twitch_api_stream_url, headers=headers).json()

        if streamer_request.get('stream'):
            # use chatters application to get current users in chat (no api so may break in the future)
            url = 'http://tmi.twitch.tv/group/user/{}/chatters'.format(channel)
            chatter_info = requests.get(url).json()
            viewers_in_chat = chatter_info['chatters']['viewers']
            mods_in_chat = chatter_info['chatters'].get('moderators')

            if mods_in_chat:
                viewers_in_chat.extend(mods_in_chat)

            viewer_data = point_utils.get_viewer_data()
            
            viewer_names = viewer_data.keys()

            current_viewers_dict = {}
            # loop through all viewers in chat and update their points
            for viewer in viewers_in_chat:
                
                if viewer in viewer_names:
                    viewer_data[viewer]['points'] += 1
                    viewer_data[viewer]['total'] += 1

                else:
                    viewer_data[viewer] = {'points': 1, 'total': 1}
                    print ('new user: {}'.format(viewer))
                    sys.stdout.flush()

                # store current users for data purposes
                current_viewers_dict[viewer] = viewer_data[viewer]

            point_utils.update_viewer_data(viewer_data)

            # store current viewers in a file for logging/data purposes
            if current_viewers_dict:
                point_utils.update_current_viewers(current_viewers_dict)

        time.sleep(60)


def main():
    # read params from enviroment variables
    load_dotenv()
    username  = os.getenv('username')
    client_id = os.getenv('client_id')
    token     = os.getenv('token')
    channel   = os.getenv('channel')

    bot = TwitchBot(username, client_id, token, channel)
    
    t1 = threading.Thread(target=launch_irc_bot, args=(bot,))
    t2 = threading.Thread(target=launch_chatters_bot, args=(channel,bot.client_id,bot.channel_id,))

    t1.start()
    t2.start()

    # wait until thread 1 is completely executed 
    t1.join() 
    # wait until thread 2 is completely executed 
    t2.join() 
if __name__ == "__main__":
    main()