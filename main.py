from time import sleep
from sys import exit as close_everything
from collections import defaultdict
import json
import os
from typing import Callable, Any, TypedDict, Union, TypeAlias, Literal
from enum import Enum

SAVE_VERSION = 7

AnyJson : TypeAlias = Union[str, int, float, bool, None, dict[str, 'AnyJson'], list['AnyJson']]
ItemCode : TypeAlias = str
class ItemCodes(Enum):
    BAT = 'bat'
    FLASHLIGHT = 'flashlight'
    EMPTY_FLASHLIGHT = 'empty_flashlight'
    RADIO = 'radio'

    @property
    def value(self) -> ItemCode:
        return super().value

AnyItemCode : TypeAlias = ItemCode|ItemCodes


class ItemInfo(TypedDict):
    name : str
    description : str
    stackable : bool
    short_description : str

#Inventory slots in the inventory
class BaseInventorySlotData(TypedDict):
    code : ItemCode
    stackable : bool

class SingletonSlotData(BaseInventorySlotData):
    stackable : Literal[False]
    state : dict[str, AnyJson]

class MultipleSlotData(BaseInventorySlotData):
    stackable : Literal[True]
    amount : int

AnyInvSlotData : TypeAlias = Union[SingletonSlotData, MultipleSlotData]

KeyItemCode : TypeAlias = str

class KeyItemCodes(Enum):
    MANOR_BASEMENT_KEY = 'ManorBasementKey1'
    MANOR_FLOOR1_KEY = 'ManorFloor1Key'

    @property
    def value(self) -> KeyItemCode:
        return super().value

AnyKeyItemCode : TypeAlias = Union[KeyItemCodes, KeyItemCode]

KeyItemNames : dict[KeyItemCode, str] = {
    KeyItemCodes.MANOR_BASEMENT_KEY.value : 'Basement Key',
    KeyItemCodes.MANOR_FLOOR1_KEY.value : 'Floor 1 Key'
}

def clear_console(method : int = 1):
    if method == 1:
        print("\033c", end="")
    elif method == 2:
        print(f"\033[H\033[3J", end="")
    elif method == 3:
        print("\n" * 50)
    else:
        os.system('cls' if os.name == 'nt' else 'clear')

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

class TextFormatTags(Enum):
    NOTHING = 0
    BOLD = 1 #vscode only
    ITALIC = 3
    UNDERLINE = 4
    FLASHING = 5 #not in vscode
    NEGATIVE = 7
    STRIKETRHOUGH = 9
    DOUBLE_UNDERLINE = 21 #not in vscode

class TextColorTags(Enum):
    BLACK = 30
    DARK_RED = 31
    DARK_GREEN = 32
    DARK_YELLOW = 33
    DARK_BLUE = 34
    DARK_MAGENTA = 35
    DARK_CYAN = 36
    DARK_WHITE = 37

    BRIGHT_BLACK = 90 #grey
    BRIGHT_RED = 91
    BRIGHT_GREEN = 92
    BRIGHT_YELLOW = 93
    BRIGHT_BLUE = 94
    BRIGHT_MAGENTA = 95
    BRIGHT_CYAN = 96
    BRIGHT_WHITE = 97

class TextBGColorTags(Enum):
    BLACK = 40
    DARK_RED = 41
    DARK_GREEN = 42
    DARK_YELLOW = 43
    DARK_BLUE = 44
    DARK_MAGENTA = 45
    DARK_CYAN = 46
    DARK_WHITE = 47

    BRIGHT_BLACK = 100 #grey
    BRIGHT_RED = 101
    BRIGHT_GREEN = 102
    BRIGHT_YELLOW = 103
    BRIGHT_BLUE = 104
    BRIGHT_MAGENTA = 105
    BRIGHT_CYAN = 106
    BRIGHT_WHITE = 107

AnyTextTag : TypeAlias = TextFormatTags|TextColorTags|TextBGColorTags

class TextFormatter:
    def __init__(self):
        pass

    def format(self, text : str, *args : AnyTextTag) -> str:
        start_part = ''.join([f"\033[{tag.value}m" for tag in args])
        end_part : str = f"{text}\033[0m"
        return start_part + end_part
        
TF = TextFormatter()

def italic(text : str):
    return TF.format(text, TextFormatTags.ITALIC)


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
    key_items : list[str]

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
    key_item_drop : KeyItemCode

class RoomInfo(OptionalRoomInfo):
    entry_text : str
    options : dict[str, int]|int|str
    type : RoomType|str

class EndingInfo(TypedDict):
    ending_text : str
    ending_name : str
    retryable : bool
    retry_checkpoint : str

ITEM_DATA : dict[ItemCode, ItemInfo] = {
    ItemCodes.BAT.value : {'name' : 'Wooden Bat', 'description' : 'A wooden bat', 'stackable' : False, 'short_description' : 'A wooden bat'},
    ItemCodes.FLASHLIGHT.value : {'name' : 'Flashlight', 'description' : 'A flaslight', 'stackable' : False, 'short_description' : 'A flaslight'},
    ItemCodes.RADIO.value : {'name' : 'Radio', 'description' : 'A radio', 'stackable' : False, 'short_description' : 'A radio'},
    
    ItemCodes.EMPTY_FLASHLIGHT.value : {'name' : 'Empty Flashlight', 'description' : 'A flashlight with no batteries', 
                                        'stackable' : False, 'short_description' : 'A flashlight with no batteries'}
}


class Game:
    def __init__(self):
        self.global_state : dict[str, AnyJson] = {'Cash' : 0}
        self.inventory : list[AnyInvSlotData] = []
        self.has_visited : dict[int, int] = defaultdict(lambda : 0)
        self.room_state : dict[int, dict] = {}
        self.perma_state : dict[str, AnyJson] = {}
        self.checkpoints : dict[str, GameState] = {}
        self.room_number : int = 0
        self.temp_data : dict[str, AnyJson] = {}
        self.key_items : list[str] = []

    def reset(self):
        self.global_state = {'Cash' : 0}
        self.inventory = []
        self.has_visited = defaultdict(lambda : 0)
        self.room_state = {}
        self.perma_state = {}
        self.checkpoints = {}
        self.room_number = 0
        self.temp_data = {}
        self.key_items = []

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
        except json.JSONDecodeError:
            print('File is empty/is corrupted/is not a json file!')
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
        elif is_filled < SAVE_VERSION:
            print("Save is outdated and data cannot be recovered - Wiping data!")
            return True


        return self._load_data(data)

    def _get_data(self) -> SaveFile:
        current_state = self._get_game_state()
        data : SaveFile = {
            'current_state' : current_state,
            'is_filled' : SAVE_VERSION,
            'perma_state' : self.perma_state,
            'checkpoints' : self.checkpoints
        }
        return data

    def _get_game_state(self) -> GameState:
        has_visited = {str(key) : self.has_visited[key] for key in self.has_visited}
        current_state : GameState = {
            'global_state' : self.global_state,
            'key_items' : self.key_items,
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
        self.key_items = state['key_items']

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
        for item_slot in self.inventory:
            item_count = item_slot.get('amount', 1)
            if item_count <= 0: continue
            print(self.format_inventory_slot(item_slot))
    
    def format_inventory_slot(self, slot : AnyInvSlotData) -> str|None:
        item_count = slot.get('amount', 1)
        if item_count <= 0: return None
        item_code : ItemCode = slot['code']
        item_name : str = ITEM_DATA[item_code]['name']
        item_desc : str = ITEM_DATA[item_code]['description']
        if slot['stackable']:
            return f'{item_name} ({item_count}) - {item_desc}'
        return f'{item_name} - {item_desc}'

    def find_inventory_item(self, item_code : AnyItemCode) -> AnyInvSlotData|None:
        if isinstance(item_code, ItemCodes): item_code = item_code.value
        for item_slot in self.inventory:
            if item_slot['code'] == item_code: return item_slot
        return None

    def find_all_inventory_items(self, item_code : AnyItemCode) -> list[AnyInvSlotData]:
        if isinstance(item_code, ItemCodes): item_code = item_code.value
        return_value : list[AnyInvSlotData] = []
        for item_slot in self.inventory:
            if item_slot['code'] == item_code: return_value.append(item_slot)
        return return_value

    def item_in_inventory(self, item_code : AnyItemCode) -> bool:
        if isinstance(item_code, ItemCodes): item_code = item_code.value
        return True if self.find_inventory_item(item_code) else False

    def add_item_to_inventory(self, item_code : AnyItemCode, amount : int = 1):
        if isinstance(item_code, ItemCodes): item_code = item_code.value
        if not ITEM_DATA[item_code]['stackable']:
            return self._add_unstackable_item(item_code, amount)
        current_slot : MultipleSlotData|None = self.find_inventory_item(item_code)
        if current_slot is None:
            new_slot : MultipleSlotData = {'code' : item_code, 'stackable' : True, amount : amount}
            self.inventory.append(new_slot)
            return
        else:
            current_slot['amount'] += amount

    def _add_unstackable_item(self, item_code : AnyItemCode, amount : int = 1):
        if isinstance(item_code, ItemCodes): item_code = item_code.value
        for _ in range(amount):
            new_slot : SingletonSlotData = {'code' : item_code, 'stackable' : False, 'state' : {}}
            self.inventory.append(new_slot)

    def add_modified_item_to_inventory(self, item_code : AnyItemCode, state : dict[str, AnyJson], amount : int = 1):
        if isinstance(item_code, ItemCodes): item_code = item_code.value
        for _ in range(amount):
            new_slot : SingletonSlotData = {'code' : item_code, 'stackable' : False, 'state' : state}
            self.inventory.append(new_slot)

ManagmentFunction : TypeAlias = Callable[[], str|int]
EntryFunction : TypeAlias = Callable[[], None]

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
        if self.data.get('key_item_drop', None):
            drop : KeyItemCode|KeyItemCodes = self.data['key_item_drop']
            if isinstance(drop, KeyItemCodes): drop = drop.value
            if drop not in game.key_items: game.key_items.append(drop)
        options = self.data['options']
        if type(options) == str:
            if options == 'END': stall()
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
            txt_to_display : list[str]
            for part in txt_to_display:
                if part == txt_to_display[-1]:
                    print(part, end = '\n')
                    if not isinstance(self.data['options'], int): 
                        stall()
                        print('')
                    break
                else:
                    stall(part)

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

    def manage_room_2(self):
        item_codes = [ItemCodes.BAT, ItemCodes.FLASHLIGHT]
        item_description_dict = {code : ITEM_DATA[code.value]['short_description'] for code in item_codes}
        option_dict : dict[int, ItemCode] = {}
        print('')
        for i, item_code in enumerate(item_codes):
            print(f'{i + 1}-{item_description_dict[item_code]}')
            option_dict[i + 1] = item_code
        option_dict[3] = 'Nothing'
        option_dict[4] = 'All of them'
        print('3-Nothing\n4-Both of them')

        choice = get_int_choice(4)
        if choice == 3:
            print('You decided not to get anything.')
        elif choice == 4:
            print('You picked up the bat and the flashlight.')
            game.add_item_to_inventory(ItemCodes.BAT)
            game.add_item_to_inventory(ItemCodes.FLASHLIGHT)
        else:
            item_to_get = option_dict[choice]
            game.add_item_to_inventory(item_to_get)
            insertion_name = {ItemCodes.BAT : 'bat', ItemCodes.FLASHLIGHT : 'flashlight'}[item_to_get]
            print(f"You decided to pick the {insertion_name}. You hope that it's going to be useful.")
    
        stall()
        return self.data['options']

    def manage_room_12(self):
        options = self.data['options']
        option_dict : dict[int, str] = {}
        for i, option in enumerate(options):
            print(f'{i+1}-{option}')
            option_dict[i + 1] = option
        choice = get_int_choice(len(options))
        print('')
        result = options[option_dict[choice]]
        if result == 20:
            result = 20_001 if KeyItemCodes.MANOR_FLOOR1_KEY.value in game.key_items else 20
        elif result == 29:
            result = 29_001 if KeyItemCodes.MANOR_BASEMENT_KEY.value in game.key_items else 29
        return result
    
    def enter_room_20001(self):
        if game.has_visited[20] >= 1 or game.has_visited[20_001] >= 1:
            self.enter_default()
            return
        print('''You decide to go up the stairs.''', end='')
        stall('')
        print('At the top, you notice that the door to the second floor is locked.', end='')
        stall('')
        print('Thankfully, you already have the key to unlock the door and you open it.')

    def manage_room_20001(self):
        if KeyItemCodes.MANOR_BASEMENT_KEY.value in game.key_items:
            room_to_return = 21_002
        else:
            room_to_return = 21_001
        stall()
        print('')
        return room_to_return

    def enter_room_32(self):
        if game.has_visited[32] > 1:
            print(self.data['second_arrival_text'])
            return

        if game.find_inventory_item(ItemCodes.RADIO):
            print('''You tried using the radio you got earlier to get help.\nNo one picked up...''')
        else:
            print(self.data['entry_text'])

    def enter_room_33(self):
        if game.has_visited[33] > 1:
            print(self.data['second_arrival_text'])
            return

        did_fight_door = False
        if game.find_inventory_item(ItemCodes.BAT):
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

room_data : dict[int, RoomInfo] = {
    0 : {
'type' : RoomType.STANDARD,
'entry_text' : '''---------CHAPTER 0 - Prologue---------''',
'options' : 1,
},

    1 : {
'type' : RoomType.STANDARD,
'entry_text' : [
'''It's a nice summer day.''',
'''The sky is a clear blue, and the temperature is just perfect...''',
'''It's the kind of weather that makes you feel like nothing could go wrong.''',
'''That's why you decided to go on a walk around the block.''',
'''While you're walking, something catches your attention.''',
'''You see a decrepit house near you.''',
'''While you've never exactly been an explorer, it manages to spike your interest.''',
'''Although it's a bit creepy, you can't help but wonder what's in there.''',
'''It's not like anyone lives there anymore...'''
],
'options' : {'Continue your walk' : 4, 'Investigate the mansion' : 3},
},

    2 : {
'type' : RoomType.STANDARD,
'entry_text' : '''Right before arriving at the mansion, you encountered a mysterious stand. 
They have a few items on display, and a sign that reads: "Take one item!"
What do you take?''',
'options' : 8,
},

    3 : {
'type' : RoomType.STANDARD,
'entry_text' : '''You decided to investigate the mansion. Will you regret this choice? Only time will tell...''',
'options' : 2,
},

    4 : {
'type' : RoomType.STANDARD,
'entry_text' : [
'''You decided walk past it.''',
'''There's no way you were going to ruin your day by going to that creepy house...''',
'''...''',
'''You feel like you just forgot something important.'''
],
'options' : 'ENDING AVOID_DANGER'
},

    5 : {
'type' : RoomType.STANDARD,
'entry_text' : 'You think about another way to get into the mansion.',
'options' : {'Force the door open' : 9, 'Try to find a way around' : 11},
},

    6 : {
'type' : RoomType.STANDARD,
'entry_text' : [
f'''You decided that {italic('maybe')} breaking into an unhabited house isn't a very good use of your time.''',
'''You turn around and decide to go on with your day.''',
'''...''',
f'''You feel like you just forgot something important.'''
],
'options' : 'ENDING AVOID_DANGER'
},

    7 : {
'type' : RoomType.STANDARD,
'entry_text' : '''You decided to investigate. Will you regret this choice? Only time will tell...''',
'options' : 8
},

    8 : {
'type' : RoomType.STANDARD,
'entry_text' : [
'''You arrived at the mansion.''',
'''It looks extremely worn down.''',
'''For some reason, it dosen't seem to have any windows.''',
'''You slowly walk up to the front door and look at it.''',
'''It's in surprisingly good condition, considering what the rest of the house looks like.''',
'''You try to open it.''',
'''*click*''',
'''*click* *click*''',
'''It's locked. What do you do?''',
],
'second_arrival_text' : 'You think about another way to get into the mansion.',
'options' : {'Force the door open' : 9, 'Try to find a way around' : 11, 'Stop trying to break in' : 6},
},

    9 : {
'type' : RoomType.STANDARD,
'entry_text' : '''You tried to force the door open. Unfortunately, for you, the door won't budge.
Not one to give up so quickly, you start fighting with the door.
...
The door won.''',
'second_arrival_text' : '''You have a feeling this won't be very productive.''',
'options' : 5
},

    10 : {
'type' : RoomType.STANDARD,
'entry_text' : [
'''You look around for a window to break and find one.''',
f'''For some reason, the mansion dosen't have {italic('any')} windows.''',
],
'second_arrival_text' : '''Cant break a window if there's no window...''',
'options' : 5
},

    11 : {
'type' : RoomType.STANDARD,
'entry_text' : [
'''You looked around the house for a way in.''',
'''Despite the front door being completely fine, the backdoor is on the verge of falling apart.''',
'''You make your way into the house.''',
],
'options' : 11_001
},

11_001 : {
'type' : RoomType.STANDARD,
'entry_text' : '''---------CHAPTER 1 - The Manor---------''',
'options' : 11_002
},

11_002 : {
'type' : RoomType.CHECKPOINT,
'entry_text' : 'New checkpoint!',
'options' : 12,
'extra_info' : {'checkpoint_name' : 'Chapter1Start'}
},

    12 : {
'type' : RoomType.STANDARD,
'entry_text' : [
'''The house is odd.''',
'''For some reason, it feels like some things are just... out of place.''',
'''You decide to take a look at...''',
],
'second_arrival_text' : '''What now?''',
'options' : {'The living room' : 13, 'The kitchen' : 14, 'The bathroom' : 15, 'The washing room' : 16, #cut the washing room?
             'The entry' : 17, 'The front door' : 18, 'Upstairs' : 20, 'The basement door' : 29},
},

13 : {
'type' : RoomType.STANDARD, #might be a bit silly to latch on to this detail
'entry_text' : [
'''You take a look at the room.''',
'''There isn't anything that catches your attention.''',
'''That is, until you notice a book.''',
'''There's nothing special about this book, except for the fact that it released last week.''',
'''...'''
'''You decide to not think about the implications.'''
],
'second_arrival_text' : '''You remember the book you noticed earlier. What could it possibly mean?''',
'options' : 12,
},

14 : {
'type' : RoomType.STANDARD,
'entry_text' : '''Nothing here.''',
'second_arrival_text' : '''Nothing here.''',
'options' : 12,
},

15 : {
'type' : RoomType.STANDARD,
'entry_text' : '''Nothing here.''',
'second_arrival_text' : '''Nothing here.''',
'options' : 12,
},

16 : {
'type' : RoomType.STANDARD,
'entry_text' : '''Nothing here.''',
'second_arrival_text' : '''Nothing here.''',
'options' : 12,
},

17 : {
'type' : RoomType.STANDARD,
'entry_text' : f'''{TF.format('Floor 1 key obtained!', TextColorTags.BRIGHT_YELLOW)}''',
'second_arrival_text' : '''Nothing here.''',
'options' : 12,
'key_item_drop' : KeyItemCodes.MANOR_FLOOR1_KEY.value
},

18 : {
'type' : RoomType.STANDARD,
'entry_text' : '''Nothing here.''',
'second_arrival_text' : '''Nothing here.''',
'options' : 12,
},

    20 : {
'type' : RoomType.STANDARD,
'entry_text' : [
'''You decide to go up the stairs.''',
'''At the top, you notice that the door to the second floor is locked.'''
],
'second_arrival_text' : '''You try to go upstairs, but it's locked.''',
'options' : 21_001,
},

    20_001 : {
'type' : RoomType.STANDARD,
'entry_text' : 'You go up the stairs and unlock the door.',
'second_arrival_text' : '''You make your way upstairs.''',
'options' : 21_001,
},

20_002 : {
'type' : RoomType.STANDARD,
'entry_text' : 'You go back downstairs.',
'options' : 12
},

21_001 : {
'type' : RoomType.STANDARD,
'entry_text' : [
'''You take a look at the second floor.''',
'''... It's completely empty.''',
'''No rooms, no walls, no furniture...''',
'''Nothing apart from a single window.''',
'''But you don't remember seeing any windows on the exterior of the house...''',
'''You take a look at the floor.''',
'''Despite the house's apparent age, the floor is completely clean, as if someone passed by here to clean.''',
'''On the ground, there's a key in the middle of the room.''',
'''You feel like it could be useful, but something tells you you should leave it there.''',
'''This place is really starting to unsettle you.''',
'''You decide to...'''
],
'second_arrival_text' : '''You ponder about taking the key you left on the floor.\nYou decide to...''',
'options' : {'Take the key' : 21_003, 'Leave the key' : 21_004},
},

21_002 : {
'type' : RoomType.STANDARD,
'entry_text' : [
'''You think about the window and the key and start wondering\nif you've made a mistake by coming to this place.''',
'''You hope that the awnser is no but, at this point, you really can't be sure.'''
],
'options' : 20_002,
},

21_003 : {
'type' : RoomType.STANDARD,
'entry_text' : [
'''You decide to take the key.''',
f'''{TF.format('Basement key obtained!', TextColorTags.BRIGHT_YELLOW)}''',
'''Hopefully, this won't backfire...'''
],
'options' : 20_002,
'key_item_drop' : KeyItemCodes.MANOR_BASEMENT_KEY.value
},

21_004 : {
'type' : RoomType.STANDARD,
'entry_text' : 'You decided to leave the key on the ground. Something about it just creeps you out.',
'options' : 20_002
},


    21 : {
'type' : RoomType.STANDARD,
'entry_text' : 'You arrive at the second floor. Where do you go?',
'second_arrival_text' : '''What now?''',
'options' : {'The first bedroom' : 22, 'The second bedroom' : 23, 'The storage room' : 25, #bedroom 3 = 24
             'A closet' : 27, 'The hallway' : 28, 'Downstairs' : 20_002}, #bathroom 2 = 26
},



22 : {
'type' : RoomType.STANDARD,
'entry_text' : '''Nothing in the first bedroom.''',
'second_arrival_text' : '''Nothing here.''',
'options' : 21,
},

23 : {
'type' : RoomType.STANDARD,
'entry_text' : '''Nothing in the second bedroom.''',
'second_arrival_text' : '''Nothing here.''',
'options' : 21,
},

24 : {
'type' : RoomType.STANDARD,
'entry_text' : '''Nothing in the third bedroom.''',
'second_arrival_text' : '''Nothing here.''',
'options' : 21,
},

25 : {
'type' : RoomType.STANDARD,
'entry_text' : '''Nothing here.''',
'second_arrival_text' : '''Nothing here.''',
'options' : 21,
},

26 : {
'type' : RoomType.STANDARD,
'entry_text' : '''Nothing in the second bathroom.''',
'second_arrival_text' : '''Nothing here.''',
'options' : 21,
},

27 : {
'type' : RoomType.STANDARD,
'entry_text' : f'''{TF.format('Basement key obtained!', TextColorTags.BRIGHT_YELLOW)}''',
'second_arrival_text' : '''Nothing here.''',
'options' : 21,
'key_item_drop' : KeyItemCodes.MANOR_BASEMENT_KEY.value
},

28 : {
'type' : RoomType.STANDARD,
'entry_text' : '''Nothing here.''',
'second_arrival_text' : '''Nothing here.''',
'options' : 21,
},

    29 : {
'type' : RoomType.STANDARD,
'entry_text' : '''It's locked.''',
'second_arrival_text' : '''It's still locked.''',
'options' : 12,
},

    29_001 : {
'type' : RoomType.STANDARD,
'entry_text' : '''You think about using the key. You hesitate.''',
'second_arrival_text' : '''You think about using the key.''',
'options' : 30,
},

30 : {
'type' : RoomType.STANDARD,
'entry_text' : '''You actually open the door.''',
'options' : 31,
},


    31 : {
'type' : RoomType.STANDARD,
'entry_text' :  [
'''As you take your first steps into the basement, you already start regretting your decision.
But before you can even consider getting out...''',
'''*BLAM!*''',
'''The door closes in on you. Even worse, it's also locked on the inside...''',
'''...''',
'''Looks like you only have one way forwards. Unless...'''
],
'second_arrival_text' : '''What now?''',
'options' : {'Call for help' : 32, 'Investigate the basement' : 34, 'Break the door open' : 33},
},

    32 : {
'type' : RoomType.STANDARD,
'entry_text' :'''You try to call for help with yout voice. Unfortunately, no one is around to hear you.
Looks like you are on your own...''',
'second_arrival_text' : '''This isn't going to work...''',
'options' : 31
},

    33 : {
'type' : RoomType.STANDARD,
'entry_text' : [
'''You try to force the door open.''',
'''...''',
'''It dosent even budge...''',
],
'second_arrival_text' : '''That's not going to work.''',
'options' : 31
},

    34 : {
'type' : RoomType.STANDARD,
'entry_text' : '''After a moment of thought, you come to the conclusion that the only way you can hope to get out is by going further in.
While this seems like a very bad idea... It looks like the only way out.''',
'options' : 'END'
},

    35 : {
'type' : RoomType.STANDARD,
'entry_text' :  '''---------CHAPTER 2 - Into the dark---------''',
'options' : 'END'
},

    36 : {
'type' : RoomType.CHECKPOINT,
'entry_text' : 'New checkpoint!',
'options' : 'END',
'extra_info' : {'checkpoint_name' : 'Chapter2Start'}
},

}
def show_map(map : str, marker_dict : dict[str|int, str]|None = None):
    if marker_dict is None: marker_dict = {}
    for marker in marker_dict:
        if isinstance(marker, str): marker = MAP_MARKER_DATA[map][marker]
    start_index : int = 0
    while True:
        index = map.find('`', start_index)
        if index == -1: break
        num_slice = map[index + 1 : index + 3]
        map.replace(num_slice, ' ' * len(num_slice))
        marker_value = int(num_slice)
        if marker_value in marker_dict:
            map[index : index+6] = marker_dict[marker_value]
        start_index = index + 2
        
MAP_MANOR_GROUND : str = \
'''
__________________________________
| kitchen |
| `1      |                                       
|_________|
|
|
|
|
|
|
|_______________________
'''.removeprefix('\n')

MAP_MARKER_DATA : dict[str, dict[str, int]] = {
    MAP_MANOR_GROUND : {'kitchen' : 1}
}


ending_data : dict[str, EndingInfo] = {
'Tumble' : {
'ending_name' : 'Bad Ending: Tumble',
'ending_text' : '''That wasn't very bright...''',
'retryable' : True,
'retry_checkpoint' : 'Chapter2Start'
},
'AVOID_DANGER' : {
'ending_name' : 'Good Ending: Smart decisions',
'ending_text' : 'You managed to stay out of trouble.',
'retryable' : False,
'retry_checkpoint' : None
}
}

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
            print(ending_name)
            print(ending_text)
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