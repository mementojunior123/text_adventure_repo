from sys import exit as close_everything
from collections import defaultdict
import json
import os

def return_0():
    return 0

class Game:
    def __init__(self):
        self.state : dict = {'Cash' : 0, 'KeyItems' : []}
        self.inventory : dict = {}
        self.has_visited : dict[int, int] = defaultdict(return_0)
        self.has_visited[3]
        self.room_state : dict[int, dict] = {}
    
    def save(self, file_path = 'default_save.json'):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data : dict = json.load(file)
        except FileNotFoundError:
            return False
        has_visited = {str(key) : self.has_visited[key] for key in self.has_visited}
        data = {
            'game_state' : self.state,
            'room_state' : self.room_state,
            'game_inventory' : self.inventory,
            'visited_rooms' : has_visited,
            'current_room' : room_number,
            'is_filled' : True
        }
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        
        return True
    
    def load(self, file_path = 'default_save.json'):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data : dict = json.load(file)
        except FileNotFoundError:
            print(f'{file_path} not found')
            return False
        
        if not data.get('is_filled', False):
            return True
        
        global room_number
        room_number = data['current_room']
        self.room_state = data['room_state']
        self.inventory = data['game_inventory']
        self.has_visited = defaultdict(lambda : 0)
        for key in data['visited_rooms']:
            self.has_visited[int(key)] = data['visited_rooms'][key]
        self.state = data['game_state']
        return True

    def quit(self):
        print('Goodbye!')
        close_everything()
    
    def print_inventory(self):
        if len(self.inventory) <= 0:
            print("Inventory is empty.")
            return
        for item in self.inventory:
            item_count = self.inventory[item]
            if item_count <= 0: continue
            print(f'{item} ({item_count})')

class Room:
    room_management_funcs = {}
    entry_funcs = {}
    def __init__(self, room_number):
        self.entry_func : function = Room.entry_funcs.get(room_number, None) or Room.enter_default
        self.management_func : function = Room.room_management_funcs.get(room_number, None) or Room.default_manage
        self.room_number = room_number
    
    def manage(self):
        return self.management_func(self)
    
    def enter(self):
        self.entry_func(self)

    def default_manage(self) -> str|int:
        options = room_options[self.room_number]
        if type(options) == str:
            return options
        elif type(options) == int:
            stall()
            print('')
            return options
        option_dict : dict[int, str] = {} 
        for i, option in enumerate(options):
            print(f'{i+1}-{option}')
            option_dict[i + 1] = option
        choice = get_int_choice(len(options))
        print('')
        result = options[option_dict[choice]]
        return result
    
    def enter_default(self):
        if game.has_visited[self.room_number] <= 1:
            txt_to_display = room_text[self.room_number]
        else:
            second_arrival_text = room_text_second_arrival.get(self.room_number, False)
            txt_to_display = second_arrival_text if second_arrival_text else room_text[self.room_number]
                
        
        if type(txt_to_display) == str:
            print(txt_to_display)
        else:
            txt_to_display : list[str]
            for part in txt_to_display:
                print(part, end = '')
                stall()
    
    def enter_room_1(self):
        if game.has_visited[1] <= 1:
            self.enter_default()
        else:
            print('You are back at the crossroads. What now?')
    
    def enter_room_2(self):
        if game.has_visited[2] <= 1:
            game.room_state[2] = {'items_left' : ['bat', 'flashlight', 'radio']}

        if len(game.room_state[2]['items_left']) == 0:
            print("You encountered a shop. Unfortunately, there's nothing left to buy. I wonder why...")

        elif game.state['Cash'] > 0:
            self.enter_default()
        else:
            print('''You encountered a mysterious shop with no one there. They have a few items on sale. 
Unfortunately, you dont't have any money left. What do you do?''')
            
    def manage_room_2(self):

        item_count = len(game.room_state[2]['items_left'])
        if item_count == 0:
            stall()
            return 1

        elif game.state['Cash'] > 0:
            print('''1-Buy an item\n2-Steal something\n3-Save your money and go back''')
            choice = get_int_choice(3)
            option_chosen = ['buy', 'steal', 'save'][choice - 1]
        else:
            print('1-Steal something\n2-Go back')
            choice = get_int_choice(2)
            option_chosen = ['steal', 'save'][choice - 1]

        if option_chosen == 'save':
            return 1
        
        item_conversion_dict = {'bat' : 'A wooden bat', 'flashlight' : 'A flaslight', 'radio' : 'A radio'}

        prompt_text = 'What do you buy?' if option_chosen == 'buy' else 'What do you steal?'

        print(prompt_text)
        option_dict = {}
        for i, item in enumerate(game.room_state[2]['items_left']):
            print(f'{i + 1}-{item_conversion_dict[item]}')
            option_dict[i + 1] = item
        choice = get_int_choice(item_count)
        item_to_get = option_dict[choice]
        game.room_state[2]['items_left'].remove(item_to_get)
        if item_to_get not in game.inventory:
            game.inventory[item_to_get] = 0
        game.inventory[item_to_get] += 1
        if option_chosen == 'buy':
            print('You grabbed the item and left the correct amount of money on the counter.')
            game.state['Cash'] -= 1
        else:
            print('You snuck up to the stand, made sure no one was looking... And grabbed the item with seemingly no one noticing you.')
            print("Let's hope this dosen't backfire...")
        stall()
        return 1    
    
    def enter_room_13(self):
        if 'Floor1Key1' not in game.state['KeyItems']:
            game.state['KeyItems'].append('Floor1Key1')
        self.enter_default()
    
    
    def enter_room_14(self):
        if 'Floor1Key1' in game.state['KeyItems']:
            if game.has_visited[16] == 0:
                self.enter_default()
    
        elif 'BasementKey1' in game.state['KeyItems']: 
            print('You try the key you grabbed on the first floor. Unfortunately, it is not the right key.')
        else:
            print('Its locked. You need a key to get in there.')
    
    def manage_room_14(self):
        if game.has_visited[16] == 0:
            stall()
        if 'Floor1Key1' in game.state['KeyItems']: 
            return 16
        else:
            return 12
    
    
    def enter_room_15(self):
        if 'BasementKey1' in game.state['KeyItems']: 
            self.enter_default()
        elif 'Floor1Key1' in game.state['KeyItems']: 
            print('You try the key you grabbed on the ground floor. Unfortunately, it is not the right key.')
        else:
            print('Its locked. You need a key to get in there.')
    
    def manage_room_15(self):
        stall()
        if 'BasementKey1' in game.state['KeyItems']: 
            return 17
        else:
            return 12
    
    def enter_room_16(self):
        if 'BasementKey1' not in game.state['KeyItems']:
            game.state['KeyItems'].append('BasementKey1')
        self.enter_default()
    
    def enter_room_18(self):
        if game.has_visited[18] > 1:
            print(room_text_second_arrival[18])
            return
        
        if 'radio' in game.inventory:
            print('''You tried using the radio you got earlier to get help.\nNo one picked up...''')
        else:
            print(room_text[18])
    
    def enter_room_19(self):
        if game.has_visited[19] > 1:
            print(room_text_second_arrival[19])
            return
        
        did_fight_door = game.has_visited[9]
        if 'bat' in game.inventory:
            if did_fight_door:
                print('''With a bat by your side, you can surely force this door open, right?
...
The score is 2-0 now.''')
            else:
                print('You took a few swings at the door, but your attacks barely left a scratch.')
        else:
            if did_fight_door:
                print('''Your past experiences with doors tells you this isn't going to work.''')
            else:
                print(room_text[19])
    
    def manage_room_21(self):
        print('\n')
        stall()
        return 22
        

Room.room_management_funcs = {2 : Room.manage_room_2, 14 : Room.manage_room_14, 15 : Room.manage_room_15}
Room.entry_funcs = {2 : Room.enter_room_2, 13 : Room.enter_room_13, 14 : Room.enter_room_14, 15: Room.enter_room_15,
16 : Room.enter_room_16}


room_text = {
    1 : '''You encountered a crossing. What do you do?''',
    2 : '''You encountered a mysterious shop. They have a few items on sale. 
You don't have much money, so you can only buy one of them.
What do you do?''',
    3 : '''There's an abandoned mansion up ahead. Should you investigate?''',
    4 : '''Are you sure? You might miss out on the entire game...''',
    5 : '''Unfortunately for you, you don't really have a choice.''',
    6 : '''Despite your initial hesitations, you decided to investigate. Will you regret this choice? Only time will tell...''',
    7 : '''You decided to investigate. Will you regret this choice? Only time will tell...''',
    8 : '''You arrived at the mansion. You walk up to the front door and try to open it. However, it's locked. What do you do?''',
    9 : '''You tried to force the door open. Unfortunately, for you, the door won't budge. 
Not one to give up so quickly, you start fighting with the door.
...
The door won.''',
    10: '''You look around for a window to break and find one. 
Unfortunatively for you, it's way too small for you to fit in.
Besides, you don't exactly want to draw attention to what you are doing.''',
    11: '''You looked around the house for a way in. 
While the front door was well maintained, the backdoor had already fallen off on its own.
You made your way to the house's living room.''',
    12: 'The mansion is huge, and there are quite a few things worth taking a look at. Where do you go?',
    13: 'You searched around and found a key. Maybe it could be useful for something?',
    14: 'You used the key you found and went to the first floor.',
    15: '''You used the second key you found on the basement door. As you turn the doorknob, you question why you are doing this.
But you choose to push on anyways. You didn't come this far just to turn around, right?''',
    16: '''You searched around and found another key.
You feel like you might know what to do with it.''',
    17: '''As you take your first steps into the basement, you already start regretting your decision.
But before you can consider getting out...
*BLAM!*
The door closes in on you. Even worse, it's also locked on the inside...
...
Looks like you only have one way forwards. Unless...''',
    18: '''You try to call for help with yout voice. Unfortunately, no one is around to hear you.
Looks like you are on your own...''',
    19: '''You try to force the door open. Unfortunatively, it's stronger than you expected and dosent even budge.''',
    20: '''After a moment of thought, you come to the conclusion that the only way you can hope to get out is by going further in.
While this seems like a very bad idea... It looks like the only way out.''',
    21: '''---------ACT 1 - Into the dark---------'''
}
room_text_second_arrival = {
    1 : '''You are back at the crossing. What now?''',
    8 : 'You think about another way to get into the mansion.',
    9 : '''You have a feeling this won't be very productive.''',
    10: '''This can't be the right way. Breaking the window would be way too loud...''',
    12: '''What do you investigate?''',
    13: '''You couldn't find anything interesting.''',
    16: '''You couldn't find anything interesting.''',
    18: '''This isn't going to work...''',
    19: '''That's not going to work.''',

}
room_options = {
    1 : {'Go left' : 2, 'Go right' : 3},
    2 : {'Go back' : 1},
    3 : {'Investigate' : 7,  '''Don't investigate''' : 4},
    4 : {'Yes' : 5, 'No' : 6},
    5 : 6,
    6 : 8,
    7 : 8,
    8 : {'Force the door open' : 9, 'Break a window' : 10, 'Try to find a way around' : 11},
    9 : 8,
    10: 8,
    11: 12,
    12: {'The 1st floor' : 14, 'The ground floor' : 13, 'The basement' : 15},
    13: 12,
    14: 16,
    15: 17,
    16: 12, 
    17: {'Call for help' : 18, 'Investigate the basement' : 20, 'Break the door open' : 19},
    18: 17,
    19: 17,
    20 : 21,
    21 : 'END'

    

}




def get_int_choice(option_count : int) -> int:
    valid = [str(i + 1) for i in range(option_count)]
    while True:
        result = input('Selection : ')
        if result in valid:
            return int(result)       
        elif result == "cmd":
            enter_command()
            
        elif len(result) == 0:
            print(f'Invalid. Number must range from 1 to {option_count}. To see run a command, type "cmd" or prefix it with "/".')
        elif result[0] == '/':
            parse_command(result)
        else:
            print(f'Invalid. Number must range from 1 to {option_count}. To see run a command, type "cmd" or prefix it with "/".')

def enter_command():
    parse_command(input("Command : "))

def parse_command(message : str):
    if message[0] == '/':
        message = message[1:]
    command = message
    result = is_valid_command(command)
    if result == False:
        print(f'"{command}" is not a recognized command. To see a list of all commands, use help.')
        return False
    elif result == True:
        process_command(command)
        return True
    elif type(result) == str:
        print(result)
        return False
    else:
        print('Something went wrong. Please try again.')

command_list = ['stop', 'exit', 'quit', 'exit', 'help']

def is_valid_command(message : str):
    message = message.lower()
    words = message.split()
    command = words[0]
    args = words[1:]
    arg_count = len(args)
    default_error = f'Command was formatted incorrectly. To see how to format the command, use "help {command}"'
    match command:
        case 'stop'|'end'|'quit'|'exit':
            return True
        
        case 'check':
            if arg_count == 0:
                return default_error
            thing_to_check = args[0]
            match thing_to_check:
                case 'inventory':
                    return True
                case _:
                    return f'"check {thing_to_check}" isnt valid. To see how to format the command, use "help {command}"'

        case 'help':
            if arg_count == 0:
                return True
            command_to_help = args[0]
            if command_to_help not in command_list:
                return f'{command_to_help} is not a valid command. To see a list of all commands, use "help".'
            return True
        
        case _:
            return False

def process_command(message : str):
    message = message.lower()
    words = message.split()
    command = words[0]
    args = words[1:]
    arg_count = len(args)
    default_error = 'Something went wrong. Please try again.'

    match command:
        case 'stop'|'end'|'quit'|'exit':
            print('Are you sure you want to quit? Type "Y" or "yes" if you want to quit.')
            result = input().lower()
            if result == 'y' or result == 'yes':
                sucsess = game.save(f'saves/{current_save_file}.json')
                if sucsess:
                    print('Data saved sucessfully!')
                else:
                    print('Data failed to save...')
                game.quit()
        case 'check':
            thing_to_check = args[0]
            match thing_to_check:
                case 'inventory':
                    game.print_inventory()
                case _:
                    print(default_error)
        case 'help':
            if arg_count == 0:
                print('quit, stop, end, exit - Close the game')
                print('For more detailed help about a command, use "help <command>"')
                return
            command_to_help = args[0]
            match command_to_help:
                case 'help':
                    print('For more detailed help about a command, use "help <command>"')
                case 'stop'|'end'|'quit'|'exit':
                    print('Use to quit the game.')
        case _:
            print(default_error)

def stall(stall_text = '(Enter to continue.) -->'):
    input(stall_text)

game = Game()
game.state['Cash'] = 1
room_number = 1
current_save_file : str|None = None
decision = input('Enter "new save" to make a new save. Enter anything else to continue a save.\n').lower()
if decision != "new save":
    saves : list[str]
    for path, dirs, files in os.walk('saves'):
        saves = files
        break
    saves = [os.path.splitext(sv)[0] for sv in saves]
    if saves:
        print("Here are the registered saves:")
        for index, save in enumerate(saves):
            print(f'{index + 1}. {save}')
        while True:
            save_choice = input("What save do you want to load?\n")
            if save_choice == 'new save' or save_choice in saves:
                break
            try:
                save_index = int(save_choice) - 1
                if save_index <= 0:
                    raise ValueError
                save_choice = saves[save_index]
            except ValueError:
                print("The save does not exist!")
            except IndexError:
                print("The save does not exist!")
            else:
                break
        if save_choice != 'new save':
            result = game.load(f'saves/{save_choice}.json')
            if result == True:
                current_save_file = save_choice
                game.has_visited[room_number] -= 1
                print("Save was sucessfully loaded.")
                stall()
            else:
                print(f'Save {save_choice} could not be loaded...')

if current_save_file is None:
    while True:
        save_name = input("What will this new save be called?\n")
        if save_name == 'new save': print("Invalid!"); continue
        try:
            with open(f'saves/{save_name}.json', 'x') as f:
                pass
        except FileExistsError:
            print("This save already exists!")
        else:
            break
    print("New save was created; Starting game!")
    stall()
current_save_file : str
while True:
    room = Room(room_number)
    game.has_visited[room_number] += 1
    room.enter()
    result = room.manage()
    
    if type(result) == int:
        room_number = result
    elif result == 'END':
        break
        
stall()    
print('DEMO END')