from time import sleep
from sys import exit as close_everything
from collections import defaultdict
import json
import os
from typing import Callable, Any, TypedDict, Union, TypeAlias, Literal
from enum import Enum

SAVE_VERSION = 5
IS_VSCODE : bool
saves : list[str] = []
for _, _, files in os.walk('saves'):
    saves = files
    break
IS_VSCODE = any('gitkeep' in save for save in saves)

def crossplatform_input(prompt : object = "") -> str:
    return_value = input(prompt)
    #if not IS_VSCODE: print('')
    return return_value

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
    MANOR_BASEMENT_KEY = 'Ch1ManorBasementKey'
    MANOR_FLOOR1_KEY = 'Ch1ManorFloor1Key'

    @property
    def value(self) -> KeyItemCode:
        return super().value

AnyKeyItemCode : TypeAlias = Union[KeyItemCodes, KeyItemCode]

KeyItemNames : dict[KeyItemCode, str] = {
    KeyItemCodes.MANOR_BASEMENT_KEY.value : 'Basement Key',
    KeyItemCodes.MANOR_FLOOR1_KEY.value : 'Floor 1 Key'
}

def log(text : str):
    if not game.logs: game.logs.append(text); return
    if len(game.logs) >= 200: game.logs.pop(0)
    if game.logs[-1].endswith('\n'):
        game.logs.append(text)
    else:
        game.logs[-1] += text 

def printlog(text, end = '\n', do_log = True):
    print(text, end=end)
    if do_log : log(text + end)

def clear_console(method : int = 1):
    if method == 1:
        print("\033c", end="")
    elif method == 2:
        print(f"\033[H\033[3J", end="")
    elif method == 3:
        print("\n" * 50)
    else:
        os.system('cls' if os.name == 'nt' else 'clear')

def get_int_choice(option_count : int, allow_command : bool = True, do_log : bool = True) -> int:
    valid = [str(i + 1) for i in range(option_count)]
    while True:
        result = crossplatform_input('Selection : ')
        if result in valid:
            if do_log: log(f'Selection : {int(result)}\n')
            return int(result)
        elif result == "cmd" and allow_command:
            enter_command()

        elif len(result) == 0:
            print(f'Invalid. Number must range from 1 to {option_count}. To see run a command, type "cmd" or prefix it with "/".')
        elif result[0] == '/' and allow_command:
            parse_command(result)
        else:
            print(f'Invalid. Number must range from 1 to {option_count}. To see run a command, type "cmd" or prefix it with "/".')

def enter_command():
    parse_command(crossplatform_input("Command : "))

def parse_command(message : str):
    if message[0] == '/':
        message = message[1:]
    command = message
    if not any(command.startswith(cmd_name) for cmd_name in ['stop', 'exit', 'quit']): log(f'Attempted to use command "{command}"\n')
    result = is_valid_command(command)
    if result == False:
        printlog(f'"{command}" is not a recognized command. To see a list of all commands, use help.')
        return False
    elif result == True:
        process_command(command)
        return True
    elif type(result) == str:
        printlog(result)
        return False
    else:
        printlog('Something went wrong. Please try again.')

command_list = ['stop', 'exit', 'quit', 'exit', 'help', 'check', 'save', 'reminder', 'remind', 'logs']

def is_valid_command(message : str):
    message = message.lower()
    words = message.split()
    command = words[0]
    args = words[1:]
    arg_count = len(args)
    default_error = f'Command was formatted incorrectly. To see how to format the command, use "help {command}"'
    match command:
        case 'stop'|'quit'|'exit':
            return True
        case 'save':
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
        case 'remind'|'reminder'|'logs':
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
        case 'stop'|'quit'|'exit':
            print('Are you sure you want to quit? Type "Y" or "yes" if you want to quit.')
            result = crossplatform_input().lower()
            if result == 'y' or result == 'yes':
                sucsess = game.save(f'saves/{current_save_file}.json')
                if sucsess:
                    print('Data saved sucessfully!')
                else:
                    print('Data failed to save...')
                game.quit()
        case 'save':
            sucsess = game.save(f'saves/{current_save_file}.json')
            if sucsess:
                printlog('Data saved sucessfully!')
            else:
                printlog('Data failed to save...')
        case 'check':
            thing_to_check = args[0]
            match thing_to_check:
                case 'inventory':
                    game.print_inventory()
                    log('Inventory was checked sucessfully.\n')
                case _:
                    printlog(default_error)
        case 'help':
            if arg_count == 0:
                print('quit, stop, exit - Close the game')
                print('check - Check something')
                print('save - Save the game in the current save file.')
                print('For more detailed help about a command, use "help <command>"')
                log('Received a summary of all available commands in the game.\n')
                return
            command_to_help = args[0]
            match command_to_help:
                case 'help':
                    printlog('For more detailed help about a command, use "help <command>"')
                case 'stop'|'quit'|'exit':
                    printlog('Use to quit the game.')
                case 'save':
                    printlog('Use to save the game in the current save file.')
                case 'check':
                    printlog('Use check <something> to check something. You can try to check your inventory.')
                case 'remind'|'reminder'|'logs':
                    printlog('Use to check past events.')
        
        case 'remind'|'reminder'|'logs':
            log_viewer()
            log('Viewed logs.\n')
            return

        case _:
            printlog(default_error)

def log_viewer(window : int = 18, scroll : int = 4):
    log_lentgh : int = len(game.logs)
    if log_lentgh == 0:
        print('There are no logs to view!')
        return
    clear_console()
    if log_lentgh <= window:
        print(''.join(game.logs))
        print(TF.format('1-Up', TextColorTags.BRIGHT_BLACK))
        print(TF.format('2-Down', TextColorTags.BRIGHT_BLACK))
        print('3-Back')
        while True:
            choice : int = get_int_choice(3, allow_command=False, do_log=False)
            if choice in {1,2}: print('You cannot scroll that way!'); continue
            if choice == 3: 
                clear_console()
                print(''.join(game.logs)) 
                return
    slice_top : int
    slice_bottom : int = 1
    max_bottom : int = log_lentgh - window + 1
    while True:
        slice_top = slice_bottom + window
        section : list[str]
        if slice_bottom <= 1:
            section = game.logs[-slice_top:]
        else:
            section = game.logs[-slice_top:-(slice_bottom-1)]
        can_scroll_up : bool = True if slice_bottom <= max_bottom else False
        can_scroll_down : bool = True if slice_bottom > 1 else False
        print('---')
        print(''.join(section), end='' if section[-1].endswith('\n') else '\n')
        print('---')
        print(TF.format('1-Up', TextColorTags.BRIGHT_BLACK if not can_scroll_up else TextFormatTags.NOTHING))
        print(TF.format('2-Down', TextColorTags.BRIGHT_BLACK if not can_scroll_down else TextFormatTags.NOTHING))
        print('3-Back')
        while True:
            choice : int = get_int_choice(3, allow_command=False, do_log=False)
            if choice == 1:
                if can_scroll_up:
                    slice_bottom = min(slice_bottom + scroll, max_bottom)
                    clear_console()
                    break
                else:
                    print('You cannot scroll that way!')
                    continue
            if choice == 2:
                if can_scroll_down:
                    slice_bottom = max(slice_bottom - scroll, 1)
                    clear_console()
                    break
                else:
                    print('You cannot scroll that way!')
                    continue
            if choice == 3: 
                clear_console()
                slice_top = min(window + 1, log_lentgh)
                print(''.join(game.logs[-(window + 1):]))
                return

def stall(stall_text = '(Enter to continue.) -->', do_log = False):
    crossplatform_input(stall_text)
    if do_log: log(stall_text + '\n')


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

ConvertedToInteger : TypeAlias = int

class GameState(TypedDict):
    global_state : dict[str, AnyJson]
    room_state : dict[ConvertedToInteger, dict[str, AnyJson]]
    game_inventory : dict[str, int]
    visited_rooms : dict[ConvertedToInteger, int]
    current_room : int
    temp_data : dict[str, AnyJson]
    key_items : list[str]
    logs : list[str]

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
    second_arrival_text : str|list[str]
    extra_info : dict[str, Any]
    key_item_drop : KeyItemCode
    alternate_text : list[str|list[str]]

class RoomInfo(OptionalRoomInfo):
    entry_text : str|list[str]
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
        self.global_state : dict[str, AnyJson] = {}
        self.inventory : list[AnyInvSlotData] = []
        self.has_visited : dict[int, int] = defaultdict(lambda : 0)
        self.room_state : dict[int, dict[str, AnyJson]] = {}
        self.perma_state : dict[str, AnyJson] = {}
        self.checkpoints : dict[str, GameState] = {}
        self.room_number : int = 0
        self.temp_data : dict[str, AnyJson] = {}
        self.key_items : list[str] = []
        self.logs : list[str] = []

    def reset(self):
        self.global_state = {}
        self.inventory = []
        self.has_visited = defaultdict(lambda : 0)
        self.room_state = {}
        self.perma_state = {}
        self.checkpoints = {}
        self.room_number = 0
        self.temp_data = {}
        self.key_items = []
        self.logs = []

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
            'temp_data' : self.temp_data,
            'logs' : self.logs
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
        self.logs = state['logs']

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
            stall(do_log=(not first_room))
            printlog('', do_log=(not first_room))
            return options
        option_dict : dict[int, str] = {}
        for i, option in enumerate(options):
            printlog(f'{i+1}-{option}', do_log=(not first_room))
            option_dict[i + 1] = option
        choice = get_int_choice(len(options))
        printlog('', do_log=(not first_room))
        result = options[option_dict[choice]]
        return result

    def enter_default(self):
        if self.data['type'] == RoomType.CHECKPOINT:
            return self._enter_checkpoint()
        if game.has_visited[self.room_number] <= 1:
            txt_to_display = self.data['entry_text']
        else:
            second_arrival_text = self.data.get('second_arrival_text', None)
            txt_to_display = second_arrival_text if second_arrival_text else self.data['entry_text']

        if type(txt_to_display) == str:
            printlog(txt_to_display, do_log=(not first_room))
        else:
            txt_to_display : list[str]
            for part in txt_to_display:
                if part == txt_to_display[-1]:
                    printlog(part, end = '\n', do_log=(not first_room))
                    if not isinstance(self.data['options'], int): 
                        stall(do_log=(not first_room))
                        printlog('', do_log=(not first_room))
                    break
                else:
                    stall(part, do_log=(not first_room))

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
        print('', do_log=(not first_room))
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
    
    def enter_room_12(self):
        if 12 not in game.room_state: game.room_state[12] = {}
        if 'Alert' not in game.room_state[12]: game.room_state[12]['Alert'] = 0
        if 'TimesAlerted' not in game.room_state[12]: game.room_state[12]['TimesAlerted'] = 0
        high_alert : bool = game.room_state[12]['Alert'] >= 6

        if high_alert and not game.temp_data.get('did_alert', False):
            game.room_state[12]['TimesAlerted'] += 1
            game.temp_data['did_alert'] = True

        if game.has_visited[self.room_number] <= 1:
            txt_to_display = self.data['entry_text']
        elif game.room_state[12]['TimesAlerted'] <= 0 or not high_alert:
            txt_to_display = self.data['second_arrival_text']
        elif game.room_state[12]['TimesAlerted'] == 1:
            txt_to_display = [
            '''...'''
            '''This place is really getting under your skin...''',
            '''You start considering leaving.'''
            ]
        else:
            txt_to_display = 'What now? Maybe leaving is a good idea...'
        
        if type(txt_to_display) == str:
            printlog(txt_to_display, do_log=(not first_room))
        else:
            txt_to_display : list[str]
            for part in txt_to_display:
                if part == txt_to_display[-1]:
                    printlog(part, end = '\n', do_log=(not first_room))
                    if not isinstance(self.data['options'], int): 
                        stall(do_log=(not first_room))
                        printlog('', do_log=(not first_room))
                    break
                else:
                    stall(part, do_log=(not first_room))

    def manage_room_12(self):
        room_12_state = game.room_state[12]
        high_alert : bool = room_12_state['Alert'] >= 6
        options = self.data['options']
        option_dict : dict[int, str] = {}
        for i, option in enumerate(options):
            printlog(f'{i+1}-{option}', do_log=(not first_room))
            option_dict[i + 1] = option
        if high_alert:
            printlog(f'{i+2}-Leave', do_log=(not first_room))
            option_dict[i+2] = 'Leave'
        choice = get_int_choice(len(options) + 1 if high_alert else len(options))
        str_result = option_dict[choice]
        result = options[str_result] if str_result != 'Leave' else 12_001
        printlog('', do_log=(not first_room))
        if result == 20:
            result = 20_001 if KeyItemCodes.MANOR_FLOOR1_KEY.value in game.key_items else 20
        elif result == 29:
            if game.has_visited[30_002] >= 1:
                result = 30_002 if high_alert else 30_005
            elif KeyItemCodes.MANOR_BASEMENT_KEY.value not in game.key_items:
                result = 29
            elif high_alert:
                result = 29_002
            else:
                result = 29_001
        elif result == 18:
            result = 18_001 if high_alert else 18
        return result
    
    def enter_room_13(self):
        self.enter_default()
        if game.has_visited[13] <= 1 and not game.temp_data.get('did_alert', False):
            game.room_state[12]['Alert'] += 1
            game.temp_data['did_alert'] = True
    
    def enter_room_14(self):
        high_alert : bool = game.room_state[12]['Alert'] >= 6
        if game.has_visited[14] <= 1:
            txt_to_display = self.data['entry_text'] if not high_alert else self.data['alternate_text'][0]
        else: 
            txt_to_display = self.data['second_arrival_text'] if not high_alert else self.data['alternate_text'][1]
        if type(txt_to_display) == str:
            printlog(txt_to_display, do_log=(not first_room))
        else:
            txt_to_display : list[str]
            for part in txt_to_display:
                if part == txt_to_display[-1]:
                    printlog(part, end = '\n', do_log=(not first_room))
                    if not isinstance(self.data['options'], int): 
                        stall(do_log=(not first_room))
                        printlog('', do_log=(not first_room))
                    break
                else:
                    stall(part, do_log=(not first_room))

        if game.has_visited[14] <= 1 and not game.temp_data.get('did_alert', False):
            game.room_state[12]['Alert'] += 1
            game.temp_data['did_alert'] = True
    
    def enter_room_18(self): #low alert
        self.enter_default()
        if game.has_visited[18_001] <= 0: game.has_visited[18_001] = 1
    
    def enter_room_18_001(self): #high alert
        self.enter_default()
        if game.has_visited[18] <= 0: game.has_visited[18] = 1
    
    def manage_room_18_001(self):
        stall()
        print('')
        return 12 if game.has_visited[19_001] >= 1 else 18_002 #can only go outside (room 19_001) once
    
    def enter_room_19003(self):
        self.enter_default()
        if game.has_visited[19003] <= 1 and not game.temp_data.get('did_unalert', False):
            game.room_state[12]['Alert'] = 1
            game.temp_data['did_unalert'] = True
    
    def enter_room_20001(self):
        if game.has_visited[20] >= 1 or game.has_visited[20_001] >= 1:
            self.enter_default()
            return
        stall('''You decide to go up the stairs.''', do_log=(not first_room))
        stall('At the top, you notice that the door to the second floor is locked.', do_log=(not first_room))
        stall('You try to unlock the door with the key you already have.', do_log=(not first_room))
        stall('*click*', do_log=(not first_room))
        print('It works perfectly.', do_log=(not first_room))

    def manage_room_20001(self):
        if KeyItemCodes.MANOR_BASEMENT_KEY.value in game.key_items:
            room_to_return = 21_002
        else:
            room_to_return = 21_001
        stall(do_log=(not first_room))
        printlog('', do_log=(not first_room))
        return room_to_return
    
    def enter_room_21001(self):
        ROOM_21001_DISAPPEARING_LINE_INDEX : int = 9
        if game.has_visited[self.room_number] <= 1:
            txt_to_display = self.data['entry_text']
        else:
            second_arrival_text = self.data.get('second_arrival_text', None)
            txt_to_display = second_arrival_text if second_arrival_text else self.data['entry_text']

        if type(txt_to_display) == str:
            printlog(txt_to_display, do_log=(not first_room))
        else:
            txt_to_display : list[str]
            for i, part in enumerate(txt_to_display):
                if part == txt_to_display[-1]:
                    printlog(part, end = '\n', do_log=(not first_room))
                    if not isinstance(self.data['options'], int): 
                        stall(do_log=(not first_room))
                        printlog('', do_log=(not first_room))
                    break
                elif i == ROOM_21001_DISAPPEARING_LINE_INDEX:
                    chunks : list[str] = list(italic(c) for c in ["do","n't ","go ","in ","the ","bas","em","ent"," it ","made ","me ","for","get"])
                    i = len(chunks) - 1
                    print(''.join(chunks), end = '\r')
                    sleep(1.6)
                    while i >= 0:
                        print(' ' * 70, end='\r')
                        print(''.join(chunks[:i]), end = '\r')
                        i-=1
                        sleep(0.12)
                else:
                    stall(part, do_log=(not first_room))
        if game.has_visited[21_001] <= 1 and not game.temp_data.get('did_alert', False):
            game.room_state[12]['Alert'] += 3
            game.temp_data['did_alert'] = True
    
    def enter_room_21003(self):
        self.enter_default()
        if game.has_visited[21_003] <= 1 and not game.temp_data.get('did_unalert', False):
            game.room_state[12]['Alert'] -= 0
            game.temp_data['did_unalert'] = True
        
    def enter_room_21004(self):
        self.enter_default()
        if game.has_visited[21_004] <= 1 and not game.temp_data.get('did_alert', False):
            game.room_state[12]['Alert'] += 1
            game.temp_data['did_alert'] = True
    
    def enter_room_29(self):
        high_alert : bool = game.room_state[12]['Alert'] >= 6
        if game.has_visited[29] <= 1:
            txt_to_display = self.data['entry_text'] if not high_alert else self.data['alternate_text'][0]
        else: 
            txt_to_display = self.data['second_arrival_text'] if not high_alert else self.data['alternate_text'][1]
        if type(txt_to_display) == str:
            printlog(txt_to_display, do_log=(not first_room))
        else:
            txt_to_display : list[str]
            for part in txt_to_display:
                if part == txt_to_display[-1]:
                    printlog(part, end = '\n', do_log=(not first_room))
                    if not isinstance(self.data['options'], int): 
                        stall(do_log=(not first_room))
                        printlog('', do_log=(not first_room))
                    break
                else:
                    stall(part, do_log=(not first_room))
    
    def enter_room_29001(self): #low alert
        self.enter_default()
        if game.has_visited[29_002] <= 0: game.has_visited[29_002] = 1
    
    def enter_room_29002(self): #high alert
        self.enter_default()
        if game.has_visited[29_001] <= 0: game.has_visited[29_001] = 1

    def enter_room_32(self):
        if game.has_visited[32] > 1:
            printlog(self.data['second_arrival_text'], do_log=(not first_room))
            return

        if game.find_inventory_item(ItemCodes.RADIO):
            printlog('''You tried using the radio you got earlier to get help.\nNo one picked up...''', do_log=(not first_room))
        else:
            printlog(self.data['entry_text'], do_log=(not first_room))

    def enter_room_33(self):
        if game.has_visited[33] > 1:
            print(self.data['second_arrival_text'])
            return

        did_fight_door = False
        if game.find_inventory_item(ItemCodes.BAT):
            if did_fight_door:
                printlog('''With a bat by your side, you can surely force this door open, right?
...
The score is 2-0 now.''', do_log=(not first_room))
            else:
                printlog('You took a few swings at the door, but your attacks barely left a scratch.', do_log=(not first_room))
        else:
            if did_fight_door:
                printlog('''Your past experiences with doors tells you this isn't going to work.''', do_log=(not first_room))
            else:
                printlog('\n'.join(self.data['entry_text']), do_log=(not first_room))
    
    def enter_room_35(self):
        self.enter_default()
        game.global_state['Ch2Time'] = 60

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

    2 : { #scrapped
'type' : RoomType.STANDARD,
'entry_text' : '''Right before arriving at the mansion, you encountered a mysterious stand. 
They have a few items on display, and a sign that reads: "Take one item!"
What do you take?''',
'options' : 8,
},

    3 : {
'type' : RoomType.STANDARD,
'entry_text' : '''You decided to investigate the mansion. Will you regret this choice? Only time will tell...''',
'options' : 8,
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

    7 : { #unused
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
'entry_text' : '''---------CHAPTER 1 - The Beginning---------''',
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
'''The house is extremely dark.''',
'''The only light source in this place is the backdoor you just opened.''',
'''You walk around the room you are in to try and find a lightswitch.''',
'''You bump into a few objects and eventually find one.''',
'''*click*''',
'''Nothing.''',
'''Either the power is out, or the lights just don't work.''',
'''Either way, you need a solution.''',
'''You pull out your phone.''',
f'''{italic('26% battery remaining')}''',
'''You turn on your phone's flashlight.''',
'''It has much less reach than what you would expect.''',
'''Well, it's not like you have any other options...''',
'''Armed with a source of light, you decide to take a look at...''',
],
'second_arrival_text' : '''What now?''',
'options' : {'The living room' : 13, 'The kitchen' : 14, 'The bathroom' : 15, 'The washing room' : 16, #cut the washing room?
             'The entry' : 17, 'The front door' : 18, 'Upstairs' : 20, 'The basement door' : 29},
},

    12_001 : {
'type' : RoomType.STANDARD,
'entry_text' : [
f'''...''',
f'''This place is creeping you out too much.''',
f'''You have to get out of here...''',
f'''You decide to get out of the house.''',
f'''As you walk outside, the fresh air calms you down.''', #this line feels awkward
f'''You walk away from the house.''',
f'''...''',
f'''You feel like you just forgot something important.''',
f'''No, you {italic('definitively')} forgot something important.'''
],
'options' : 'ENDING AVOID_DANGER_B'
},


    13 : {
'type' : RoomType.STANDARD,
'entry_text' : [
'''The author wrote something he thought was going to be scary, but then he realised it didn't make any sense so it was scrapped.'''
],
'second_arrival_text' : '''What could it have possibly been?''',
'options' : 12,
},

    14 : {
'type' : RoomType.STANDARD,
'entry_text' : [
'''You decide to take a look at the kitchen.''',
'''As soon as you enter it, you hear a loud noise come from the other side of the room.''',
'''*Loud noise*''',
'''You get a bit startled.'''
],
'second_arrival_text' : [
'''Nothing here.'''
],
'alternate_text' : [[
'''*Loud noise*''',
'''Normally, you would be a bit startled.''', #High alert first entry
'''But since you're paranoid now you make a disproportionate reaction.'''
],[
'''[Second arrival text but there's some extra flavor text]''' #High alert second arrival
],
],
'options' : 12,
},

    15 : {
'type' : RoomType.STANDARD,
'entry_text' : [
'''Nothing in the bathroom.'''
],
'second_arrival_text' : '''Nothing here.''',
'options' : 12,
},

    16 : {
'type' : RoomType.STANDARD,
'entry_text' : [
'''Nothing in the washing room.'''
],
'second_arrival_text' : '''Nothing here.''',
'options' : 12,
},

    17 : {
'type' : RoomType.STANDARD,
'entry_text' : [
f'''{TF.format('Floor 1 key obtained!', TextColorTags.BRIGHT_YELLOW)}'''
],
'second_arrival_text' : '''Nothing in the entry.''',
'options' : 12,
'key_item_drop' : KeyItemCodes.MANOR_FLOOR1_KEY.value
},

    18 : {
'type' : RoomType.STANDARD,
'entry_text' : [
'''You take a look at the front door.''',
'''Nothing about it stands out.'''
],
'second_arrival_text' : '''Still, nothing stands out about the door.''',
'options' : 12,
},

    18_001 : {
'type' : RoomType.STANDARD,
'entry_text' : [
'''You take a look at the front door.''',
'''Nothing about it stands out, but you feel like you're missing something important.'''
],
'second_arrival_text' : [
'''Still, nothing stands out about the door.''',
'''But you can't help but feel like you're missing something.'''
],
'options' : 18_002,
},

    18_002 : {
'type' : RoomType.STANDARD,
'entry_text' : [
'''This place is creeping you out.''',
'''You consider going outside to get some fresh air. Maybe it will help a little bit.'''
],
'second_arrival_text' : ['''...''', '''You consider going outside to calm down a bit.'''],
'options' : {'Go outside' : 19_001, "Don't go outside" : 19},
},

    19 : {
'type' : RoomType.STANDARD,
'entry_text' : '''You decide not to go outside.''',
'options' : 12,   
},

    19_001: {
'type' : RoomType.STANDARD,
'entry_text' : [
'''You open the door and go outside.''',
'''The good weather is refreshing and calming.''',
'''You think about leaving.''',
'''After all, there's nothing that forces you to stay here...'''
],
'options' : {'Leave' : 19_002, "Go back in" : 19_003},
},

    19_002 : {
'type' : RoomType.STANDARD,
'entry_text' : [
f'''This place is creeping you out too much.''',
f'''The fresh air managed to calm you down a bit, but not enough to willingly go back in.''', #this line feels weird
f'''You walk away from the house.''',
f'''...''',
f'''You feel like you just forgot something important.''',
f'''No, you {italic('definitively')} forgot something important.'''
],
'options' : 'ENDING AVOID_DANGER_B'
},

    19_003 : {
'type' : RoomType.STANDARD,
'entry_text' : [
f'''Despite your fears, you decided to stay here and figure out what this place's deal is.''',
'''Going outside managed to calm you down a bit.'''
],
'options' : 12    
},

    20 : {
'type' : RoomType.STANDARD,
'entry_text' : [
'''You decide to go up the stairs.''',
'''At the top, you notice that the door to the second floor is locked, for some reason.''',
'''It looks like you'll need a key to unlock it.'''
],
'second_arrival_text' : '''You try to go upstairs, but it's locked.''',
'options' : 21_001,
},

    20_001 : {
'type' : RoomType.STANDARD,
'entry_text' : [
'''You go up the stairs and try to unlock the door with the key you have.''',
'''*click*''',
'''The door unlocks.'''
],
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
'''...''',
'''It's completely empty.''', #2
'''No rooms, no walls, no furniture...''',
'''Nothing apart from a single key on the middle of the floor.''', #4
'''You feel like it could be useful, but something tells you you should leave it there.''', 
'''This place is really starting to unsettle you...''', #6
'''Before you can make a decision, something catches your attention.''', #7
'''There seems to be a message written on a sticky note taped to the wall.''', #8
f'''{italic("don't go in the basement it made me forget")}''', #9
'''!''',
'''As you read the message, it starts vanishing in front of your very eyes.''',
'''In the blink of an eye, it's completely gone.''',
'''...''',
'''You look back at the key in the middle of the room...''',
'''The key is still there.''',
'''You decide to...'''
],
'second_arrival_text' : '''You ponder about taking the key you left on the floor.\nYou decide to...''',
'options' : {'Take the key' : 21_003, 'Leave the key' : 21_004},
},

    21_002 : {
'type' : RoomType.STANDARD,
'entry_text' : [
f'''You think about the note and the key and start wondering if you've made a mistake by coming to this place.''',
'''You hope that the awnser is no, but at this point you really can't be sure.'''
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
'entry_text' : [
'''After what you just saw, there's no way you're picking up that key.'''
],
'second_arrival_text' : '''You leave the key on the floor. Picking up that key can't possibly be a good idea...''',
'options' : 20_002
},


    21 : { #unused
'type' : RoomType.STANDARD,
'entry_text' : 'You arrive at the second floor. Where do you go?',
'second_arrival_text' : '''What now?''',
'options' : {'The first bedroom' : 22, 'The second bedroom' : 23, 'The storage room' : 25, #bedroom 3 = 24
             'A closet' : 27, 'The hallway' : 28, 'Downstairs' : 20_002}, #bathroom 2 = 26
},

    22 : { #unused
'type' : RoomType.STANDARD,
'entry_text' : '''Nothing in the first bedroom.''',
'second_arrival_text' : '''Nothing here.''',
'options' : 21,
},

    23 : { #unused
'type' : RoomType.STANDARD,
'entry_text' : '''Nothing in the second bedroom.''',
'second_arrival_text' : '''Nothing here.''',
'options' : 21,
},

    24 : { #unused
'type' : RoomType.STANDARD,
'entry_text' : '''Nothing in the third bedroom.''',
'second_arrival_text' : '''Nothing here.''',
'options' : 21,
},

    25 : { #unused
'type' : RoomType.STANDARD,
'entry_text' : '''Nothing here.''',
'second_arrival_text' : '''Nothing here.''',
'options' : 21,
},

    26 : { #unused
'type' : RoomType.STANDARD,
'entry_text' : '''Nothing in the second bathroom.''',
'second_arrival_text' : '''Nothing here.''',
'options' : 21,
},

    27 : { #unused
'type' : RoomType.STANDARD,
'entry_text' : f'''{TF.format('Basement key obtained!', TextColorTags.BRIGHT_YELLOW)}''',
'second_arrival_text' : '''Nothing here.''',
'options' : 21,
'key_item_drop' : KeyItemCodes.MANOR_BASEMENT_KEY.value
},

    28 : { #unused
'type' : RoomType.STANDARD,
'entry_text' : '''Nothing here.''',
'second_arrival_text' : '''Nothing here.''',
'options' : 21,
},

    29 : {
'type' : RoomType.STANDARD,
'entry_text' : [
'''You walk up to the basement door and notice it's locked.''',
'''Unfortunately, you don't have the right key to open it.''',
'''It looks like if you want to get in there, you'll have to search around for the basement key.'''
],
'second_arrival_text' : '''You need a key to open this door.''',
'alternate_text' : [[
'''You walk up to the basement door and notice it's locked.''',
'''You don't have the right key to open it.''',
'''It looks like if you want to get in there, you'll have to search around for the basement key.''', #High alert first entry
'''But finding out what's in there isn't a particularly tempting offer.'''
],[
'''If, for some reason, you decide to go in, you'll need a key to open this door.''' #High alert second arrival
],
],
'options' : 12,
},

    29_001 : { #low alert
'type' : RoomType.STANDARD,
'entry_text' : [
'''You stroll up to the basement door, key in hand.''',
'''You're fairly hesitant about going in there, but if you want to figure out what's going on here...''',
'''You have to go down.'''
],
'second_arrival_text' : '''You think about finally going in the basement. You hesitate a bit.''',
'options' : {'Go in' : 30, 'Go back' : 30_001},
},

    29_002 : { #high alert
'type' : RoomType.STANDARD,
'entry_text' : [
'''You walk up to the basement door, key in hand.''',
f'''You {italic('really')} don't want to go in there.''',
'''If there's nothing in the basement, then it's just a waste of time.''',
'''But if there really is something in there...''',
'''...''',
'''Everything about this seems like a terrible idea, but your curiosity won't just let you walk away.'''
],
'second_arrival_text' : '''You think about using the key.''',
'options' : {'Open the door' : 30_002, 'Go back' : 30_001},
},


    30 : {
'type' : RoomType.STANDARD,
'entry_text' : '''You open the door and walk into the basement.''',
'options' : 31,
},


    30_001 : {
'type' : RoomType.STANDARD,
'entry_text' : '''You decide not to go in. Not yet, atleast.''',
'options' : 12,
},

    30_002 : {
'type' : RoomType.STANDARD,
'entry_text' : [
'''You open the door and take a peek.''',
'''All you see is a staircase going down into complete darkness.''',
'''You try to use your flashlight to figure out how deep the stairs go,''',
'''The obscurity is not very reassuring.''',
'''You consider what to do.'''
],
'second_arrival_text' : '''You consider going in the basement. It feels like a terrible idea, but your curiosity says otherwise.''',
'options' : {'Go in' : 30_003, 'Go back' : 30_004},
},

    30_005 : {
'type' : RoomType.STANDARD,
'entry_text' : '''You consider going in the basement.''',
'options' : {'Go in' : 30_003, 'Go back' : 30_004},
},

    30_003 : {
'type' : RoomType.STANDARD,
'entry_text' : '''You choose to walk into the basement.''',
'options' : 31,
},

    30_004 : {
'type' : RoomType.STANDARD,
'entry_text' : '''You choose to go back. No way you're going in there...''',
'options' : 12,
},

    31 : { #This might need a bit more panicking
'type' : RoomType.STANDARD,
'entry_text' :  [
'''As you take your first steps, you already start regretting your decision.''',
'''A chill runs down your spine.''', #this line is weird
'''But before you can even consider getting out...''',
'''*BLAM!*''',
'''The door closes by itself.''',
'''You try to open it back up.''',
'''It's locked!''',
'''You try to use the basement key to open the door back up, but then you notice that the lock 
on the inside needs a completely different key than the lock on the outside.''',
'''...''',
'''Looks like you only have one way forwards. Unless...'''
],
'second_arrival_text' : '''Surely, there's something you can do...''',
'options' : {'Call for help' : 32, 'Go deeper' : 34, 'Break the door open' : 33},
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
'options' : 35
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
'TUBMLE' : {
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
},
'AVOID_DANGER_B' : {
'ending_name' : 'Good Ending: Spooked',
'ending_text' : 'Although you got a bit scared, you manged to stay out of trouble.',
'retryable' : True,
'retry_checkpoint' : 'Chapter1Start'
},
'ESCAPE' : {
'ending_name' : 'Good Ending: Escaped',
'ending_text' : "You managed to escape the basement. Too bad you won't remember any of it...",
'retryable' : True,
'retry_checkpoint' : 'Chapter2Start'
},
}

game = Game()
current_save_file : str|None = None
first_room : bool = True
if not os.path.isdir('saves'):
    try:
        os.makedirs('saves')
    except FileExistsError:
        os.remove('saves')
        os.makedirs('saves')

def main():
    global current_save_file, game, first_room
    decision = crossplatform_input('Enter "new save" to make a new save. Enter anything else to continue a save.\n').lower()
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
                save_choice = crossplatform_input("What save do you want to load?\n")
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
            save_name = crossplatform_input("What will this new save be called?\n")
            if not all([character in allow_list or character.isalnum() for character in save_name]): print("Invalid! (Invalid character was used)"); continue
            if len(save_name) > 20: print("Invalid! (Save name is max 20 characters)"); continue
            if save_name == 'new save': print("Invalid! (Cannot use this name)"); continue
            if not save_name[0].isalpha() : print("Invalid (Dosen't start with a letter!)"); continue
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
            if game.room_number == 0: first_room = False
            room = Room(game.room_number)
            game.has_visited[game.room_number] += 1
            room.enter()
            room_result : str|int = room.manage()

            if type(room_result) == int:
                game.room_number = room_result
            elif type(room_result) == str:
                break
            game.temp_data.clear()
            first_room = False

        if type(room_result) != str:
            print('DEMO END - Your progress from this session will not be saved!')
            response : str = crossplatform_input("Do you want to play again? Input Y/yes to restart. This will wipe your save.\n").lower()
            if response == 'y' or response == 'yes':
                game.reset()
                continue
            print('Goodbye!')
            stall()
            close_everything()

        words = room_result.split()
        if words[0] == 'END':
            print('DEMO END - Your progress from this session will not be saved!')
            response : str = crossplatform_input("Do you want to play again? Input Y/yes to restart. This will wipe your save.\n").lower()
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
                response : str = crossplatform_input('Input "quit" to exit the game. Input anything else to go back to a checkpoint and retry.\n').lower()
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
            response : str = crossplatform_input("Do you want to play again from the start? Input Y/yes to restart. This will wipe your save.\n").lower()
            if response == 'y' or response == 'yes':
                game.reset()
                clear_console()
                continue
            print('Goodbye!')
            stall()
            close_everything()

main()