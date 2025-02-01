from time import sleep
from sys import exit as close_everything
from collections import defaultdict
import json
import os
from typing import Callable, Any, TypedDict, Union, TypeAlias
from enum import Enum

ITEM_IDS : list[str] = ['bat', 'flashlight', 'radio', 'empty_flashlight']
item_name_dict : dict[str, str] = {
'bat' : 'Wooden Bat',
'flashlight' : "Flashlight",
'radio' : 'Radio',
'empty_flaslight' : 'Expired Flashlight'
}
item_description_dict = {
'bat' : 'A wooden bat',
'flashlight' : 'A flaslight',
'radio' : 'A radio',
'empty_flashlight' : 'A flashlight with no batteries'
}
def clear_console(method : int = 1):
    if method == 1:
        print("\033c", end="")
    elif method == 2:
        x = 3
        print(f"\033[H\033[{x}J", end="")
    elif method == 3:
        print("\n" * 50)
    else:
        os.system('cls' if os.name == 'nt' else 'clear')

AnyJson = Union[str, int, float, bool, None, dict[str, 'AnyJson'], list['AnyJson']]
ManagmentFunction : TypeAlias = Callable[[], str|int]
EntryFunction : TypeAlias = Callable[[], None]

class GameState(TypedDict):
    '''global_state : dict[str, AnyJson]
    room_state : dict[int|str, dict[str, AnyJson]]
    game_inventory : dict[str, int]
    visited_rooms : dict[int|str, int]
    current_room : int'''
    global_state : dict[str, AnyJson]
    room_state : dict[int|str, dict[str, AnyJson]]
    game_inventory : dict[str, int]
    visited_rooms : dict[int|str, int]
    current_room : int
    temp_data : dict[str, AnyJson]

class SaveFile(TypedDict):
    '''current_state : GameState
    is_filled : int
    perma_state : dict[str, AnyJson]
    checkpoints : dict[str, GameState]'''
    current_state : GameState
    is_filled : int
    perma_state : dict[str, AnyJson]
    checkpoints : dict[str, GameState]

class RoomType(Enum):
    STANDARD = 'Standard'
    CHECKPOINT = 'Checkpoint'

class OptionalRoomInfo(TypedDict, total=False):
    second_arrival_text : str
    extra_info : dict[str, Any]

class RoomInfo(OptionalRoomInfo):
    entry_text : str
    options : dict[str, int]|int|str
    type : RoomType|str

class EndingInfo(TypedDict):
    ending_text : str
    ending_name : str
    retryable : bool
    retry_checkpoint : str

class Game:
    def __init__(self):
        self.global_state : dict[str, AnyJson] = {'Cash' : 1, 'KeyItems' : []}
        self.inventory : dict[str, int] = {}
        self.has_visited : dict[int, int] = defaultdict(lambda : 0)
        self.room_state : dict[int, dict] = {}
        self.perma_state : dict[str, AnyJson] = {}
        self.checkpoints : dict[str, GameState] = {}
        self.room_number : int = 0
        self.temp_data : dict[str, AnyJson] = {}

    def reset(self):
        self.global_state = {'Cash' : 1, 'KeyItems' : []}
        self.inventory = {}
        self.has_visited = defaultdict(lambda : 0)
        self.room_state = {}
        self.perma_state = {}
        self.checkpoints = {}
        self.room_number = 0
        self.temp_data = {}

    def save(self, file_path = 'saves/default_save.json'):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                pass
        except FileNotFoundError:
            print(f'File path "{file_path}" not found!')
            return False

        data : SaveFile = self._get_data()
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        return True
    
    def load(self, file_path = 'saves/default_save.json'):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data : dict = json.load(file)
        except FileNotFoundError:
            print(f'{file_path} not found')
            return False

        is_filled : bool|int|None = data.get('is_filled', None)
        if not data:
            print("Save is empty!")
            return True
        elif not is_filled:
            if file_path[:6] == 'saves/':
                file_path = file_path[6:]
            print(f"{file_path} is not a valid save file - Wiping data!")
            return True
        elif is_filled < 3:
            print("Save is outdated and data cannot be recovered - Wiping data!")
            return True


        return self._load_data(data)
      
    def _get_data(self) -> SaveFile:
        current_state = self._get_game_state()
        data : SaveFile = {
            'current_state' : current_state,
            'is_filled' : 3,
            'perma_state' : self.perma_state,
            'checkpoints' : self.checkpoints
        }
        return data

    def _get_game_state(self) -> GameState:
        has_visited = {str(key) : self.has_visited[key] for key in self.has_visited}
        current_state : GameState = {
            'global_state' : self.global_state,
            'room_state' : self.room_state,
            'game_inventory' : self.inventory,
            'visited_rooms' : has_visited,
            'current_room' : self.room_number,
            'temp_data' : self.temp_data
        }
        return current_state
    
    def _load_data(self, data : SaveFile) -> bool:
        current_state : GameState = data['current_state']
        self._load_game_state(current_state)

        self.perma_state = data['perma_state']
        self.checkpoints = data['checkpoints']
        return True

    def _load_game_state(self, state : GameState):
        self.room_number = state['current_room']
        self.room_state = {int(key) : state['room_state'][key] for key in state['room_state']}
        self.inventory = state['game_inventory']
        self.has_visited = defaultdict(lambda : 0)
        for key in state['visited_rooms']:
            self.has_visited[int(key)] = state['visited_rooms'][key]
        self.global_state = state['global_state']
        self.temp_data = state['temp_data']

    def make_checkpoint(self, checkpoint_name : str) -> bool:
        self.checkpoints[checkpoint_name] = self._get_game_state()
        return True

    def restore_checkpoint(self, checkpoint_name : str) -> bool:
        if checkpoint_name not in self.checkpoints:
            return False
        self._load_game_state(self.checkpoints[checkpoint_name])
        return True

    def quit(self):
        print('Goodbye!')
        stall()
        close_everything()

    def print_inventory(self):
        if len(self.inventory) <= 0:
            print("Inventory is empty.")
            return
        for item in self.inventory:
            item_count = self.inventory[item]
            item_name = item_description_dict[item]
            if item_count <= 0: continue
            print(f'{item_name} ({item_count})' if item_count >= 1 else f'{item_name}')

class Room:
    def __init__(self, room_number : int):
        self.room_number : int = room_number
        self.data : RoomInfo = room_data[room_number]
        self.entry_func : EntryFunction = self.get_entry_func()
        self.management_func : ManagmentFunction = self.get_management_func()

    def get_entry_func(self) -> EntryFunction:
        entry_func : EntryFunction = None
        entry_func = getattr(Room, f'enter_room_{self.room_number}', None)
        if entry_func is None:
            entry_func = Room.enter_default
        return entry_func

    def get_management_func(self) -> ManagmentFunction:
        management_func : ManagmentFunction = None
        management_func = getattr(Room, f'manage_room_{self.room_number}', None)
        if management_func is None:
            management_func = Room.default_manage
        return management_func

    def manage(self) -> str|int:
        return self.management_func(self)

    def enter(self) -> None:
        self.entry_func(self)

    def default_manage(self) -> str|int:
        if self.data['type'] == RoomType.CHECKPOINT:
            return self._manage_checkpoint()
        options = self.data['options']
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
        if self.data['type'] == RoomType.CHECKPOINT:
            return self._enter_checkpoint()
        if game.has_visited[self.room_number] <= 1:
            txt_to_display = self.data['entry_text']
        else:
            second_arrival_text = self.data.get('second_arrival_text', False)
            txt_to_display = second_arrival_text if second_arrival_text else self.data['entry_text']


        if type(txt_to_display) == str:
            print(txt_to_display)
        else:
            print('(Enter to continue.) -->')
            txt_to_display : list[str]
            for part in txt_to_display:
                print(part, end = '')
                if part == txt_to_display[-1]: stall(); break
                if part == txt_to_display[-1]: stall(); print(''); break
                stall("")

    def _enter_checkpoint(self):
        if game.has_visited[self.room_number] > 1:
            return
        print(self.data['entry_text'])

    def _manage_checkpoint(self) -> str|int:
        options = self.data['options']
        if game.has_visited[self.room_number] > 1:
            return options
        game.room_number = self.data['options']
        game.make_checkpoint(self.data['extra_info']['checkpoint_name'])
        stall()
        print('')
        game.room_number = self.room_number
        return options

    def enter_room_2(self):
        if game.has_visited[2] <= 1:
            game.room_state[2] = {'items_left' : ['bat', 'flashlight', 'radio']}

        if len(game.room_state[2]['items_left']) == 0:
            print("You encountered a shop. Unfortunately, there's nothing left to buy. I wonder why...")

        elif game.global_state['Cash'] > 0:
            self.enter_default()
        else:
            print('''You encountered a mysterious shop with no one there. They have a few items on sale.
Unfortunately, you dont't have any money left. What do you do?''')

    def manage_room_2(self):

        item_count = len(game.room_state[2]['items_left'])
        if item_count == 0:
            stall()
            return 1

        elif game.global_state['Cash'] > 0:
            print('''1-Buy an item\n2-Steal something\n3-Save your money and go back''')
            choice = get_int_choice(3)
            option_chosen = ['buy', 'steal', 'save'][choice - 1]
        else:
            print('1-Steal something\n2-Go back')
            choice = get_int_choice(2)
            option_chosen = ['steal', 'save'][choice - 1]

        if option_chosen == 'save':
            return 1

        item_description_dict = {'bat' : 'A wooden bat', 'flashlight' : 'A flaslight', 'radio' : 'A radio'}

        prompt_text = 'What do you buy?' if option_chosen == 'buy' else 'What do you steal?'

        print(prompt_text)
        option_dict = {}
        for i, item in enumerate(game.room_state[2]['items_left']):
            print(f'{i + 1}-{item_description_dict[item]}')
            option_dict[i + 1] = item
        choice = get_int_choice(item_count)
        item_to_get = option_dict[choice]
        game.room_state[2]['items_left'].remove(item_to_get)
        if item_to_get not in game.inventory:
            game.inventory[item_to_get] = 0
        game.inventory[item_to_get] += 1
        if option_chosen == 'buy':
            print('You grabbed the item and left the correct amount of money on the counter.')
            game.global_state['Cash'] -= 1
        else:
            print('You snuck up to the stand, made sure no one was looking... And grabbed the item with seemingly no one noticing you.')
            print("Let's hope this dosen't backfire...")
        stall()
        return 1

    def enter_room_13(self):
        if 'Floor1Key1' not in game.global_state['KeyItems']:
            game.global_state['KeyItems'].append('Floor1Key1')
        self.enter_default()

    def enter_room_14(self):
        if 'Floor1Key1' in game.global_state['KeyItems']:
            if game.has_visited[16] == 0:
                self.enter_default()

        elif 'BasementKey1' in game.global_state['KeyItems']:
            print("You try the key you grabbed on the first floor. Unfortunately, it doesn't seem to be the right one.")
        else:
            print('Its locked. You need a key to get in there.')

    def manage_room_14(self):
        if game.has_visited[16] == 0:
            stall()
        if 'Floor1Key1' in game.global_state['KeyItems']:
            return 16
        else:
            return 12

    def enter_room_15(self):
        if 'BasementKey1' in game.global_state['KeyItems']:
            self.enter_default()
        elif 'Floor1Key1' in game.global_state['KeyItems']:
            print("You try the key you grabbed on the ground floor. Unfortunately, it doesn't seem to be the right one.")
        else:
            print('Its locked. You need a key to get in there.')

    def manage_room_15(self):
        stall()
        if 'BasementKey1' in game.global_state['KeyItems']:
            return 17
        else:
            return 12

    def enter_room_16(self):
        if 'BasementKey1' not in game.global_state['KeyItems']:
            game.global_state['KeyItems'].append('BasementKey1')
        self.enter_default()

    def enter_room_18(self):
        if game.has_visited[18] > 1:
            print(self.data['second_arrival_text'])
            return

        if 'radio' in game.inventory:
            print('''You tried using the radio you got earlier to get help.\nNo one picked up...''')
        else:
            print(self.data['entry_text'])

    def enter_room_19(self):
        if game.has_visited[19] > 1:
            print(self.data['second_arrival_text'])
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
                print(self.data['entry_text'])

    def manage_room_22(self):
        options : dict[str, int] = {'Track back to find a light source' : 23,  'Go downstairs in the dark' : 24}
        if 'flashlight' in game.inventory:
            options['Use your flashlight to light up the path'] = 25
        option_dict : dict[int, str] = {}
        for i, option in enumerate(options):
            print(f'{i+1}-{option}')
            option_dict[i + 1] = option
        choice = get_int_choice(len(options))
        print('')
        result = options[option_dict[choice]]
        return result

room_data : dict[int, RoomType] = {
    0 : {
'type' : RoomType.STANDARD,
'entry_text' : '''---------ACT 0 - Prologue---------''',
'options' : 1,
},

    1 : {
'type' : RoomType.STANDARD,
'entry_text' : '''You encountered a crossing. What do you do?''',
'second_arrival_text' : '''You are back at the crossroads. What now?''',
'options' : {'Go left' : 2, 'Go right' : 3},
},

    2 : {
'type' : RoomType.STANDARD,
'entry_text' : '''You encountered a mysterious shop. They have a few items on sale.
You don't have much money, so you can only buy one of them.
What do you do?''',
'options' : {'Go back' : 1},
},

    3 : {
'type' : RoomType.STANDARD,
'entry_text' : '''There's an abandoned mansion up ahead. Should you investigate?''',
'options' : {'Investigate' : 7,  '''Don't investigate''' : 4},
},

    4 : {
'type' : RoomType.STANDARD,
'entry_text' : '''Are you sure? You might miss out on the entire game...''',
'options' : {'Yes' : 5, 'No' : 6}
},

    5 : {
'type' : RoomType.STANDARD,
'entry_text' : '''Unfortunately for you, you don't really have a choice.''',
'options' : 6
},

    6 : {
'type' : RoomType.STANDARD,
'entry_text' : '''Despite your initial hesitations, you decided to investigate. Will you regret this choice? Only time will tell...''',
'options' : 8
},

    7 : {
'type' : RoomType.STANDARD,
'entry_text' : '''You decided to investigate. Will you regret this choice? Only time will tell...''',
'options' : 8
},

    8 : {
'type' : RoomType.STANDARD,
'entry_text' : '''You arrived at the mansion. You walk up to the front door and try to open it. However, it's locked. What do you do?''',
'second_arrival_text' : 'You think about another way to get into the mansion.',
'options' : {'Force the door open' : 9, 'Break a window' : 10, 'Try to find a way around' : 11},
},

    9 : {
'type' : RoomType.STANDARD,
'entry_text' : '''You tried to force the door open. Unfortunately, for you, the door won't budge.
Not one to give up so quickly, you start fighting with the door.
...
The door won.''',
'second_arrival_text' : '''You have a feeling this won't be very productive.''',
'options' : 8
},

    10 : {
'type' : RoomType.STANDARD,
'entry_text' : '''You look around for a window to break and find one.
Unfortunatively for you, it's way too small for you to fit in.
Besides, you don't exactly want to draw attention to what you are doing.''',
'second_arrival_text' : '''This can't be the right way. Breaking the window would be way too loud...''',
'options' : 8
},

    11 : {
'type' : RoomType.STANDARD,
'entry_text' : '''You looked around the house for a way in.
While the front door was well maintained, the backdoor had already fallen off on its own.
You made your way to the house's living room.''',
'options' : 12
},

    12 : {
'type' : RoomType.STANDARD,
'entry_text' : 'The mansion is huge, and there are quite a few things worth taking a look at. Where do you go?',
'second_arrival_text' : '''What do you investigate?''',
'options' : {'The 1st floor' : 14, 'The ground floor' : 13, 'The basement' : 15},
},

    13 : {
'type' : RoomType.STANDARD,
'entry_text' : 'You searched around and found a key. Maybe it could be useful for something?',
'second_arrival_text' : '''You couldn't find anything interesting.''',
'options' : 12
},

    14 : {
'type' : RoomType.STANDARD,
'entry_text' : 'You used the key you found and went to the first floor.',
'options' : 16
},

    15 : {
'type' : RoomType.STANDARD,
'entry_text' : '''You used the second key you found on the basement door. As you turn the doorknob, you question why you are doing this.
But you choose to push on anyways. You didn't come this far just to turn around, right?''',
'options' : 17
},

    16 : {
'type' : RoomType.STANDARD,
'entry_text' : '''You searched around and found another key.
You feel like you might know what to do with it.''',
'second_arrival_text' : '''You couldn't find anything interesting.''',
'options' : 12
},

    17 : {
'type' : RoomType.STANDARD,
'entry_text' :  [
'''As you take your first steps into the basement, you already start regretting your decision.
But before you can even consider getting out...\n''',
'''*BLAM!*\n''',
'''The door closes in on you. Even worse, it's also locked on the inside...\n''',
'''...\n''',
'''Looks like you only have one way forwards. Unless...\n'''
],
'second_arrival_text' : '''What now?''',
'options' : {'Call for help' : 18, 'Investigate the basement' : 20, 'Break the door open' : 19},
},

    18 : {
'type' : RoomType.STANDARD,
'entry_text' :'''You try to call for help with yout voice. Unfortunately, no one is around to hear you.
Looks like you are on your own...''',
'second_arrival_text' : '''This isn't going to work...''',
'options' : 17
},

    19 : {
'type' : RoomType.STANDARD,
'entry_text' : '''You try to force the door open. Unfortunatively, it's stronger than you expected and dosent even budge.''',
'second_arrival_text' : '''That's not going to work.''',
'options' : 17
},

    20 : {
'type' : RoomType.STANDARD,
'entry_text' : '''After a moment of thought, you come to the conclusion that the only way you can hope to get out is by going further in.
While this seems like a very bad idea... It looks like the only way out.''',
'options' : 21
},

    21 : {
'type' : RoomType.STANDARD,
'entry_text' :  '''---------ACT 1 - Into the dark---------''',
'options' : 26
},

    26 : {
'type' : RoomType.CHECKPOINT,
'entry_text' : 'New checkpoint!',
'options' : 22,
'extra_info' : {'checkpoint_name' : 'Act1Start'}
},

    22 : {
'type' : RoomType.STANDARD,
'entry_text' : [
'''You take a few more steps down the stairs leading to the basement door.\n''',
'''The deeper you go, the darker it gets. Eventually, you can barely see anything.\n''',
'''Going down the stairs in complete darkness is a terrible idea, but unless you can find a way to light the path, you don't really have an option.\n'''
],
'options' : {'Track back to find a light source' : 23,  'Go downstairs in the dark' : 24, 'Use your flashlight to light up the path' : 25},
},

    23 : {
'type' : RoomType.STANDARD,
'entry_text' : '''You track back to find a light source and eventually find one.
You use the newfound light to lighten up the path ahead.''',
'options' : 27
},

    24 : {
'type' : RoomType.STANDARD,
'entry_text' : [
    'Despite not being able to see anything, you choose to push on anyways.\n',
    '''Eventually, you can't even see the steps you're going wakling on.\n''',
    '''Your pace slows down to a crawl as you try to avoid falling.\n''',
    '''Unfortunately for you, you step on a crack that was concealed in the darkness...\n''',
    '''And you tumble all the way down the stairs.\n'''
],
'options' : 'ENDING BADA1',
},

    25 : {
'type' : RoomType.STANDARD,
'entry_text' : '''You use the flashlight you grabbed earlier to lighten up the path.''',
'options' : 27
},

    27 : {
'type' : RoomType.STANDARD,
'entry_text' : [
'''As you descend further, you notice that the stairs are slowly deteriorating.''',
],
'options' : 28
},

    28 : {
'type' : RoomType.STANDARD,
'entry_text' : '''... (TBD)''',
'options' : 'END'
},
}

ending_data : dict[str, EndingInfo] = {
'BADA1' : {
'ending_name' : 'Bad Ending: (Litterally) Fallen',
'ending_text' : '''That wasn't very bright...''',
'retryable' : True,
'retry_checkpoint' : 'Act1Start'
}
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

command_list = ['stop', 'exit', 'quit', 'exit', 'help', 'check']

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
                print('check - Check something')
                print('For more detailed help about a command, use "help <command>"')
                return
            command_to_help = args[0]
            match command_to_help:
                case 'help':
                    print('For more detailed help about a command, use "help <command>"')
                case 'stop'|'end'|'quit'|'exit':
                    print('Use to quit the game.')
                case 'check':
                    print('Use check <something> to check something. You can try to check your inventory.')
        case _:
            print(default_error)

def stall(stall_text = '(Enter to continue.) -->'):
    input(stall_text)

game = Game()
current_save_file : str|None = None
if not os.path.isdir('saves'):
    try:
        os.makedirs('saves')
    except FileExistsError:
        os.remove('saves')
        os.makedirs('saves')

def main():
    global current_save_file, game
    decision = input('Enter "new save" to make a new save. Enter anything else to continue a save.\n').lower()
    if decision != "new save":
        saves : list[str] = []
        for path, dirs, files in os.walk('saves'):
            saves = files
            break
        saves = [os.path.splitext(sv)[0] for sv in saves]
        if '.gitkeep' in saves: saves.remove('.gitkeep')
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
                    if save_index < 0:
                        raise ValueError
                    save_choice = saves[save_index]
                except ValueError as e:
                    print("The save does not exist!")
                except IndexError as e:
                    print("The save does not exist!")
                else:
                    break
            if save_choice != 'new save':
                result = game.load(f'saves/{save_choice}.json')
                if result == True:
                    current_save_file = save_choice
                    game.has_visited[game.room_number] -= 1
                    print("Save was sucessfully loaded.")
                    stall()
                else:
                    print(f'Save {save_choice} could not be loaded...')
                    print('Making a new save file...')
        else:
            print("There are no registered save files!")
            print('Making a new save file...')

    if current_save_file is None:
        allow_list : list[str] = ' -_'
        while True:
            save_name = input("What will this new save be called?\n")
            if not all([character in allow_list or character.isalnum() for character in save_name]): print("Invalid! (Invalid character was used)"); continue
            if len(save_name) > 40: print("Invalid! (Save name is max. 40 lines)"); continue
            if save_name == 'new save': print("Invalid! (Cannot use this save name)"); continue
            try:
                with open(f'saves/{save_name}.json', 'x') as f:
                    json.dump({}, f)
            except FileExistsError:
                print("This save already exists!")
            else:
                break
        current_save_file = save_name
        print("New save was created; Starting game!")
        stall()
    clear_console()
    while True:
        while True:
            room = Room(game.room_number)
            game.has_visited[game.room_number] += 1
            room.enter()
            room_result : str|int = room.manage()

            if type(room_result) == int:
                game.room_number = room_result
            elif type(room_result) == str:
                break
            game.temp_data.clear()

        if type(room_result) != str:
            print('DEMO END - Your progress from this session will not be saved!')
            response : str = input("Do you want to play again? Input Y/yes to restart. This will wipe your save.\n").lower()
            if response == 'y' or response == 'yes':
                game.reset()
                continue
            print('Goodbye!')
            stall()
            close_everything()

        words = room_result.split()
        if words[0] == 'END':
            print('DEMO END - Your progress from this session will not be saved!')
            response : str = input("Do you want to play again? Input Y/yes to restart. This will wipe your save.\n").lower()
            if response == 'y' or response == 'yes':
                game.reset()
                continue
            print('Goodbye!')
            stall()
            close_everything()

        if words[0] == 'ENDING':
            clear_console()
            ending_code = words[1]
            ending_info = ending_data[ending_code]
            ending_text = ending_info['ending_text']
            ending_name = ending_info['ending_name']
            print(ending_text)
            print(ending_name)
            if ending_info['retryable']:
                stall()
                response : str = input('Input "quit" to exit the game. Input anything else to go back to a checkpoint and retry.\n').lower()
                if response != 'quit':
                    restore_result : bool = game.restore_checkpoint(ending_info['retry_checkpoint'])
                    if restore_result == False: print('Checkpoint could not be loaded- Terminating session!')
                    else:
                        print("Checkpoint loaded!")
                        stall()
                        clear_console()
                        continue
            print('DEMO END - Your progress from this session will not be saved!')
            stall()
            response : str = input("Do you want to play again from the start? Input Y/yes to restart. This will wipe your save.\n").lower()
            if response == 'y' or response == 'yes':
                game.reset()
                clear_console()
                continue
            print('Goodbye!')
            stall()
            close_everything()

main()