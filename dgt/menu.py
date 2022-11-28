# Copyright (C) 2013-2018 Jean-Francois Romang (jromang@posteo.de)
#                         Shivkumar Shivaji ()
#                         Jürgen Précour (LocutusOfPenguin@posteo.de)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import os
import logging
from configobj import ConfigObj  # type: ignore
from collections import OrderedDict
from typing import Dict, List, Set

import chess  # type: ignore
from timecontrol import TimeControl
from utilities import Observable, DispatchDgt, get_tags, version, write_picochess_ini
from dgt.util import TimeMode, TimeModeLoop, Top, TopLoop, Mode, ModeLoop, Language, LanguageLoop, BeepLevel, BeepLoop, EBoard, EBoardLoop, EngineTop, EngineTopLoop
from dgt.util import System, SystemLoop, Display, DisplayLoop, ClockIcons, Voice, VoiceLoop, Info, InfoLoop, PicoTutor, Game, GameLoop, GameSave, GameSaveLoop, GameRead, GameReadLoop, PicoComment, PicoCommentLoop
from dgt.api import Dgt, Event
from dgt.translate import DgtTranslate


class MenuState(object):

    """Keep the current DgtMenu State."""

    TOP = 100000

    MODE = 200000
    MODE_TYPE = 210000  # normal, observe, ...

    POS = 300000
    POS_COL = 310000
    POS_REV = 311000
    POS_UCI = 311100
    POS_READ = 311110

    TIME = 400000
    TIME_BLITZ = 410000  # blitz, fischer, fixed
    TIME_BLITZ_CTRL = 411000  # time_control objs
    TIME_FISCH = 420000
    TIME_FISCH_CTRL = 421000
    TIME_FIXED = 430000
    TIME_FIXED_CTRL = 431000
    TIME_TOURN = 440000         # molli: tournament
    TIME_TOURN_CTRL = 441000    # molli: tournament
    TIME_DEPTH = 450000         # molli: search depth
    TIME_DEPTH_CTRL = 451000    # molli: search depth

    BOOK = 500000
    BOOK_NAME = 510000

    ENGINE = 550000

    ENG_MODERN = 600000
    ENG_MODERN_NAME = 610000
    ENG_MODERN_NAME_LEVEL = 611000

    ENG_RETRO = 630000
    ENG_RETRO_NAME = 631000
    ENG_RETRO_NAME_LEVEL = 631100

    ENG_FAV = 650000
    ENG_FAV_NAME = 651000
    ENG_FAV_NAME_LEVEL = 651100

    SYS = 700000
    SYS_INFO = 710000
    SYS_INFO_VERS = 711000
    SYS_INFO_IP = 712000
    SYS_INFO_BATTERY = 713000
    SYS_SOUND = 720000
    SYS_SOUND_BEEP = 721000  # never, always, some
    SYS_LANG = 730000
    SYS_LANG_NAME = 731000  # de, en, ...
    SYS_LOG = 740000
    SYS_VOICE = 750000
    SYS_VOICE_USER = 751000  # user
    SYS_VOICE_USER_MUTE = 751100  # on, off
    SYS_VOICE_USER_MUTE_LANG = 751110  # de, en, ...
    SYS_VOICE_USER_MUTE_LANG_SPEAK = 751111  # al, christina, ...
    SYS_VOICE_COMP = 752000  # computer
    SYS_VOICE_COMP_MUTE = 752100  # on, off
    SYS_VOICE_COMP_MUTE_LANG = 752110  # de, en, ...
    SYS_VOICE_COMP_MUTE_LANG_SPEAK = 752111  # al, christina, ...
    SYS_VOICE_SPEED = 753000  # vspeed
    SYS_VOICE_SPEED_FACTOR = 753100  # 0-7
    SYS_VOICE_VOLUME = 754000
    SYS_VOICE_VOLUME_FACTOR = 754100
    SYS_DISP = 760000
    SYS_DISP_CONFIRM = 761000
    SYS_DISP_CONFIRM_YESNO = 761100  # yes,no
    SYS_DISP_PONDER = 762000
    SYS_DISP_PONDER_INTERVAL = 762100  # 1-8
    SYS_DISP_CAPITAL = 763000
    SYS_DISP_CAPTIAL_YESNO = 763100  # yes, no
    SYS_DISP_NOTATION = 764000
    SYS_DISP_NOTATION_MOVE = 764100  # short, long
    SYS_DISP_ENGINENAME = 765000        # molli v3
    SYS_DISP_ENGINENAME_YESNO = 765100  # yes,no ## molli v3
    SYS_EBOARD = 770000
    SYS_EBOARD_TYPE = 771000  # dgt, chesslink, ...

    PICOTUTOR = 800000
    PICOTUTOR_PICOWATCHER = 810000
    PICOTUTOR_PICOWATCHER_ONOFF = 811000  # on,off
    PICOTUTOR_PICOCOACH = 820000
    PICOTUTOR_PICOCOACH_ONOFF = 821000  # on,off
    PICOTUTOR_PICOEXPLORER = 830000
    PICOTUTOR_PICOEXPLORER_ONOFF = 831000  # all, eng, off
    PICOTUTOR_PICOCOMMENT = 840000
    PICOTUTOR_PICOCOMMENT_OFF = 841000
    PICOTUTOR_PICOCOMMENT_ON_ENG = 842000
    PICOTUTOR_PICOCOMMENT_ON_ALL = 843000

    GAME = 900000
    GAME_GAMESAVE = 910000
    GAME_GAMESAVE_GAME1 = 911000
    GAME_GAMESAVE_GAME2 = 912000
    GAME_GAMESAVE_GAME3 = 913000
    GAME_GAMEREAD = 920000
    GAME_GAMEREAD_GAMELAST = 921000
    GAME_GAMEREAD_GAME1 = 922000
    GAME_GAMEREAD_GAME2 = 923000
    GAME_GAMEREAD_GAME3 = 924000
    GAME_GAMEALTMOVE = 930000
    GAME_GAMEALTMOVE_ONOFF = 931000
    GAME_GAMECONTLAST = 940000
    GAME_GAMECONTLAST_ONOFF = 941000


class DgtMenu(object):

    """Handle the Dgt Menu."""

    def __init__(self, disable_confirm: bool, ponder_interval: int,
                 user_voice: str, comp_voice: str, speed_voice: int, enable_capital_letters: bool,
                 disable_short_move: bool, log_file, engine_server, rol_disp_norm: bool,
                 volume_voice: int, board_type: str,
                 rol_disp_brain: bool, show_enginename: bool, dgttranslate: DgtTranslate):
        super(DgtMenu, self).__init__()

        self.current_text = None  # save the current text

        logging.debug('molli: roll.norm %s', str(rol_disp_norm))
        logging.debug('molli: roll.brain %s', str(rol_disp_brain))
        self.menu_system_display_rolldispnorm = rol_disp_norm
        self.menu_system_display_rolldispbrain = rol_disp_brain

        self.menu_system_display_enginename = show_enginename

        self.menu_picotutor = PicoTutor.WATCHER
        self.menu_picotutor_picowatcher = False
        self.menu_picotutor_picocoach = False
        self.menu_picotutor_picoexplorer = False
        self.menu_picotutor_picocomment = PicoComment.COM_OFF

        self.menu_game = Game.SAVE
        self.menu_game_save = GameSave.GAME1
        self.menu_game_read = GameRead.GAMELAST
        self.menu_game_altmove = True
        self.menu_game_contlast = True

        self.menu_system_display_confirm = disable_confirm
        self.menu_system_display_ponderinterval = ponder_interval
        self.menu_system_display_capital = enable_capital_letters
        self.menu_system_display_notation = disable_short_move  # True = disable short move display => long display
        self.log_file = log_file
        self.remote_engine = bool(engine_server)
        self.dgttranslate = dgttranslate
        if show_enginename:
            self.state = MenuState.ENG_MODERN_NAME
        else:
            self.state = MenuState.TOP

        self.dgt_fen = '8/8/8/8/8/8/8/8'
        self.int_ip = None
        self.ext_ip = None
        self.flip_board = False

        self.menu_position_whitetomove = True
        self.menu_position_reverse = False
        self.menu_position_uci960 = False

        if show_enginename:
            self.menu_top = Top.ENGINE
        else:
            self.menu_top = Top.MODE

        self.menu_mode = Mode.NORMAL
        self.engine_has_960 = False
        self.engine_has_ponder = False
        self.engine_restart = False

        self.installed_engines: List[Dict[str, str]] = []  # list of all engines available, sum of modern+retro engines
        self.menu_engine_index = 0
        self.menu_engine_level = 0
        self.menu_modern_engine_index = 0
        self.menu_modern_engine_level = 0
        self.installed_modern_engines: List[Dict[str, str]] = []  # list of all modern engines
        self.menu_retro_engine_index = 0
        self.menu_retro_engine_level = 0
        self.installed_retro_engines: List[Dict[str, str]] = []  # list of all retro engines
        self.menu_fav_engine_index = 0
        self.menu_fav_engine_level = 0
        self.installed_fav_engines: List[Dict[str, str]] = []  # favorites, selection from all available engines
        self.menu_engine = EngineTop.MODERN_ENGINE

        self.menu_book = 0
        self.all_books: List[Dict[str, str]] = []

        self.menu_system = System.INFO
        self.menu_system_sound = self.dgttranslate.beep

        langs = {'en': Language.EN, 'de': Language.DE, 'nl': Language.NL,
                 'fr': Language.FR, 'es': Language.ES, 'it': Language.IT}
        self.menu_system_language = langs[self.dgttranslate.language]

        self.voices_conf = ConfigObj('talker' + os.sep + 'voices' + os.sep + 'voices.ini')
        self.menu_system_voice = Voice.COMP
        self.menu_system_voice_user_active = bool(user_voice)
        self.menu_system_voice_comp_active = bool(comp_voice)
        try:
            (user_language_name, user_speaker_name) = user_voice.split(':')
            self.menu_system_voice_user_lang = self.voices_conf.keys().index(user_language_name)
            self.menu_system_voice_user_speak = self.voices_conf[user_language_name].keys().index(user_speaker_name)
        except (AttributeError, ValueError):  # None = "not set" throws an AttributeError
            self.menu_system_voice_user_lang = 0
            self.menu_system_voice_user_speak = 0
        try:
            (comp_language_name, comp_speaker_name) = comp_voice.split(':')
            self.menu_system_voice_comp_lang = self.voices_conf.keys().index(comp_language_name)
            self.menu_system_voice_comp_speak = self.voices_conf[comp_language_name].keys().index(comp_speaker_name)
        except (AttributeError, ValueError):  # None = "not set" throws an AttributeError
            self.menu_system_voice_comp_lang = 0
            self.menu_system_voice_comp_speak = 0

        self.menu_system_voice_speedfactor = speed_voice
        self.menu_system_voice_volumefactor = volume_voice

        self.board_type = board_type
        eboards = {'certabo': EBoard.CERTABO, 'chesslink': EBoard.CHESSLINK, 'chessnut': EBoard.CHESSNUT,
                   'dgt': EBoard.DGT}
        self.menu_system_eboard_type = eboards[board_type]

        self.menu_system_display = Display.PONDER
        self.menu_system_info = Info.VERSION

        self.menu_time_mode = TimeMode.BLITZ

        self.menu_time_fixed = 0
        self.menu_time_blitz = 2  # Default time control: Blitz, 5min
        self.menu_time_fisch = 0
        self.menu_time_tourn = 0
        self.menu_time_depth = 0

        self.tc_fixed_list = [' 1', ' 3', ' 5', '10', '15', '30', '60', '90']
        self.tc_blitz_list = [' 1', ' 3', ' 5', '10', '15', '30', '60', '90']
        self.tc_fisch_list = [' 1  1', ' 3  2', ' 5  3', '10  5', '15 10', '30 15', '60 20', '90 30', ' 0  5', ' 0 10', ' 0 15', ' 0 20', ' 0 30', ' 0 60', ' 0 90']
        self.tc_tourn_list = ['10 10 0 5', '20 15 0 15', '30 40 0 15', '40 120 0 90', '40 60 15 30', '40 60 30 30', '40 90 30 30', '40 90 15 60', '40 90 30 60']
        self.tc_depth_list = [' 1', ' 2', ' 3', ' 4', '10', '15', '20', '25']

        self.tc_fixed_map = OrderedDict([
            ('rnbqkbnr/pppppppp/Q7/8/8/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FIXED, fixed=1)),
            ('rnbqkbnr/pppppppp/1Q6/8/8/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FIXED, fixed=3)),
            ('rnbqkbnr/pppppppp/2Q5/8/8/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FIXED, fixed=5)),
            ('rnbqkbnr/pppppppp/3Q4/8/8/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FIXED, fixed=10)),
            ('rnbqkbnr/pppppppp/4Q3/8/8/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FIXED, fixed=15)),
            ('rnbqkbnr/pppppppp/5Q2/8/8/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FIXED, fixed=30)),
            ('rnbqkbnr/pppppppp/6Q1/8/8/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FIXED, fixed=60)),
            ('rnbqkbnr/pppppppp/7Q/8/8/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FIXED, fixed=90))])
        self.tc_blitz_map = OrderedDict([
            ('rnbqkbnr/pppppppp/8/8/Q7/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.BLITZ, blitz=1)),
            ('rnbqkbnr/pppppppp/8/8/1Q6/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.BLITZ, blitz=3)),
            ('rnbqkbnr/pppppppp/8/8/2Q5/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.BLITZ, blitz=5)),
            ('rnbqkbnr/pppppppp/8/8/3Q4/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.BLITZ, blitz=10)),
            ('rnbqkbnr/pppppppp/8/8/4Q3/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.BLITZ, blitz=15)),
            ('rnbqkbnr/pppppppp/8/8/5Q2/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.BLITZ, blitz=30)),
            ('rnbqkbnr/pppppppp/8/8/6Q1/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.BLITZ, blitz=60)),
            ('rnbqkbnr/pppppppp/8/8/7Q/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.BLITZ, blitz=90))])
        self.tc_fisch_map = OrderedDict([
            ('rnbqkbnr/pppppppp/8/8/8/Q7/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FISCHER, blitz=1, fischer=1)),
            ('rnbqkbnr/pppppppp/8/8/8/1Q6/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FISCHER, blitz=3, fischer=2)),
            ('rnbqkbnr/pppppppp/8/8/8/2Q5/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FISCHER, blitz=5, fischer=3)),
            ('rnbqkbnr/pppppppp/8/8/8/3Q4/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FISCHER, blitz=10, fischer=5)),
            ('rnbqkbnr/pppppppp/8/8/8/4Q3/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FISCHER, blitz=15, fischer=10)),
            ('rnbqkbnr/pppppppp/8/8/8/5Q2/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FISCHER, blitz=30, fischer=15)),
            ('rnbqkbnr/pppppppp/8/8/8/6Q1/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FISCHER, blitz=60, fischer=20)),
            ('rnbqkbnr/pppppppp/8/8/8/7Q/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FISCHER, blitz=90, fischer=30)),
            ('8/8/8/8/k1K5/8/8/8', TimeControl(TimeMode.FISCHER, blitz=0, fischer=5)),
            ('8/8/8/8/1k1K4/8/8/8', TimeControl(TimeMode.FISCHER, blitz=0, fischer=10)),
            ('8/8/8/8/2k1K3/8/8/8', TimeControl(TimeMode.FISCHER, blitz=0, fischer=15)),
            ('8/8/8/8/3k1K2/8/8/8', TimeControl(TimeMode.FISCHER, blitz=0, fischer=20)),
            ('8/8/8/8/4k1K1/8/8/8', TimeControl(TimeMode.FISCHER, blitz=0, fischer=30)),
            ('8/8/8/8/5k1K/8/8/8', TimeControl(TimeMode.FISCHER, blitz=0, fischer=60)),
            ('8/8/8/8/k2K4/8/8/8', TimeControl(TimeMode.FISCHER, blitz=0, fischer=90))])
        self.tc_tourn_map = OrderedDict([
            ('rnbqkbnr/pppppppp/8/8/8/Qq6/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.BLITZ, blitz=10, fischer=0, moves_to_go=10, blitz2=5)),
            ('rnbqkbnr/pppppppp/8/8/8/Q6q/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.BLITZ, blitz=15, fischer=0, moves_to_go=20, blitz2=15)),
            ('rnbqkbnr/pppppppp/8/8/8/1Q5q/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.BLITZ, blitz=30, fischer=0, moves_to_go=40, blitz2=15)),
            ('rnbqkbnr/pppppppp/8/8/8/2Q4q/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.BLITZ, blitz=120, fischer=0, moves_to_go=40, blitz2=90)),
            ('rnbqkbnr/pppppppp/8/8/8/3Q3q/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FISCHER, blitz=60, fischer=15, moves_to_go=40, blitz2=30)),
            ('rnbqkbnr/pppppppp/8/8/8/4Q2q/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FISCHER, blitz=60, fischer=30, moves_to_go=40, blitz2=30)),
            ('rnbqkbnr/ppppppp1/p7/8/8/5Q1q/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FISCHER, blitz=90, fischer=30, moves_to_go=40, blitz2=30)),
            ('rnbqkbnr/pppppppp/8/8/8/5Q1q/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FISCHER, blitz=90, fischer=15, moves_to_go=40, blitz2=60)),
            ('rnbqkbnr/pppppppp/8/8/8/6Qq/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FISCHER, blitz=90, fischer=30, moves_to_go=40, blitz2=60))])
        self.tc_depth_map = OrderedDict([
             ('rnbqkbnr/pppppppp/8/8/Qq6/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FIXED, fixed=900, depth=1)),
             ('rnbqkbnr/pppppppp/8/8/Q6q/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FIXED, fixed=900, depth=2)),
             ('rnbqkbnr/pppppppp/8/8/1Q5q/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FIXED, fixed=900, depth=3)),
             ('rnbqkbnr/pppppppp/8/8/2Q4q/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FIXED, fixed=900, depth=4)),
             ('rnbqkbnr/pppppppp/8/8/3Q3q/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FIXED, fixed=900, depth=10)),
             ('rnbqkbnr/pppppppp/8/8/4Q2q/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FIXED, fixed=900, depth=15)),
             ('rnbqkbnr/pppppppp/8/8/5Q1q/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FIXED, fixed=900, depth=20)),
             ('rnbqkbnr/pppppppp/8/8/6Qq/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FIXED, fixed=900, depth=25))])

        # setup the result vars for api (dgtdisplay)
        self.save_choices()
        self.res_engine_index = self.menu_engine_index
        self.res_engine_level = self.menu_engine_level

        # During "picochess" is displayed, some special actions allowed
        self.picochess_displayed: Set[str] = set()
        self.updt_top = False  # inside the update-menu?
        self.updt_devs: Set[str] = set()  # list of devices which are inside the update-menu
        self.updt_tags: List[List[str]] = []
        self.updt_version = 0  # index to current version

        self.battery = '-NA'  # standard value: NotAvailable (discharging)
        self.inside_room = False

    def set_state_current_engine(self):
        self.state = MenuState.ENG_MODERN_NAME
        self.menu_top = Top.ENGINE

    def inside_updt_menu(self):
        """Inside update menu."""
        return self.updt_top

    def disable_picochess_displayed(self, dev):
        """Disable picochess display."""
        self.picochess_displayed.discard(dev)

    def enable_picochess_displayed(self, dev):
        """Enable picochess display."""
        self.picochess_displayed.add(dev)
        self.updt_tags = get_tags()
        try:
            self.updt_version = [item[1] for item in self.updt_tags].index(version)
        except ValueError:
            self.updt_version = len(self.updt_tags) - 1

    def inside_picochess_time(self, dev):
        """Picochess displayed on clock."""
        return dev in self.picochess_displayed

    def save_choices(self):
        """Save the user choices to the result vars."""
        self.state = MenuState.TOP

        self.res_mode = self.menu_mode

        self.res_position_whitetomove = self.menu_position_whitetomove
        self.res_position_reverse = self.menu_position_reverse
        self.res_position_uci960 = self.menu_position_uci960

        self.res_time_mode = self.menu_time_mode
        self.res_time_fixed = self.menu_time_fixed
        self.res_time_blitz = self.menu_time_blitz
        self.res_time_fisch = self.menu_time_fisch
        self.res_time_tourn = self.menu_time_tourn
        self.res_time_depth = self.menu_time_depth

        self.res_book_name = self.menu_book

        self.res_system_display_confirm = self.menu_system_display_confirm
        self.res_system_display_ponderinterval = self.menu_system_display_ponderinterval
        self.res_system_display_rolldispnorm = self.menu_system_display_rolldispnorm
        self.res_system_display_rolldispbrain = self.menu_system_display_rolldispbrain
        self.res_system_display_rolldispbrain = self.menu_system_display_rolldispbrain
        self.res_system_display_enginename = self.menu_system_display_enginename
        self.res_picotutor_picocoach = self.menu_picotutor_picocoach
        self.res_picotutor_picowatcher = self.menu_picotutor_picowatcher
        self.res_picotutor_picoexplorer = self.menu_picotutor_picoexplorer
        self.res_picotutor = self.menu_picotutor

        self.res_game_game_save = self.menu_game_save
        self.res_game_game_read = self.menu_game_read
        self.res_game_altmove = self.menu_game_altmove
        self.res_game_contlast = self.menu_game_contlast

        self.res_picotutor_picocomment = self.menu_picotutor_picocomment

        self.dgttranslate.set_capital(self.menu_system_display_capital)
        self.dgttranslate.set_notation(self.menu_system_display_notation)
        return False

    def set_engine_restart(self, flag: bool):
        """Set the flag."""
        self.engine_restart = flag

    def get_engine_restart(self):
        """Get the flag."""
        return self.engine_restart

    def get_flip_board(self):
        """Get the flag."""
        return self.flip_board

    def get_engine_has_960(self):
        """Get the flag."""
        return self.engine_has_960

    def set_engine_has_960(self, flag: bool):
        """Set the flag."""
        self.engine_has_960 = flag

    def get_engine_has_ponder(self):
        """Get the flag."""
        return self.engine_has_ponder

    def set_engine_has_ponder(self, flag: bool):
        """Set the flag."""
        self.engine_has_ponder = flag

    def get_dgt_fen(self):
        """Get the flag."""
        return self.dgt_fen

    def set_dgt_fen(self, fen: str):
        """Set the flag."""
        self.dgt_fen = fen

    def get_mode(self):
        """Get the flag."""
        return self.res_mode

    def set_mode(self, mode: Mode):
        """Set the flag."""
        self.res_mode = self.menu_mode = mode

    def get_engine(self):
        return self.installed_engines[self.res_engine_index]

    def set_engine_index(self, index: int):
        self.res_engine_index = self.menu_engine_index = index

    def get_engine_level(self):
        return self.res_engine_level

    def set_engine_level(self, level: int):
        self.res_engine_level = self.menu_engine_level = level

    def set_modern_engines(self, modern_engines):
        self.installed_modern_engines = modern_engines

    def set_retro_engines(self, retro_engines):
        self.installed_retro_engines = retro_engines

    def set_favorite_engines(self, fav_engines):
        self.installed_fav_engines = fav_engines

    def set_enginename(self, showname: bool):
        """Set the flag."""
        self.res_system_display_enginename = showname

    def get_enginename(self):
        """Get the flag."""
        return self.res_system_display_enginename

    def set_picowatcher(self, picowatcher: bool):
        """Set the flag."""
        self.res_picotutor_picowatcher = picowatcher
        self.menu_picotutor_picowatcher = picowatcher

    def get_picowatcher(self):
        """Get the flag."""
        return self.res_picotutor_picowatcher

    def set_picocoach(self, picocoach: bool):
        """Set the flag."""
        self.res_picotutor_picocoach = picocoach
        self.menu_picotutor_picocoach = picocoach

    def get_picocoach(self):
        """Get the flag."""
        return self.res_picotutor_picocoach

    def set_picocomment(self, picocomment: PicoComment):
        """Set the flag."""
        self.res_picotutor_picocomment = picocomment
        self.menu_picotutor_picocomment = picocomment

    def get_picocomment(self):
        """Get the flag."""
        return self.res_picotutor_picocomment

    def set_picoexplorer(self, picoexplorer: bool):
        """Set the flag."""
        self.res_picotutor_picoexplorer = picoexplorer
        self.menu_picotutor_picoexplorer = picoexplorer

    def get_picoexplorer(self):
        """Get the flag."""
        return self.res_picotutor_picoexplorer

    def set_game_altmove(self, altmove: bool):
        """Set the flag."""
        self.res_game_altmove = altmove
        self.menu_game_altmove = altmove

    def get_game_altmove(self):
        """Get the flag."""
        return self.res_game_altmove

    def set_game_contlast(self, contlast: bool):
        """Set the flag."""
        self.res_game_contlast = contlast
        self.menu_game_contlast = contlast

    def get_game_contlast(self):
        """Get the flag."""
        return self.res_game_contlast

    def get_confirm(self):
        """Get the flag."""
        return self.res_system_display_confirm

    def set_book(self, index: int):
        """Set the flag."""
        self.res_book_name = self.menu_book = index

    def set_time_mode(self, mode: TimeMode):
        """Set the flag."""
        self.res_time_mode = self.menu_time_mode = mode

    def get_time_mode(self):
        """Get the flag."""
        return self.res_time_mode

    def set_time_fixed(self, index: int):
        """Set the flag."""
        self.res_time_fixed = self.menu_time_fixed = index

    def get_time_fixed(self):
        """Get the flag."""
        return self.res_time_fixed

    def set_time_blitz(self, index: int):
        """Set the flag."""
        self.res_time_blitz = self.menu_time_blitz = index

    def get_time_blitz(self):
        """Get the flag."""
        return self.res_time_blitz

    def set_time_fisch(self, index: int):
        """Set the flag."""
        self.res_time_fisch = self.menu_time_fisch = index

    def get_time_fisch(self):
        """Get the flag."""
        return self.res_time_fisch

    def set_time_tourn(self, index: int):
        """Set the flag."""
        self.res_time_tourn = self.menu_time_tourn = index

    def get_time_tourn(self):
        """Get the flag."""
        return self.res_time_tourn

    def set_time_depth(self, index: int):
        """Set the flag."""
        self.res_time_depth = self.menu_time_depth = index

    def get_time_depth(self):
        """Get the flag."""
        return self.res_time_depth

    def set_position_reverse_flipboard(self, flip_board):
        """Set the flag."""
        self.res_position_reverse = self.flip_board = flip_board

    def get_position_reverse_flipboard(self):
        """Get the flag."""
        return self.res_position_reverse

    def get_ponderinterval(self):
        """Get the flag."""
        return self.res_system_display_ponderinterval

    def get_rolldispnorm(self):
        """Get the flag."""
        return self.res_system_display_rolldispnorm

    def get_rolldispbrain(self):
        """Get the flag."""
        return self.res_system_display_rolldispbrain

    def get(self):
        """Get the current state."""
        return self.state

    def enter_top_menu(self):
        """Set the menu state."""
        self.state = MenuState.TOP
        self.current_text = None
        return False

    def enter_mode_menu(self):
        """Set the menu state."""
        self.state = MenuState.MODE
        text = self.dgttranslate.text(Top.MODE.value)
        return text

    def enter_mode_type_menu(self):
        """Set the menu state."""
        self.state = MenuState.MODE_TYPE
        text = self.dgttranslate.text(self.menu_mode.value)
        return text

    def enter_picotutor_menu(self):
        """Set the picotutor state."""
        self.state = MenuState.PICOTUTOR
        text = self.dgttranslate.text(Top.PICOTUTOR.value)
        return text

    def enter_picotutor_picowatcher_menu(self):
        """Set the picowatcher state."""
        self.state = MenuState.PICOTUTOR_PICOWATCHER
        text = self.dgttranslate.text('B00_picowatcher')
        return text

    def enter_picotutor_picowatcher_onoff_menu(self):
        """Set the menu state."""
        self.state = MenuState.PICOTUTOR_PICOWATCHER_ONOFF
        msg = 'on' if self.menu_picotutor_picowatcher else 'off'
        text = self.dgttranslate.text('B00_picowatcher_' + msg)
        return text

    def enter_picotutor_picocoach_menu(self):
        """Set the picowcoach state."""
        self.state = MenuState.PICOTUTOR_PICOCOACH
        text = self.dgttranslate.text('B00_picocoach')
        return text

    def enter_picotutor_picocoach_onoff_menu(self):
        """Set the menu state."""
        self.state = MenuState.PICOTUTOR_PICOCOACH_ONOFF
        msg = 'on' if self.menu_picotutor_picocoach else 'off'
        text = self.dgttranslate.text('B00_picocoach_' + msg)
        return text

    def enter_picotutor_picoexplorer_menu(self):
        """Set the picoeplorer state."""
        self.state = MenuState.PICOTUTOR_PICOEXPLORER
        text = self.dgttranslate.text('B00_picoexplorer')
        return text

    def enter_picotutor_picoexplorer_onoff_menu(self):
        """Set the menu state."""
        self.state = MenuState.PICOTUTOR_PICOEXPLORER_ONOFF
        msg = 'on' if self.menu_picotutor_picoexplorer else 'off'
        text = self.dgttranslate.text('B00_picoexplorer_' + msg)
        return text

    def enter_picotutor_picocomment_menu(self):
        """Set the picocomment state."""
        self.state = MenuState.PICOTUTOR_PICOCOMMENT
        text = self.dgttranslate.text('B00_picocomment')
        return text

    def enter_picotutor_picocomment_off_menu(self):
        """Set the gamesave state."""
        self.state = MenuState.PICOTUTOR_PICOCOMMENT_OFF
        text = self.dgttranslate.text('B00_picocomment_off')
        return text

    def enter_picotutor_picocomment_on_eng_menu(self):
        """Set the picocomment state."""
        self.state = MenuState.PICOTUTOR_PICOCOMMENT_ON_ENG
        text = self.dgttranslate.text('B00_picocomment_on_eng')
        return text

    def enter_picotutor_picocomment_on_all_menu(self):
        """Set the picocomment state."""
        self.state = MenuState.PICOTUTOR_PICOCOMMENT_ON_ALL
        text = self.dgttranslate.text('B00_picocomment_on_all')
        return text

    def enter_game_menu(self):
        """Set the game state."""
        self.state = MenuState.GAME
        text = self.dgttranslate.text(Top.GAME.value)
        return text

    def enter_game_gamesave_menu(self):
        """Set the gamesave state."""
        self.state = MenuState.GAME_GAMESAVE
        text = self.dgttranslate.text(self.menu_game.value)
        return text

    def enter_game_gamesave_game1_menu(self):
        """Set the gamesave state."""
        self.state = MenuState.GAME_GAMESAVE_GAME1
        text = self.dgttranslate.text('B00_game_save_game1')
        return text

    def enter_game_gamesave_game2_menu(self):
        """Set the gamesave state."""
        self.state = MenuState.GAME_GAMESAVE_GAME2
        text = self.dgttranslate.text('B00_game_save_game2')
        return text

    def enter_game_gamesave_game3_menu(self):
        """Set the gamesave state."""
        self.state = MenuState.GAME_GAMESAVE_GAME3
        text = self.dgttranslate.text('B00_game_save_game3')
        return text

    def enter_game_gameread_menu(self):
        """Set the gameread state."""
        self.state = MenuState.GAME_GAMEREAD
        text = self.dgttranslate.text('B00_game_read_menu')
        return text

    def enter_game_gameread_gamelast_menu(self):
        """Set the gameread state."""
        self.state = MenuState.GAME_GAMEREAD_GAMELAST
        text = self.dgttranslate.text('B00_game_read_gamelast')
        return text

    def enter_game_gameread_game1_menu(self):
        """Set the gameread state."""
        self.state = MenuState.GAME_GAMEREAD_GAME1
        text = self.dgttranslate.text('B00_game_read_game1')
        return text

    def enter_game_gameread_game2_menu(self):
        """Set the gameread state."""
        self.state = MenuState.GAME_GAMEREAD_GAME2
        text = self.dgttranslate.text('B00_game_read_game2')
        return text

    def enter_game_gameread_game3_menu(self):
        """Set the gameread state."""
        self.state = MenuState.GAME_GAMEREAD_GAME3
        text = self.dgttranslate.text('B00_game_read_game3')
        return text

    def enter_game_contlast_menu(self):
        """Set the CONTLAST state."""
        self.state = MenuState.GAME_GAMECONTLAST
        text = self.dgttranslate.text('B00_game_contlast_menu')
        return text

    def enter_game_contlast_onoff_menu(self):
        """Set the menu state."""
        self.state = MenuState.GAME_GAMECONTLAST_ONOFF
        msg = 'on' if self.menu_game_contlast else 'off'
        text = self.dgttranslate.text('B00_game_contlast_' + msg)
        return text

    def enter_game_altmove_menu(self):
        """Set the ALTMOVE state."""
        self.state = MenuState.GAME_GAMEALTMOVE
        text = self.dgttranslate.text('B00_game_altmove_menu')
        return text

    def enter_game_altmove_onoff_menu(self):
        """Set the menu state."""
        self.state = MenuState.GAME_GAMEALTMOVE_ONOFF
        msg = 'on' if self.menu_game_altmove else 'off'
        text = self.dgttranslate.text('B00_game_altmove_' + msg)
        return text

    def enter_pos_menu(self):
        """Set the menu state."""
        self.state = MenuState.POS
        text = self.dgttranslate.text(Top.POSITION.value)
        return text

    def enter_pos_color_menu(self):
        """Set the menu state."""
        self.state = MenuState.POS_COL
        text = self.dgttranslate.text('B00_sidewhite' if self.menu_position_whitetomove else 'B00_sideblack')
        return text

    def enter_pos_rev_menu(self):
        """Set the menu state."""
        self.state = MenuState.POS_REV
        text = self.dgttranslate.text('B00_bw' if self.menu_position_reverse else 'B00_wb')
        return text

    def enter_pos_uci_menu(self):
        """Set the menu state."""
        self.state = MenuState.POS_UCI
        text = self.dgttranslate.text('B00_960yes' if self.menu_position_uci960 else 'B00_960no')
        return text

    def enter_pos_read_menu(self):
        """Set the menu state."""
        self.state = MenuState.POS_READ
        text = self.dgttranslate.text('B00_scanboard')
        return text

    def enter_time_menu(self):
        """Set the menu state."""
        self.state = MenuState.TIME
        text = self.dgttranslate.text(Top.TIME.value)
        return text

    def enter_time_blitz_menu(self):
        """Set the menu state."""
        self.state = MenuState.TIME_BLITZ
        text = self.dgttranslate.text(self.menu_time_mode.value)
        return text

    def enter_time_blitz_ctrl_menu(self):
        """Set the menu state."""
        self.state = MenuState.TIME_BLITZ_CTRL
        text = self.dgttranslate.text('B00_tc_blitz', self.tc_blitz_list[self.menu_time_blitz])
        return text

    def enter_time_fisch_menu(self):
        """Set the menu state."""
        self.state = MenuState.TIME_FISCH
        text = self.dgttranslate.text(self.menu_time_mode.value)
        return text

    def enter_time_fisch_ctrl_menu(self):
        """Set the menu state."""
        self.state = MenuState.TIME_FISCH_CTRL
        text = self.dgttranslate.text('B00_tc_fisch', self.tc_fisch_list[self.menu_time_fisch])
        return text

    def enter_time_fixed_menu(self):
        """Set the menu state."""
        self.state = MenuState.TIME_FIXED
        text = self.dgttranslate.text(self.menu_time_mode.value)
        return text

    def enter_time_fixed_ctrl_menu(self):
        """Set the menu state."""
        self.state = MenuState.TIME_FIXED_CTRL
        text = self.dgttranslate.text('B00_tc_fixed', self.tc_fixed_list[self.menu_time_fixed])
        return text

    def enter_time_tourn_menu(self):
        """Set the menu state."""
        self.state = MenuState.TIME_TOURN
        text = self.dgttranslate.text(self.menu_time_mode.value)
        return text

    def enter_time_tourn_ctrl_menu(self):
        """Set the menu state."""
        self.state = MenuState.TIME_TOURN_CTRL
        text = self.dgttranslate.text('B00_tc_tourn', self.tc_tourn_list[self.menu_time_tourn])
        return text

    def enter_time_depth_menu(self):
        """Set the menu state."""
        self.state = MenuState.TIME_DEPTH
        text = self.dgttranslate.text(self.menu_time_mode.value)
        return text

    def enter_time_depth_ctrl_menu(self):
        """Set the menu state."""
        self.state = MenuState.TIME_DEPTH_CTRL
        text = self.dgttranslate.text('B00_tc_depth', self.tc_depth_list[self.menu_time_depth])
        return text

    def enter_book_menu(self):
        """Set the menu state."""
        self.state = MenuState.BOOK
        text = self.dgttranslate.text(Top.BOOK.value)
        return text

    def _get_current_book_name(self):
        text = self.all_books[self.menu_book]['text']
        text.beep = self.dgttranslate.bl(BeepLevel.BUTTON)
        return text

    def enter_book_name_menu(self):
        """Set the menu state."""
        self.state = MenuState.BOOK_NAME
        return self._get_current_book_name()

    def enter_modern_eng_menu(self):
        """Set the menu state."""
        self.state = MenuState.ENG_MODERN
        text = self.dgttranslate.text(EngineTop.MODERN_ENGINE.value)
        return text

    def enter_retro_eng_menu(self):
        """Set the menu state."""
        self.state = MenuState.ENG_RETRO
        text = self.dgttranslate.text(EngineTop.RETRO_ENGINE.value)
        return text

    def enter_fav_eng_menu(self):
        """Set the menu state."""
        self.state = MenuState.ENG_FAV
        text = self.dgttranslate.text(EngineTop.FAV_ENGINE.value)
        return text

    def _get_current_modern_engine_name(self):
        text = self.installed_engines[self.menu_modern_engine_index]['text']
        text.beep = self.dgttranslate.bl(BeepLevel.BUTTON)
        return text

    def _get_current_retro_engine_name(self):
        text = self.installed_retro_engines[self.menu_retro_engine_index]['text']
        text.beep = self.dgttranslate.bl(BeepLevel.BUTTON)
        return text

    def _get_current_fav_engine_name(self):
        text = self.installed_fav_engines[self.menu_fav_engine_index]['text']
        text.beep = self.dgttranslate.bl(BeepLevel.BUTTON)
        return text

    def get_current_engine_name(self):
        """Get current engine name."""
        text = self.installed_engines[self.menu_engine_index]['text']
        text.beep = self.dgttranslate.bl(BeepLevel.BUTTON)
        return text

    def enter_eng_modern_name_menu(self):
        """Set the menu state."""
        self.state = MenuState.ENG_MODERN_NAME
        return self._get_current_modern_engine_name()

    def enter_eng_retro_name_menu(self):
        """Set the menu state."""
        self.state = MenuState.ENG_RETRO_NAME
        return self._get_current_retro_engine_name()

    def enter_eng_fav_name_menu(self):
        """Set the menu state."""
        self.state = MenuState.ENG_FAV_NAME
        return self._get_current_fav_engine_name()

    def enter_modern_eng_name_level_menu(self):
        """Set the menu state."""
        self.state = MenuState.ENG_MODERN_NAME_LEVEL
        eng = self.installed_engines[self.menu_modern_engine_index]
        level_dict = eng['level_dict']
        if level_dict:
            if self.menu_modern_engine_level is None or len(level_dict) <= self.menu_modern_engine_level:
                self.menu_modern_engine_level = len(level_dict) - 1
            msg = sorted(level_dict)[self.menu_modern_engine_level]
            text = self.dgttranslate.text('B00_level', msg)
        else:
            self.res_engine_index = self.menu_modern_engine_index
            self.res_engine_level = self.menu_modern_engine_level
            text = self.save_choices()
        return text

    def enter_retro_eng_name_level_menu(self):
        """Set the menu state."""
        self.state = MenuState.ENG_RETRO_NAME_LEVEL
        retro_eng = self.installed_retro_engines[self.menu_retro_engine_index]
        retro_level_dict = retro_eng['level_dict']
        if retro_level_dict:
            if self.menu_retro_engine_level is None or len(retro_level_dict) <= self.menu_retro_engine_level:
                self.menu_retro_engine_level = len(retro_level_dict) - 1
            msg = sorted(retro_level_dict)[self.menu_retro_engine_level]
            text = self.dgttranslate.text('B00_level', msg)
        else:
            self.res_engine_index = self.menu_engine_index = len(self.installed_modern_engines) + self.menu_retro_engine_index
            self.res_engine_level = self.menu_retro_engine_level
            text = self.save_choices()
        return text

    def enter_fav_eng_name_level_menu(self):
        """Set the menu state."""
        self.state = MenuState.ENG_FAV_NAME_LEVEL
        fav_eng = self.installed_fav_engines[self.menu_fav_engine_index]
        fav_level_dict = fav_eng['level_dict']
        if fav_level_dict:
            if self.menu_fav_engine_level is None or len(fav_level_dict) <= self.menu_fav_engine_level:
                self.menu_fav_engine_level = len(fav_level_dict) - 1
            msg = sorted(fav_level_dict)[self.menu_fav_engine_level]
            text = self.dgttranslate.text('B00_level', msg)
        else:
            self.res_engine_index = self.menu_engine_index
            self.res_engine_level = self.menu_engine_level
            text = self.save_choices()
        return text

    def enter_engine_menu(self):
        self.state = MenuState.ENGINE
        return self.dgttranslate.text(Top.ENGINE.value)

    def enter_sys_menu(self):
        """Set the menu state."""
        self.state = MenuState.SYS
        text = self.dgttranslate.text(Top.SYSTEM.value)
        return text

    def enter_sys_info_menu(self):
        """Set the menu state."""
        self.state = MenuState.SYS_INFO
        text = self.dgttranslate.text(self.menu_system.value)
        return text

    def enter_sys_info_vers_menu(self):
        """Set the menu state."""
        self.state = MenuState.SYS_INFO_VERS
        text = self.dgttranslate.text(self.menu_system_info.value)
        return text

    def enter_sys_info_ip_menu(self):
        """Set the menu state."""
        self.state = MenuState.SYS_INFO_IP
        text = self.dgttranslate.text(self.menu_system_info.value)
        return text

    def enter_sys_info_battery_menu(self):
        """Set the menu state."""
        self.state = MenuState.SYS_INFO_BATTERY
        text = self.dgttranslate.text(self.menu_system_info.value)
        return text

    def enter_sys_sound_menu(self):
        """Set the menu state."""
        self.state = MenuState.SYS_SOUND
        text = self.dgttranslate.text(self.menu_system.value)
        return text

    def enter_sys_sound_beep_menu(self):
        """Set the menu state."""
        self.state = MenuState.SYS_SOUND_BEEP
        text = self.dgttranslate.text(self.menu_system_sound.value)
        return text

    def enter_sys_lang_menu(self):
        """Set the menu state."""
        self.state = MenuState.SYS_LANG
        text = self.dgttranslate.text(self.menu_system.value)
        return text

    def enter_sys_lang_name_menu(self):
        """Set the menu state."""
        self.state = MenuState.SYS_LANG_NAME
        text = self.dgttranslate.text(self.menu_system_language.value)
        return text

    def enter_sys_log_menu(self):
        """Set the menu state."""
        self.state = MenuState.SYS_LOG
        text = self.dgttranslate.text(self.menu_system.value)
        return text

    def enter_sys_voice_menu(self):
        """Set the menu state."""
        self.state = MenuState.SYS_VOICE
        text = self.dgttranslate.text(self.menu_system.value)
        return text

    def enter_sys_voice_user_menu(self):
        """Set the menu state."""
        self.state = MenuState.SYS_VOICE_USER
        text = self.dgttranslate.text(Voice.USER.value)
        return text

    def enter_sys_voice_user_mute_menu(self):
        """Set the menu state."""
        self.state = MenuState.SYS_VOICE_USER_MUTE
        msg = 'on' if self.menu_system_voice_user_active else 'off'
        text = self.dgttranslate.text('B00_voice_' + msg)
        return text

    def enter_sys_voice_user_mute_lang_menu(self):
        """Set the menu state."""
        self.state = MenuState.SYS_VOICE_USER_MUTE_LANG
        vkey = self.voices_conf.keys()[self.menu_system_voice_user_lang]
        text = self.dgttranslate.text('B00_language_' + vkey + '_menu')
        return text

    def enter_sys_voice_comp_menu(self):
        """Set the menu state."""
        self.state = MenuState.SYS_VOICE_COMP
        text = self.dgttranslate.text(Voice.COMP.value)
        return text

    def enter_sys_voice_comp_mute_menu(self):
        """Set the menu state."""
        self.state = MenuState.SYS_VOICE_COMP_MUTE
        msg = 'on' if self.menu_system_voice_comp_active else 'off'
        text = self.dgttranslate.text('B00_voice_' + msg)
        return text

    def enter_sys_voice_comp_mute_lang_menu(self):
        """Set the menu state."""
        self.state = MenuState.SYS_VOICE_COMP_MUTE_LANG
        vkey = self.voices_conf.keys()[self.menu_system_voice_comp_lang]
        text = self.dgttranslate.text('B00_language_' + vkey + '_menu')
        return text

    def _get_current_speaker(self, speakers, index: int):
        speaker = speakers[list(speakers)[index]]
        text = Dgt.DISPLAY_TEXT(large_text=speaker['large'], medium_text=speaker['medium'], small_text=speaker['small'])
        text.beep = self.dgttranslate.bl(BeepLevel.BUTTON)
        text.wait = False
        text.maxtime = 0
        text.devs = {'ser', 'i2c', 'web'}
        return text

    def enter_sys_voice_user_mute_lang_speak_menu(self):
        """Set the menu state."""
        self.state = MenuState.SYS_VOICE_USER_MUTE_LANG_SPEAK
        vkey = self.voices_conf.keys()[self.menu_system_voice_user_lang]
        self.menu_system_voice_user_speak %= len(self.voices_conf[vkey])  # in case: change from higher=>lower speakerNo
        return self._get_current_speaker(self.voices_conf[vkey], self.menu_system_voice_user_speak)

    def enter_sys_voice_comp_mute_lang_speak_menu(self):
        """Set the menu state."""
        self.state = MenuState.SYS_VOICE_COMP_MUTE_LANG_SPEAK
        vkey = self.voices_conf.keys()[self.menu_system_voice_comp_lang]
        self.menu_system_voice_comp_speak %= len(self.voices_conf[vkey])  # in case: change from higher=>lower speakerNo
        return self._get_current_speaker(self.voices_conf[vkey], self.menu_system_voice_comp_speak)

    def enter_sys_voice_speed_menu(self):
        """Set the menu state."""
        self.state = MenuState.SYS_VOICE_SPEED
        text = self.dgttranslate.text(Voice.SPEED.value)
        return text

    def enter_sys_voice_speed_factor_menu(self):
        """Set the menu state."""
        self.state = MenuState.SYS_VOICE_SPEED_FACTOR
        text = self.dgttranslate.text('B00_voice_speed', str(self.menu_system_voice_speedfactor))
        return text

    def enter_sys_voice_volume_menu(self):
        """Set the menu state."""
        self.state = MenuState.SYS_VOICE_VOLUME
        text = self.dgttranslate.text(Voice.VOLUME.value)
        return text

    def enter_sys_voice_volume_factor_menu(self):
        """Set the menu state."""
        self.state = MenuState.SYS_VOICE_VOLUME_FACTOR
        text = self.dgttranslate.text('B00_voice_volume', str(self.menu_system_voice_volumefactor))
        return text

    def set_volume_voice(self, volume_factor):
        """ Set the Volume-Voice."""
        logging.debug('amixer sset Headphone ' + str(volume_factor * 5 + 50) + '%')
        os.system('amixer sset Headphone ' + str(volume_factor * 5 + 50) + '%')  # PulseAudio Fix for DGTPi -RR
        return

    def enter_sys_disp_menu(self):
        """Set the menu state."""
        self.state = MenuState.SYS_DISP
        text = self.dgttranslate.text(self.menu_system.value)
        return text

    def enter_sys_disp_confirm_menu(self):
        """Set the menu state."""
        self.state = MenuState.SYS_DISP_CONFIRM
        text = self.dgttranslate.text(Display.CONFIRM.value)
        return text

    def enter_sys_disp_confirm_yesno_menu(self):
        """Set the menu state."""
        self.state = MenuState.SYS_DISP_CONFIRM_YESNO
        msg = 'off' if self.menu_system_display_confirm else 'on'
        text = self.dgttranslate.text('B00_confirm_' + msg)
        return text

    def enter_sys_disp_enginename_menu(self):
        """Set the menu state."""
        self.state = MenuState.SYS_DISP_ENGINENAME
        text = self.dgttranslate.text(Display.ENGINENAME.value)
        return text

    def enter_sys_disp_enginename_yesno_menu(self):
        """Set the menu state."""
        self.state = MenuState.SYS_DISP_ENGINENAME_YESNO
        msg = 'on' if self.menu_system_display_enginename else 'off'
        text = self.dgttranslate.text('B00_enginename_' + msg)
        return text

    def enter_sys_disp_ponder_menu(self):
        """Set the menu state."""
        self.state = MenuState.SYS_DISP_PONDER
        text = self.dgttranslate.text(Display.PONDER.value)
        return text

    def enter_sys_disp_ponder_interval_menu(self):
        """Set the menu state."""
        self.state = MenuState.SYS_DISP_PONDER_INTERVAL
        text = self.dgttranslate.text('B00_ponder_interval', str(self.menu_system_display_ponderinterval))
        return text

    def enter_sys_disp_capital_menu(self):
        """Set the menu state."""
        self.state = MenuState.SYS_DISP_CAPITAL
        text = self.dgttranslate.text(Display.CAPITAL.value)
        return text

    def enter_sys_disp_capital_yesno_menu(self):
        """Set the menu state."""
        self.state = MenuState.SYS_DISP_CAPTIAL_YESNO
        msg = 'on' if self.menu_system_display_capital else 'off'
        text = self.dgttranslate.text('B00_capital_' + msg)
        return text

    def enter_sys_disp_notation_menu(self):
        """Set the menu state."""
        self.state = MenuState.SYS_DISP_NOTATION
        text = self.dgttranslate.text(Display.NOTATION.value)
        return text

    def enter_sys_disp_notation_move_menu(self):
        """Set the menu state."""
        self.state = MenuState.SYS_DISP_NOTATION_MOVE
        msg = 'long' if self.menu_system_display_notation else 'short'
        text = self.dgttranslate.text('B00_notation_' + msg)
        return text

    def enter_sys_eboard_menu(self):
        """Set the menu state."""
        self.state = MenuState.SYS_EBOARD
        text = self.dgttranslate.text(self.menu_system.value)
        return text

    def enter_sys_eboard_type_menu(self):
        """Set the menu state."""
        self.state = MenuState.SYS_EBOARD_TYPE
        text = self.dgttranslate.text(self.menu_system_eboard_type.value)
        return text

    def _fire_event(self, event: Event):
        Observable.fire(event)
        return self.save_choices()

    def _fire_dispatchdgt(self, text):
        DispatchDgt.fire(text)
        return self.save_choices()

    def _fire_timectrl(self, timectrl: TimeControl):
        time_text = self.dgttranslate.text('B10_oktime')
        event = Event.SET_TIME_CONTROL(tc_init=timectrl.get_parameters(), time_text=time_text, show_ok=True)
        return self._fire_event(event)

    def exit_menu(self):
        """Exit the menu."""
        if self.inside_main_menu():
            self.enter_top_menu()
            if not self.get_confirm():
                return True
        return False

    def main_up(self):
        """Change the menu state after UP action == LEFT arrow button in web interface."""
        text = self.dgttranslate.text('Y00_errormenu')
        if False:  # switch-case
            pass
        elif self.state == MenuState.TOP:
            pass
        elif self.state == MenuState.MODE:
            text = self.enter_top_menu()

        elif self.state == MenuState.MODE_TYPE:
            text = self.enter_mode_menu()

        elif self.state == MenuState.POS:
            text = self.enter_top_menu()

        elif self.state == MenuState.POS_COL:
            text = self.enter_pos_menu()

        elif self.state == MenuState.POS_REV:
            text = self.enter_pos_color_menu()

        elif self.state == MenuState.POS_UCI:
            text = self.enter_pos_rev_menu()

        elif self.state == MenuState.POS_READ:
            text = self.enter_pos_uci_menu()

        elif self.state == MenuState.TIME:
            text = self.enter_top_menu()

        elif self.state == MenuState.TIME_BLITZ:
            text = self.enter_time_menu()

        elif self.state == MenuState.TIME_BLITZ_CTRL:
            text = self.enter_time_blitz_menu()

        elif self.state == MenuState.TIME_FISCH:
            text = self.enter_time_menu()

        elif self.state == MenuState.TIME_FISCH_CTRL:
            text = self.enter_time_fisch_menu()

        elif self.state == MenuState.TIME_FIXED:
            text = self.enter_time_menu()

        elif self.state == MenuState.TIME_FIXED_CTRL:
            text = self.enter_time_fixed_menu()

        elif self.state == MenuState.TIME_TOURN:
            text = self.enter_time_menu()

        elif self.state == MenuState.TIME_TOURN_CTRL:
            text = self.enter_time_tourn_menu()

        elif self.state == MenuState.TIME_DEPTH:
            text = self.enter_time_menu()

        elif self.state == MenuState.TIME_DEPTH_CTRL:
            text = self.enter_time_depth_menu()

        elif self.state == MenuState.BOOK:
            text = self.enter_top_menu()

        elif self.state == MenuState.BOOK_NAME:
            text = self.enter_book_menu()

        elif self.state == MenuState.ENGINE:
            text = self.enter_top_menu()

        elif self.state == MenuState.ENG_MODERN:
            text = self.enter_engine_menu()

        elif self.state == MenuState.ENG_MODERN_NAME:
            text = self.enter_modern_eng_menu()

        elif self.state == MenuState.ENG_MODERN_NAME_LEVEL:
            text = self.enter_eng_modern_name_menu()

        elif self.state == MenuState.ENG_RETRO:
            text = self.enter_engine_menu()

        elif self.state == MenuState.ENG_RETRO_NAME:
            text = self.enter_retro_eng_menu()

        elif self.state == MenuState.ENG_RETRO_NAME_LEVEL:
            text = self.enter_eng_retro_name_menu()

        elif self.state == MenuState.ENG_FAV:
            text = self.enter_engine_menu()

        elif self.state == MenuState.ENG_FAV_NAME:
            text = self.enter_fav_eng_menu()

        elif self.state == MenuState.ENG_FAV_NAME_LEVEL:
            text = self.enter_eng_fav_name_menu()

        elif self.state == MenuState.SYS:
            text = self.enter_top_menu()

        elif self.state == MenuState.SYS_INFO:
            text = self.enter_sys_menu()

        elif self.state == MenuState.SYS_INFO_VERS:
            text = self.enter_sys_info_menu()

        elif self.state == MenuState.SYS_INFO_IP:
            text = self.enter_sys_info_menu()

        elif self.state == MenuState.SYS_INFO_BATTERY:
            text = self.enter_sys_info_menu()

        elif self.state == MenuState.SYS_SOUND:
            text = self.enter_sys_menu()

        elif self.state == MenuState.SYS_SOUND_BEEP:
            text = self.enter_sys_sound_menu()

        elif self.state == MenuState.SYS_LANG:
            text = self.enter_sys_menu()

        elif self.state == MenuState.SYS_LANG_NAME:
            text = self.enter_sys_lang_menu()

        elif self.state == MenuState.SYS_LOG:
            text = self.enter_sys_menu()

        elif self.state == MenuState.SYS_VOICE:
            text = self.enter_sys_menu()

        elif self.state == MenuState.SYS_VOICE_USER:
            text = self.enter_sys_voice_menu()

        elif self.state == MenuState.SYS_VOICE_USER_MUTE:
            text = self.enter_sys_voice_user_menu()

        elif self.state == MenuState.SYS_VOICE_USER_MUTE_LANG:
            text = self.enter_sys_voice_user_mute_menu()

        elif self.state == MenuState.SYS_VOICE_USER_MUTE_LANG_SPEAK:
            text = self.enter_sys_voice_user_mute_lang_menu()

        elif self.state == MenuState.SYS_VOICE_COMP:
            text = self.enter_sys_voice_menu()

        elif self.state == MenuState.SYS_VOICE_COMP_MUTE:
            text = self.enter_sys_voice_comp_menu()

        elif self.state == MenuState.SYS_VOICE_COMP_MUTE_LANG:
            text = self.enter_sys_voice_comp_mute_menu()

        elif self.state == MenuState.SYS_VOICE_COMP_MUTE_LANG_SPEAK:
            text = self.enter_sys_voice_comp_mute_lang_menu()

        elif self.state == MenuState.SYS_VOICE_SPEED:
            text = self.enter_sys_voice_menu()

        elif self.state == MenuState.SYS_VOICE_SPEED_FACTOR:
            text = self.enter_sys_voice_speed_menu()

        elif self.state == MenuState.SYS_VOICE_VOLUME:
            text = self.enter_sys_voice_menu()

        elif self.state == MenuState.SYS_VOICE_VOLUME_FACTOR:
            text = self.enter_sys_voice_volume_menu()

        elif self.state == MenuState.SYS_DISP:
            text = self.enter_sys_menu()

        elif self.state == MenuState.SYS_DISP_CONFIRM:
            text = self.enter_sys_disp_menu()

        elif self.state == MenuState.SYS_DISP_CONFIRM_YESNO:
            text = self.enter_sys_disp_confirm_menu()

        elif self.state == MenuState.SYS_DISP_ENGINENAME:
            text = self.enter_sys_disp_menu()

        elif self.state == MenuState.SYS_DISP_ENGINENAME_YESNO:
            text = self.enter_sys_disp_enginename_menu()

        elif self.state == MenuState.SYS_DISP_PONDER:
            text = self.enter_sys_disp_menu()

        elif self.state == MenuState.SYS_DISP_PONDER_INTERVAL:
            text = self.enter_sys_disp_ponder_menu()

        elif self.state == MenuState.SYS_DISP_CAPITAL:
            text = self.enter_sys_disp_menu()

        elif self.state == MenuState.SYS_DISP_CAPTIAL_YESNO:
            text = self.enter_sys_disp_capital_menu()

        elif self.state == MenuState.SYS_DISP_NOTATION:
            text = self.enter_sys_disp_menu()

        elif self.state == MenuState.SYS_DISP_NOTATION_MOVE:
            text = self.enter_sys_disp_notation_menu()

        elif self.state == MenuState.SYS_EBOARD:
            text = self.enter_sys_menu()

        elif self.state == MenuState.SYS_EBOARD_TYPE:
            text = self.enter_sys_eboard_menu()

        elif self.state == MenuState.PICOTUTOR:
            text = self.enter_top_menu()

        elif self.state == MenuState.PICOTUTOR_PICOWATCHER:
            text = self.enter_picotutor_menu()

        elif self.state == MenuState.PICOTUTOR_PICOWATCHER_ONOFF:
            text = self.enter_picotutor_picowatcher_menu()

        elif self.state == MenuState.PICOTUTOR_PICOCOACH:
            text = self.enter_picotutor_menu()

        elif self.state == MenuState.PICOTUTOR_PICOCOACH_ONOFF:
            text = self.enter_picotutor_picocoach_menu()

        elif self.state == MenuState.PICOTUTOR_PICOEXPLORER:
            text = self.enter_picotutor_menu()

        elif self.state == MenuState.PICOTUTOR_PICOEXPLORER_ONOFF:
            text = self.enter_picotutor_picoexplorer_menu()

        elif self.state == MenuState.PICOTUTOR_PICOCOMMENT:
            text = self.enter_picotutor_menu()

        elif self.state == MenuState.PICOTUTOR_PICOCOMMENT_OFF:
            text = self.enter_picotutor_picocomment_menu()

        elif self.state == MenuState.PICOTUTOR_PICOCOMMENT_ON_ENG:
            text = self.enter_picotutor_picocomment_menu()

        elif self.state == MenuState.PICOTUTOR_PICOCOMMENT_ON_ALL:
            text = self.enter_picotutor_picocomment_menu()

        elif self.state == MenuState.GAME:
            text = self.enter_top_menu()

        elif self.state == MenuState.GAME_GAMESAVE:
            text = self.enter_game_menu()

        elif self.state == MenuState.GAME_GAMESAVE_GAME1:
            text = self.enter_game_gamesave_menu()

        elif self.state == MenuState.GAME_GAMESAVE_GAME2:
            text = self.enter_game_gamesave_menu()

        elif self.state == MenuState.GAME_GAMESAVE_GAME3:
            text = self.enter_game_gamesave_menu()

        elif self.state == MenuState.GAME_GAMEREAD:
            text = self.enter_game_menu()

        elif self.state == MenuState.GAME_GAMEREAD_GAMELAST:
            text = self.enter_game_gameread_menu()

        elif self.state == MenuState.GAME_GAMEREAD_GAME1:
            text = self.enter_game_gameread_menu()

        elif self.state == MenuState.GAME_GAMEREAD_GAME2:
            text = self.enter_game_gameread_menu()

        elif self.state == MenuState.GAME_GAMEREAD_GAME3:
            text = self.enter_game_gameread_menu()

        elif self.state == MenuState.GAME_GAMEALTMOVE:
            text = self.enter_game_menu()

        elif self.state == MenuState.GAME_GAMEALTMOVE_ONOFF:
            text = self.enter_game_altmove_menu()

        elif self.state == MenuState.GAME_GAMECONTLAST:
            text = self.enter_game_menu()

        elif self.state == MenuState.GAME_GAMECONTLAST_ONOFF:
            text = self.enter_game_contlast_menu()

        else:  # Default
            pass
        self.current_text = text
        return text

    def main_down(self):
        """Change the menu state after DOWN action == RIGHT arrow button in web interface."""
        text = self.dgttranslate.text('Y00_errormenu')
        if False:  # switch-case
            pass
        elif self.state == MenuState.TOP:
            if self.menu_top == Top.MODE:
                text = self.enter_mode_menu()
            if self.menu_top == Top.POSITION:
                text = self.enter_pos_menu()
            if self.menu_top == Top.TIME:
                text = self.enter_time_menu()
            if self.menu_top == Top.BOOK:
                text = self.enter_book_menu()
            if self.menu_top == Top.ENGINE:
                text = self.enter_engine_menu()
            if self.menu_top == Top.SYSTEM:
                text = self.enter_sys_menu()
            if self.menu_top == Top.PICOTUTOR:
                text = self.enter_picotutor_menu()
            if self.menu_top == Top.GAME:
                text = self.enter_game_menu()

        elif self.state == MenuState.MODE:
            text = self.enter_mode_type_menu()

        elif self.state == MenuState.MODE_TYPE:
            # maybe do action!
            if self.menu_mode == Mode.BRAIN and not self.get_engine_has_ponder():
                DispatchDgt.fire(self.dgttranslate.text('Y10_erroreng'))
                text = Dgt.DISPLAY_TIME(force=True, wait=True, devs={'ser', 'i2c', 'web'})
            else:
                mode_text = self.dgttranslate.text('B10_okmode')
                event = Event.SET_INTERACTION_MODE(mode=self.menu_mode, mode_text=mode_text, show_ok=True)
                text = self._fire_event(event)

        elif self.state == MenuState.GAME:
            if self.menu_game == Game.SAVE:
                text = self.enter_game_gamesave_menu()
            if self.menu_game == Game.READ:
                text = self.enter_game_gameread_menu()
            if self.menu_game == Game.ALTMOVE:
                text = self.enter_game_altmove_menu()
            if self.menu_game == Game.CONTLAST:
                text = self.enter_game_contlast_menu()

        elif self.state == MenuState.GAME_GAMESAVE:
            if self.menu_game_save == GameSave.GAME1:
                text = self.enter_game_gamesave_game1_menu()
            if self.menu_game_save == GameSave.GAME2:
                text = self.enter_game_gamesave_game2_menu()
            if self.menu_game_save == GameSave.GAME3:
                text = self.enter_game_gamesave_game3_menu()

        elif self.state == MenuState.GAME_GAMEREAD:
            if self.menu_game_read == GameRead.GAMELAST:
                text = self.enter_game_gameread_gamelast_menu()
            if self.menu_game_read == GameRead.GAME1:
                text = self.enter_game_gameread_game1_menu()
            if self.menu_game_read == GameRead.GAME2:
                text = self.enter_game_gameread_game2_menu()
            if self.menu_game_read == GameRead.GAME3:
                text = self.enter_game_gameread_game3_menu()

        elif self.state == MenuState.GAME_GAMEALTMOVE:
            text = self.enter_game_altmove_onoff_menu()

        elif self.state == MenuState.GAME_GAMEALTMOVE_ONOFF:
            # do action!
            config = ConfigObj('picochess.ini')
            if self.menu_game_altmove:
                config['alt-move'] = self.menu_game_altmove
            elif 'alt-move' in config:
                del config['alt-move']
            config.write()
            self.res_game_altmove = self.menu_game_altmove
            event = Event.ALTMOVES(altmoves=self.menu_game_altmove)
            Observable.fire(event)
            text = self._fire_dispatchdgt(self.dgttranslate.text('B10_okaltmove'))

        elif self.state == MenuState.GAME_GAMECONTLAST:
            text = self.enter_game_contlast_onoff_menu()

        elif self.state == MenuState.GAME_GAMECONTLAST_ONOFF:
            # do action!
            config = ConfigObj('picochess.ini')
            if self.menu_game_contlast:
                config['continue-game'] = self.menu_game_contlast
            elif 'continue-game' in config:
                del config['continue-game']
            config.write()
            self.res_game_contlast = self.menu_game_contlast
            event = Event.CONTLAST(contlast=self.menu_game_contlast)
            Observable.fire(event)
            text = self._fire_dispatchdgt(self.dgttranslate.text('B10_okcontlast'))

        elif self.state == MenuState.GAME_GAMESAVE_GAME1:
            # do action!
            # raise SAVE_PGN_EVENT
            event = Event.SAVE_GAME(pgn_filename='picochess_game_1.pgn')
            Observable.fire(event)
            text = self._fire_dispatchdgt(self.dgttranslate.text('B10_oksavegame'))

        elif self.state == MenuState.GAME_GAMESAVE_GAME2:
            # raise SAVE_PGN_EVENT
            event = Event.SAVE_GAME(pgn_filename='picochess_game_2.pgn')
            Observable.fire(event)
            text = self._fire_dispatchdgt(self.dgttranslate.text('B10_oksavegame'))

        elif self.state == MenuState.GAME_GAMESAVE_GAME3:
            # raise SAVE_PGN_EVENT
            event = Event.SAVE_GAME(pgn_filename='picochess_game_3.pgn')
            Observable.fire(event)
            text = self._fire_dispatchdgt(self.dgttranslate.text('B10_oksavegame'))

        elif self.state == MenuState.GAME_GAMEREAD_GAMELAST:
            event = Event.READ_GAME(pgn_filename='last_game.pgn')
            Observable.fire(event)
            text = self._fire_dispatchdgt(self.dgttranslate.text('B10_okreadgame'))

        elif self.state == MenuState.GAME_GAMEREAD_GAME1:
            event = Event.READ_GAME(pgn_filename='picochess_game_1.pgn')
            Observable.fire(event)
            text = self._fire_dispatchdgt(self.dgttranslate.text('B10_okreadgame'))

        elif self.state == MenuState.GAME_GAMEREAD_GAME2:
            event = Event.READ_GAME(pgn_filename='picochess_game_2.pgn')
            Observable.fire(event)
            text = self._fire_dispatchdgt(self.dgttranslate.text('B10_okreadgame'))

        elif self.state == MenuState.GAME_GAMEREAD_GAME3:
            event = Event.READ_GAME(pgn_filename='picochess_game_3.pgn')
            Observable.fire(event)
            text = self._fire_dispatchdgt(self.dgttranslate.text('B10_okreadgame'))

        elif self.state == MenuState.PICOTUTOR:
            if self.menu_picotutor == PicoTutor.WATCHER:
                text = self.enter_picotutor_picowatcher_menu()
            if self.menu_picotutor == PicoTutor.COACH:
                text = self.enter_picotutor_picocoach_menu()
            if self.menu_picotutor == PicoTutor.EXPLORER:
                text = self.enter_picotutor_picoexplorer_menu()
            if self.menu_picotutor == PicoTutor.COMMENT:
                text = self.enter_picotutor_picocomment_menu()

        elif self.state == MenuState.PICOTUTOR_PICOWATCHER:
            text = self.enter_picotutor_picowatcher_onoff_menu()

        elif self.state == MenuState.PICOTUTOR_PICOWATCHER_ONOFF:
            # do action!
            config = ConfigObj('picochess.ini')
            if self.menu_picotutor_picowatcher:
                config['tutor-watcher'] = self.menu_picotutor_picowatcher
            elif 'tutor-watcher' in config:
                del config['tutor-watcher']
            config.write()
            self.res_picotutor_picowatcher = self.menu_picotutor_picowatcher
            event = Event.PICOWATCHER(picowatcher=self.menu_picotutor_picowatcher)
            Observable.fire(event)
            text = self._fire_dispatchdgt(self.dgttranslate.text('B10_okpicowatcher'))

        elif self.state == MenuState.PICOTUTOR_PICOCOACH:
            text = self.enter_picotutor_picocoach_onoff_menu()

        elif self.state == MenuState.PICOTUTOR_PICOCOACH_ONOFF:
            # do action!
            config = ConfigObj('picochess.ini')
            if self.menu_picotutor_picocoach:
                config['tutor-coach'] = self.menu_picotutor_picocoach
            elif 'tutor-coach' in config:
                del config['tutor-coach']
            config.write()
            self.res_picotutor_picocoach = self.menu_picotutor_picocoach
            event = Event.PICOCOACH(picocoach=self.menu_picotutor_picocoach)
            Observable.fire(event)
            text = self._fire_dispatchdgt(self.dgttranslate.text('B10_okpicocoach'))

        elif self.state == MenuState.PICOTUTOR_PICOEXPLORER:
            text = self.enter_picotutor_picoexplorer_onoff_menu()

        elif self.state == MenuState.PICOTUTOR_PICOEXPLORER_ONOFF:
            # do action!
            config = ConfigObj('picochess.ini')
            if self.menu_picotutor_picoexplorer:
                config['tutor-explorer'] = self.menu_picotutor_picoexplorer
            elif 'tutor-explorer' in config:
                del config['tutor-explorer']
            config.write()
            self.res_picotutor_picoexplorer = self.menu_picotutor_picoexplorer
            event = Event.PICOEXPLORER(picoexplorer=self.menu_picotutor_picoexplorer)
            Observable.fire(event)
            text = self._fire_dispatchdgt(self.dgttranslate.text('B10_okpicoexplorer'))

        elif self.state == MenuState.PICOTUTOR_PICOCOMMENT:
            if self.menu_picotutor_picocomment == PicoComment.COM_OFF:
                text = self.enter_picotutor_picocomment_off_menu()
            if self.menu_picotutor_picocomment == PicoComment.COM_ON_ENG:
                text = self.enter_picotutor_picocomment_on_eng_menu()
            if self.menu_picotutor_picocomment == PicoComment.COM_ON_ALL:
                text = self.enter_picotutor_picocomment_on_all_menu()

        elif self.state == MenuState.PICOTUTOR_PICOCOMMENT_OFF:
            # do action!
            config = ConfigObj('picochess.ini')
            config['tutor-comment'] = 'off'

            config.write()
            self.res_picotutor_picocomment = PicoComment.COM_OFF
            self.menu_picotutor_picocomment = PicoComment.COM_OFF
            event = Event.PICOCOMMENT(picocomment=self.menu_picotutor_picocomment)
            Observable.fire(event)
            text = self._fire_dispatchdgt(self.dgttranslate.text('B10_okpicocomment'))

        elif self.state == MenuState.PICOTUTOR_PICOCOMMENT_ON_ENG:
            # do action!
            config = ConfigObj('picochess.ini')
            config['tutor-comment'] = 'single'

            config.write()
            self.res_picotutor_picocomment = PicoComment.COM_ON_ENG
            self.menu_picotutor_picocomment = PicoComment.COM_ON_ENG
            event = Event.PICOCOMMENT(picocomment=self.menu_picotutor_picocomment)
            Observable.fire(event)
            text = self._fire_dispatchdgt(self.dgttranslate.text('B10_okpicocomment'))

        elif self.state == MenuState.PICOTUTOR_PICOCOMMENT_ON_ALL:
            # do action!
            config = ConfigObj('picochess.ini')
            config['tutor-comment'] = 'all'

            config.write()
            self.menu_picotutor_picocomment = PicoComment.COM_ON_ALL
            self.res_picotutor_picocomment = PicoComment.COM_ON_ALL
            event = Event.PICOCOMMENT(picocomment=self.menu_picotutor_picocomment)
            Observable.fire(event)
            text = self._fire_dispatchdgt(self.dgttranslate.text('B10_okpicocomment'))

        elif self.state == MenuState.POS:
            text = self.enter_pos_color_menu()

        elif self.state == MenuState.POS_COL:
            text = self.enter_pos_rev_menu()

        elif self.state == MenuState.POS_REV:
            text = self.enter_pos_uci_menu()

        elif self.state == MenuState.POS_UCI:
            text = self.enter_pos_read_menu()

        elif self.state == MenuState.POS_READ:
            # do action!
            fen = self.dgt_fen
            if self.flip_board != self.menu_position_reverse:
                logging.debug('flipping the board - %s infront now', 'B' if self.menu_position_reverse else 'W')
                fen = fen[::-1]
            fen += ' {0} KQkq - 0 1'.format('w' if self.menu_position_whitetomove else 'b')
            # ask python-chess to correct the castling string
            bit_board = chess.Board(fen, self.menu_position_uci960)
            bit_board.set_fen(bit_board.fen())
            if bit_board.is_valid():
                self.flip_board = self.menu_position_reverse
                event = Event.SETUP_POSITION(fen=bit_board.fen(), uci960=self.menu_position_uci960)
                Observable.fire(event)
                # self._reset_moves_and_score() done in "START_NEW_GAME"
                text = self.save_choices()
            else:
                logging.debug('illegal fen %s', fen)
                DispatchDgt.fire(self.dgttranslate.text('Y10_illegalpos'))
                text = self.dgttranslate.text('B00_scanboard')
                text.wait = True

        elif self.state == MenuState.TIME:
            if self.menu_time_mode == TimeMode.BLITZ:
                text = self.enter_time_blitz_menu()
            if self.menu_time_mode == TimeMode.FISCHER:
                text = self.enter_time_fisch_menu()
            if self.menu_time_mode == TimeMode.FIXED:
                text = self.enter_time_fixed_menu()
            if self.menu_time_mode == TimeMode.TOURN:
                text = self.enter_time_tourn_menu()
            if self.menu_time_mode == TimeMode.DEPTH:
                text = self.enter_time_depth_menu()

        elif self.state == MenuState.TIME_BLITZ:
            text = self.enter_time_blitz_ctrl_menu()

        elif self.state == MenuState.TIME_BLITZ_CTRL:
            # do action!
            text = self._fire_timectrl(self.tc_blitz_map[list(self.tc_blitz_map)[self.menu_time_blitz]])

        elif self.state == MenuState.TIME_FISCH:
            text = self.enter_time_fisch_ctrl_menu()

        elif self.state == MenuState.TIME_FISCH_CTRL:
            # do action!
            text = self._fire_timectrl(self.tc_fisch_map[list(self.tc_fisch_map)[self.menu_time_fisch]])

        elif self.state == MenuState.TIME_FIXED:
            text = self.enter_time_fixed_ctrl_menu()

        elif self.state == MenuState.TIME_FIXED_CTRL:
            # do action!
            text = self._fire_timectrl(self.tc_fixed_map[list(self.tc_fixed_map)[self.menu_time_fixed]])

        elif self.state == MenuState.TIME_TOURN:
            text = self.enter_time_tourn_ctrl_menu()

        elif self.state == MenuState.TIME_TOURN_CTRL:
            # do action!
            text = self._fire_timectrl(self.tc_tourn_map[list(self.tc_tourn_map)[self.menu_time_tourn]])

        elif self.state == MenuState.TIME_DEPTH:
            text = self.enter_time_depth_ctrl_menu()

        elif self.state == MenuState.TIME_DEPTH_CTRL:
            # do action!
            text = self._fire_timectrl(self.tc_depth_map[list(self.tc_depth_map)[self.menu_time_depth]])

        elif self.state == MenuState.BOOK:
            text = self.enter_book_name_menu()

        elif self.state == MenuState.BOOK_NAME:
            # do action!
            book_text = self.dgttranslate.text('B10_okbook')
            event = Event.SET_OPENING_BOOK(book=self.all_books[self.menu_book], book_text=book_text, show_ok=True)
            text = self._fire_event(event)

        elif self.state == MenuState.ENG_MODERN:
            text = self.enter_eng_modern_name_menu()

        elif self.state == MenuState.ENG_MODERN_NAME:
            # maybe do action!
            text = self.enter_modern_eng_name_level_menu()
            if not text:
                eng = self.installed_modern_engines[self.menu_modern_engine_index]
                if 'Online' not in str(eng['name']) and 'Remote' not in str(eng['name']) and 'FICS' not in str(eng['name']) and 'lichess' not in str(eng['name']) and 'PGN' not in str(eng['name']):
                    write_picochess_ini('engine-level', None)
                eng_text = self.dgttranslate.text('B10_okengine')
                event = Event.NEW_ENGINE(eng=eng, eng_text=eng_text, options={}, show_ok=True)
                Observable.fire(event)
                self.engine_restart = True

        elif self.state == MenuState.ENG_MODERN_NAME_LEVEL:
            # do action!
            eng = self.installed_modern_engines[self.menu_modern_engine_index]
            logging.debug('installed engines in level: %s', str(eng))

            level_dict = eng['level_dict']
            if level_dict:
                msg = sorted(level_dict)[self.menu_modern_engine_level]
                options = level_dict[msg]
                if 'Online' not in str(eng['name']) and 'Remote' not in str(eng['name']) and 'FICS' not in str(eng['name']) and 'lichess' not in str(eng['name']) and 'PGN' not in str(eng['name']):
                    write_picochess_ini('engine-level', msg)

                event = Event.LEVEL(options={}, level_text=self.dgttranslate.text('B10_level', msg), level_name=msg)
                Observable.fire(event)
            else:
                options = {}
            eng_text = self.dgttranslate.text('B10_okengine')
            event = Event.NEW_ENGINE(eng=eng, eng_text=eng_text, options=options, show_ok=True)
            text = self._fire_event(event)
            self.engine_restart = True
            self.res_engine_index = self.menu_engine_index = self.menu_modern_engine_index
            self.res_engine_level = self.menu_modern_engine_level

        elif self.state == MenuState.ENG_RETRO:
            text = self.enter_eng_retro_name_menu()

        elif self.state == MenuState.ENG_RETRO_NAME:
            # maybe do action!
            text = self.enter_retro_eng_name_level_menu()
            if not text:
                retro_eng = self.installed_retro_engines[self.menu_retro_engine_index]
                if 'Online' not in str(retro_eng['name']) and 'Remote' not in str(retro_eng['name']) and 'FICS' not in str(retro_eng['name']) and 'lichess' not in str(retro_eng['name']) and 'PGN' not in str(retro_eng['name']):
                    write_picochess_ini('engine-level', None)
                eng_text = self.dgttranslate.text('B10_okengine')
                event = Event.NEW_ENGINE(eng=retro_eng, eng_text=eng_text, options={}, show_ok=True)
                Observable.fire(event)
                self.engine_restart = True

        elif self.state == MenuState.ENG_RETRO_NAME_LEVEL:
            # do action!
            retro_eng = self.installed_retro_engines[self.menu_retro_engine_index]
            retro_level_dict = retro_eng['level_dict']
            if retro_level_dict:
                msg = sorted(retro_level_dict)[self.menu_retro_engine_level]
                options = retro_level_dict[msg]
                if 'Online' not in str(retro_eng['name']) and 'Remote' not in str(retro_eng['name']) and 'FICS' not in str(retro_eng['name']) and 'lichess' not in str(retro_eng['name']) and 'PGN' not in str(retro_eng['name']):
                    write_picochess_ini('engine-level', msg)
                event = Event.LEVEL(options={}, level_text=self.dgttranslate.text('B10_level', msg), level_name=msg)
                Observable.fire(event)
            else:
                options = {}
            eng_text = self.dgttranslate.text('B10_okengine')
            event = Event.NEW_ENGINE(eng=retro_eng, eng_text=eng_text, options=options, show_ok=True)
            text = self._fire_event(event)
            self.engine_restart = True
            self.res_engine_index = self.menu_engine_index = len(self.installed_modern_engines) + self.menu_retro_engine_index
            self.res_engine_level = self.menu_retro_engine_level

        elif self.state == MenuState.ENG_FAV:
            text = self.enter_eng_fav_name_menu()

        elif self.state == MenuState.ENG_FAV_NAME:
            # maybe do action!
            text = self.enter_fav_eng_name_level_menu()
            if not text:
                retro_eng = self.installed_fav_engines[self.menu_fav_engine_index]
                if 'Online' not in str(retro_eng['name']) and 'Remote' not in str(retro_eng['name']) and 'FICS' not in str(retro_eng['name']) and 'lichess' not in str(retro_eng['name']) and 'PGN' not in str(retro_eng['name']):
                    write_picochess_ini('engine-level', None)
                eng_text = self.dgttranslate.text('B10_okengine')
                event = Event.NEW_ENGINE(eng=retro_eng, eng_text=eng_text, options={}, show_ok=True)
                Observable.fire(event)
                self.engine_restart = True

        elif self.state == MenuState.ENG_FAV_NAME_LEVEL:
            # do action!
            fav_eng = self.installed_fav_engines[self.menu_fav_engine_index]
            fav_level_dict = fav_eng['level_dict']
            if fav_level_dict:
                msg = sorted(fav_level_dict)[self.menu_fav_engine_level]
                options = fav_level_dict[msg]
                if 'Online' not in str(fav_eng['name']) and 'Remote' not in str(fav_eng['name']) and 'FICS' not in str(fav_eng['name']) and 'lichess' not in str(fav_eng['name']) and 'PGN' not in str(fav_eng['name']):
                    write_picochess_ini('engine-level', msg)
                event = Event.LEVEL(options={}, level_text=self.dgttranslate.text('B10_level', msg), level_name=msg)
                Observable.fire(event)
            else:
                options = {}
            eng_text = self.dgttranslate.text('B10_okengine')
            event = Event.NEW_ENGINE(eng=fav_eng, eng_text=eng_text, options=options, show_ok=True)
            text = self._fire_event(event)
            self.engine_restart = True

        elif self.state == MenuState.ENGINE:
            if self.menu_engine == EngineTop.MODERN_ENGINE:
                text = self.enter_modern_eng_menu()
            elif self.menu_engine == EngineTop.RETRO_ENGINE:
                text = self.enter_retro_eng_menu()
            elif self.menu_engine == EngineTop.FAV_ENGINE:
                text = self.enter_fav_eng_menu()

        elif self.state == MenuState.SYS:
            if self.menu_system == System.INFO:
                text = self.enter_sys_info_menu()
            elif self.menu_system == System.SOUND:
                text = self.enter_sys_sound_menu()
            elif self.menu_system == System.LANGUAGE:
                text = self.enter_sys_lang_menu()
            elif self.menu_system == System.LOGFILE:
                text = self.enter_sys_log_menu()
            elif self.menu_system == System.VOICE:
                text = self.enter_sys_voice_menu()
            elif self.menu_system == System.DISPLAY:
                text = self.enter_sys_disp_menu()
            elif self.menu_system == System.EBOARD:
                text = self.enter_sys_eboard_menu()

        elif self.state == MenuState.SYS_INFO:
            if self.menu_system_info == Info.VERSION:
                text = self.enter_sys_info_vers_menu()
            if self.menu_system_info == Info.IPADR:
                text = self.enter_sys_info_ip_menu()
            if self.menu_system_info == Info.BATTERY:
                text = self.enter_sys_info_battery_menu()

        elif self.state == MenuState.SYS_INFO_VERS:
            # do action!
            text = self.dgttranslate.text('B10_picochess')
            text.rd = ClockIcons.DOT
            text.wait = False
            text = self._fire_dispatchdgt(text)

        elif self.state == MenuState.SYS_INFO_IP:
            # do action!
            if self.int_ip:
                msg = ' '.join(self.int_ip.split('.')[:2])
                text = self.dgttranslate.text('B07_default', msg)
                if len(msg) == 7:  # delete the " " for XL incase its "123 456"
                    text.s = msg[:3] + msg[4:]
                DispatchDgt.fire(text)
                msg = ' '.join(self.int_ip.split('.')[2:])
                text = self.dgttranslate.text('N07_default', msg)
                if len(msg) == 7:  # delete the " " for XL incase its "123 456"
                    text.s = msg[:3] + msg[4:]
                text.wait = True
            else:
                text = self.dgttranslate.text('B10_noipadr')
            text = self._fire_dispatchdgt(text)

        elif self.state == MenuState.SYS_INFO_BATTERY:
            # do action!
            text = self._fire_dispatchdgt(self.dgttranslate.text('B10_bat_percent', self.battery))

        elif self.state == MenuState.SYS_SOUND:
            text = self.enter_sys_sound_beep_menu()

        elif self.state == MenuState.SYS_SOUND_BEEP:
            # do action!
            self.dgttranslate.set_beep(self.menu_system_sound)
            write_picochess_ini('beep-config', self.dgttranslate.beep_to_config(self.menu_system_sound))
            text = self._fire_dispatchdgt(self.dgttranslate.text('B10_okbeep'))

        elif self.state == MenuState.SYS_LANG:
            text = self.enter_sys_lang_name_menu()

        elif self.state == MenuState.SYS_LANG_NAME:
            # do action!
            langs = {Language.EN: 'en', Language.DE: 'de', Language.NL: 'nl',
                     Language.FR: 'fr', Language.ES: 'es', Language.IT: 'it'}
            language = langs[self.menu_system_language]
            self.dgttranslate.set_language(language)
            write_picochess_ini('language', language)
            text = self._fire_dispatchdgt(self.dgttranslate.text('B10_oklang'))

        elif self.state == MenuState.SYS_LOG:
            # do action!
            if self.log_file:
                Observable.fire(Event.EMAIL_LOG())
                text = self._fire_dispatchdgt(self.dgttranslate.text('B10_oklogfile'))
            else:
                text = self._fire_dispatchdgt(self.dgttranslate.text('B10_nofunction'))

        elif self.state == MenuState.SYS_VOICE:
            if self.menu_system_voice == Voice.USER:
                text = self.enter_sys_voice_user_menu()
            if self.menu_system_voice == Voice.COMP:
                text = self.enter_sys_voice_comp_menu()
            if self.menu_system_voice == Voice.SPEED:
                text = self.enter_sys_voice_speed_menu()
            if self.menu_system_voice == Voice.VOLUME:
                text = self.enter_sys_voice_volume_menu()

        elif self.state == MenuState.SYS_VOICE_USER:
            self.menu_system_voice = Voice.USER
            text = self.enter_sys_voice_user_mute_menu()

        elif self.state == MenuState.SYS_VOICE_COMP:
            self.menu_system_voice = Voice.COMP
            text = self.enter_sys_voice_comp_mute_menu()

        elif self.state == MenuState.SYS_VOICE_USER_MUTE:
            # maybe do action!
            if self.menu_system_voice_user_active:
                text = self.enter_sys_voice_user_mute_lang_menu()
            else:
                config = ConfigObj('picochess.ini')
                if 'user-voice' in config:
                    del config['user-voice']
                    config.write()
                event = Event.SET_VOICE(type=self.menu_system_voice, lang='en', speaker='mute', speed=2)
                Observable.fire(event)
                text = self._fire_dispatchdgt(self.dgttranslate.text('B10_okvoice'))

        elif self.state == MenuState.SYS_VOICE_USER_MUTE_LANG:
            text = self.enter_sys_voice_user_mute_lang_speak_menu()

        elif self.state == MenuState.SYS_VOICE_USER_MUTE_LANG_SPEAK:
            # do action!
            vkey = self.voices_conf.keys()[self.menu_system_voice_user_lang]
            speakers = self.voices_conf[vkey].keys()
            config = ConfigObj('picochess.ini')
            skey = speakers[self.menu_system_voice_user_speak]
            config['user-voice'] = vkey + ':' + skey
            config.write()
            event = Event.SET_VOICE(type=self.menu_system_voice, lang=vkey, speaker=skey,
                                    speed=self.menu_system_voice_speedfactor)
            Observable.fire(event)
            text = self._fire_dispatchdgt(self.dgttranslate.text('B10_okvoice'))

        elif self.state == MenuState.SYS_VOICE_COMP_MUTE:
            # maybe do action!
            if self.menu_system_voice_comp_active:
                text = self.enter_sys_voice_comp_mute_lang_menu()
            else:
                config = ConfigObj('picochess.ini')
                if 'computer-voice' in config:
                    del config['computer-voice']
                    config.write()
                event = Event.SET_VOICE(type=self.menu_system_voice, lang='en', speaker='mute', speed=2)
                Observable.fire(event)
                text = self._fire_dispatchdgt(self.dgttranslate.text('B10_okvoice'))

        elif self.state == MenuState.SYS_VOICE_COMP_MUTE_LANG:
            text = self.enter_sys_voice_comp_mute_lang_speak_menu()

        elif self.state == MenuState.SYS_VOICE_COMP_MUTE_LANG_SPEAK:
            # do action!
            vkey = self.voices_conf.keys()[self.menu_system_voice_comp_lang]
            speakers = self.voices_conf[vkey].keys()
            config = ConfigObj('picochess.ini')
            skey = speakers[self.menu_system_voice_comp_speak]
            config['computer-voice'] = vkey + ':' + skey
            config.write()
            event = Event.SET_VOICE(type=self.menu_system_voice, lang=vkey, speaker=skey,
                                    speed=self.menu_system_voice_speedfactor)
            Observable.fire(event)
            text = self._fire_dispatchdgt(self.dgttranslate.text('B10_okvoice'))

        elif self.state == MenuState.SYS_VOICE_SPEED:
            self.menu_system_voice = Voice.SPEED
            text = self.enter_sys_voice_speed_factor_menu()

        elif self.state == MenuState.SYS_VOICE_SPEED_FACTOR:
            # do action!
            assert self.menu_system_voice == Voice.SPEED, 'menu item is not Voice.SPEED: %s' % self.menu_system_voice
            write_picochess_ini('speed-voice', self.menu_system_voice_speedfactor)
            event = Event.SET_VOICE(type=self.menu_system_voice, lang='en', speaker='mute',  # lang & speaker ignored
                                    speed=self.menu_system_voice_speedfactor)
            Observable.fire(event)
            text = self._fire_dispatchdgt(self.dgttranslate.text('B10_okspeed'))

        elif self.state == MenuState.SYS_VOICE_VOLUME:
            self.menu_system_voice = Voice.VOLUME
            text = self.enter_sys_voice_volume_factor_menu()

        elif self.state == MenuState.SYS_VOICE_VOLUME_FACTOR:
            # do action!
            assert self.menu_system_voice == Voice.VOLUME, 'menu item is not Voice.VOLUME: %s' % self.menu_system_voice
            write_picochess_ini('volume-voice', str(self.menu_system_voice_volumefactor))
            text = self.set_volume_voice(self.menu_system_voice_volumefactor)
            event = Event.SET_VOICE(type=self.menu_system_voice, lang='en', speaker='mute',     # WD00
                                    speed=self.menu_system_voice_speedfactor)                   # WD00
            Observable.fire(event)
            text = self._fire_dispatchdgt(self.dgttranslate.text('B10_okvolume'))

        elif self.state == MenuState.SYS_DISP:
            if self.menu_system_display == Display.PONDER:
                text = self.enter_sys_disp_ponder_menu()
            if self.menu_system_display == Display.CONFIRM:
                text = self.enter_sys_disp_confirm_menu()
            if self.menu_system_display == Display.ENGINENAME:
                text = self.enter_sys_disp_enginename_menu()
            if self.menu_system_display == Display.CAPITAL:
                text = self.enter_sys_disp_capital_menu()
            if self.menu_system_display == Display.NOTATION:
                text = self.enter_sys_disp_notation_menu()

        elif self.state == MenuState.SYS_DISP_CONFIRM:
            text = self.enter_sys_disp_confirm_yesno_menu()

        elif self.state == MenuState.SYS_DISP_CONFIRM_YESNO:
            # do action!
            config = ConfigObj('picochess.ini')
            if self.menu_system_display_confirm:
                config['disable-confirm-message'] = self.menu_system_display_confirm
            elif 'disable-confirm-message' in config:
                del config['disable-confirm-message']
            config.write()
            text = self._fire_dispatchdgt(self.dgttranslate.text('B10_okconfirm'))

        elif self.state == MenuState.SYS_DISP_ENGINENAME:
            text = self.enter_sys_disp_enginename_yesno_menu()

        elif self.state == MenuState.SYS_DISP_ENGINENAME_YESNO:
            # do action!
            config = ConfigObj('picochess.ini')
            if not self.menu_system_display_enginename:
                config['show-engine'] = self.menu_system_display_enginename
            elif 'show-engine' in config:
                del config['show-engine']
            config.write()
            self.res_system_display_enginename = self.menu_system_display_enginename
            event = Event.SHOW_ENGINENAME(show_enginename=self.menu_system_display_enginename)
            Observable.fire(event)
            text = self._fire_dispatchdgt(self.dgttranslate.text('B10_okenginename'))

        elif self.state == MenuState.SYS_DISP_PONDER:
            text = self.enter_sys_disp_ponder_interval_menu()

        elif self.state == MenuState.SYS_DISP_PONDER_INTERVAL:
            # do action!
            write_picochess_ini('ponder-interval', self.menu_system_display_ponderinterval)
            text = self._fire_dispatchdgt(self.dgttranslate.text('B10_okponder'))

        elif self.state == MenuState.SYS_DISP_CAPITAL:
            text = self.enter_sys_disp_capital_yesno_menu()

        elif self.state == MenuState.SYS_DISP_CAPTIAL_YESNO:
            # do action!
            config = ConfigObj('picochess.ini')
            if self.menu_system_display_capital:
                config['enable-capital-letters'] = self.menu_system_display_capital
            elif 'enable-capital-letters' in config:
                del config['enable-capital-letters']
            config.write()
            text = self._fire_dispatchdgt(self.dgttranslate.text('B10_okcapital'))

        elif self.state == MenuState.SYS_DISP_NOTATION:
            text = self.enter_sys_disp_notation_move_menu()

        elif self.state == MenuState.SYS_DISP_NOTATION_MOVE:
            # do-action!
            config = ConfigObj('picochess.ini')
            if self.menu_system_display_notation:
                config['disable-short-notation'] = self.menu_system_display_notation
            elif 'disable-short-notation' in config:
                del config['disable-short-notation']
            config.write()
            text = self._fire_dispatchdgt(self.dgttranslate.text('B10_oknotation'))

        elif self.state == MenuState.SYS_EBOARD:
            text = self.enter_sys_eboard_type_menu()

        elif self.state == MenuState.SYS_EBOARD_TYPE:
            eboards = {EBoard.CERTABO: 'certabo', EBoard.CHESSLINK: 'chesslink', EBoard.CHESSNUT: 'chessnut',
                       EBoard.DGT: 'dgt'}
            eboard_type = eboards[self.menu_system_eboard_type]
            write_picochess_ini('board-type', eboard_type)
            text = self._fire_dispatchdgt(self.dgttranslate.text('B10_okeboard'))
            if eboard_type != self.board_type:
                # only reboot if e-board type is different from the current e-board type
                self._fire_event(Event.REBOOT(dev='menu'))

        else:  # Default
            pass
        self.current_text = text
        return text

    def main_left(self):
        """Change the menu state after LEFT action."""
        text = self.dgttranslate.text('Y00_errormenu')
        if self.state == MenuState.GAME:
            self.state = MenuState.PICOTUTOR
            self.menu_top = TopLoop.prev(self.menu_top)
            text = self.dgttranslate.text(self.menu_top.value)

        elif self.state == MenuState.GAME_GAMESAVE:
            self.state = MenuState.GAME_GAMECONTLAST
            self.menu_game = GameLoop.prev(self.menu_game)
            text = self.dgttranslate.text(self.menu_game.value)

        elif self.state == MenuState.GAME_GAMESAVE_GAME1:
            self.state = MenuState.GAME_GAMESAVE_GAME3
            self.menu_game_save = GameSaveLoop.prev(self.menu_game_save)
            text = self.dgttranslate.text(self.menu_game_save.value)

        elif self.state == MenuState.GAME_GAMESAVE_GAME2:
            self.state = MenuState.GAME_GAMESAVE_GAME1
            self.menu_game_save = GameSaveLoop.prev(self.menu_game_save)
            text = self.dgttranslate.text(self.menu_game_save.value)

        elif self.state == MenuState.GAME_GAMESAVE_GAME3:
            self.state = MenuState.GAME_GAMESAVE_GAME2
            self.menu_game_save = GameSaveLoop.prev(self.menu_game_save)
            text = self.dgttranslate.text(self.menu_game_save.value)

        elif self.state == MenuState.GAME_GAMEREAD:
            self.state = MenuState.GAME_GAMESAVE
            self.menu_game = GameLoop.prev(self.menu_game)
            text = self.dgttranslate.text(self.menu_game.value)

        elif self.state == MenuState.GAME_GAMEREAD_GAMELAST:
            self.state = MenuState.GAME_GAMEREAD_GAME3
            self.menu_game_read = GameReadLoop.prev(self.menu_game_read)
            text = self.dgttranslate.text(self.menu_game_read.value)

        elif self.state == MenuState.GAME_GAMEREAD_GAME1:
            self.state = MenuState.GAME_GAMEREAD_GAMELAST
            self.menu_game_read = GameReadLoop.prev(self.menu_game_read)
            text = self.dgttranslate.text(self.menu_game_read.value)

        elif self.state == MenuState.GAME_GAMEREAD_GAME2:
            self.state = MenuState.GAME_GAMEREAD_GAME1
            self.menu_game_read = GameReadLoop.prev(self.menu_game_read)
            text = self.dgttranslate.text(self.menu_game_read.value)

        elif self.state == MenuState.GAME_GAMEREAD_GAME3:
            self.state = MenuState.GAME_GAMEREAD_GAME2
            self.menu_game_read = GameReadLoop.prev(self.menu_game_read)
            text = self.dgttranslate.text(self.menu_game_read.value)

        elif self.state == MenuState.GAME_GAMECONTLAST:
            self.state = MenuState.GAME_GAMEALTMOVE
            self.menu_game = GameLoop.prev(self.menu_game)
            text = self.dgttranslate.text(self.menu_game.value)

        elif self.state == MenuState.GAME_GAMECONTLAST_ONOFF:
            self.menu_game_contlast = not self.menu_game_contlast
            msg = 'on' if self.menu_game_contlast else 'off'
            text = self.dgttranslate.text('B00_game_contlast_' + msg)

        elif self.state == MenuState.GAME_GAMEALTMOVE:
            self.state = MenuState.GAME_GAMEREAD
            self.menu_game = GameLoop.prev(self.menu_game)
            text = self.dgttranslate.text(self.menu_game.value)

        elif self.state == MenuState.GAME_GAMEALTMOVE_ONOFF:
            self.menu_game_altmove = not self.menu_game_altmove
            msg = 'on' if self.menu_game_altmove else 'off'
            text = self.dgttranslate.text('B00_game_altmove_' + msg)

        elif self.state == MenuState.PICOTUTOR:
            self.state = MenuState.SYS
            self.menu_top = TopLoop.prev(self.menu_top)
            text = self.dgttranslate.text(self.menu_top.value)

        elif self.state == MenuState.PICOTUTOR_PICOWATCHER:
            self.state = MenuState.PICOTUTOR_PICOCOMMENT
            self.menu_picotutor = PicoTutor.COMMENT
            text = self.dgttranslate.text(self.menu_picotutor.value)

        elif self.state == MenuState.PICOTUTOR_PICOWATCHER_ONOFF:
            self.menu_picotutor_picowatcher = not self.menu_picotutor_picowatcher
            msg = 'on' if self.menu_picotutor_picowatcher else 'off'
            text = self.dgttranslate.text('B00_picowatcher_' + msg)

        elif self.state == MenuState.PICOTUTOR_PICOCOACH:
            self.state = MenuState.PICOTUTOR_PICOWATCHER
            self.menu_picotutor = PicoTutor.WATCHER
            text = self.dgttranslate.text(self.menu_picotutor.value)

        elif self.state == MenuState.PICOTUTOR_PICOCOACH_ONOFF:
            self.menu_picotutor_picocoach = not self.menu_picotutor_picocoach
            msg = 'on' if self.menu_picotutor_picocoach else 'off'
            text = self.dgttranslate.text('B00_picocoach_' + msg)

        elif self.state == MenuState.PICOTUTOR_PICOEXPLORER:
            self.state = MenuState.PICOTUTOR_PICOCOACH
            self.menu_picotutor = PicoTutor.COACH
            text = self.dgttranslate.text(self.menu_picotutor.value)

        elif self.state == MenuState.PICOTUTOR_PICOEXPLORER_ONOFF:
            self.menu_picotutor_picoexplorer = not self.menu_picotutor_picoexplorer
            msg = 'on' if self.menu_picotutor_picoexplorer else 'off'
            text = self.dgttranslate.text('B00_picoexplorer_' + msg)

        elif self.state == MenuState.PICOTUTOR_PICOCOMMENT:
            self.state = MenuState.PICOTUTOR_PICOEXPLORER
            self.menu_picotutor = PicoTutor.EXPLORER
            text = self.dgttranslate.text(self.menu_picotutor.value)

        elif self.state == MenuState.PICOTUTOR_PICOCOMMENT_OFF:
            self.state = MenuState.PICOTUTOR_PICOCOMMENT_ON_ALL
            self.menu_picotutor_picocomment = PicoCommentLoop.prev(self.menu_picotutor_picocomment)
            text = self.dgttranslate.text(self.menu_picotutor_picocomment.value)

        elif self.state == MenuState.PICOTUTOR_PICOCOMMENT_ON_ALL:
            self.state = MenuState.PICOTUTOR_PICOCOMMENT_ON_ENG
            self.menu_picotutor_picocomment = PicoCommentLoop.prev(self.menu_picotutor_picocomment)
            text = self.dgttranslate.text(self.menu_picotutor_picocomment.value)

        elif self.state == MenuState.PICOTUTOR_PICOCOMMENT_ON_ENG:
            self.state = MenuState.PICOTUTOR_PICOCOMMENT_OFF
            self.menu_picotutor_picocomment = PicoCommentLoop.prev(self.menu_picotutor_picocomment)
            text = self.dgttranslate.text(self.menu_picotutor_picocomment.value)

        elif self.state == MenuState.MODE:
            self.state = MenuState.GAME
            self.menu_top = TopLoop.prev(self.menu_top)
            text = self.dgttranslate.text(self.menu_top.value)

        elif self.state == MenuState.MODE_TYPE:
            self.menu_mode = ModeLoop.prev(self.menu_mode)
            text = self.dgttranslate.text(self.menu_mode.value)

        elif self.state == MenuState.POS:
            self.state = MenuState.MODE
            self.menu_top = TopLoop.prev(self.menu_top)
            text = self.dgttranslate.text(self.menu_top.value)

        elif self.state == MenuState.POS_COL:
            self.menu_position_whitetomove = not self.menu_position_whitetomove
            text = self.dgttranslate.text('B00_sidewhite' if self.menu_position_whitetomove else 'B00_sideblack')

        elif self.state == MenuState.POS_REV:
            self.menu_position_reverse = not self.menu_position_reverse
            text = self.dgttranslate.text('B00_bw' if self.menu_position_reverse else 'B00_wb')

        elif self.state == MenuState.POS_UCI:
            if self.engine_has_960:
                self.menu_position_uci960 = not self.menu_position_uci960
                text = self.dgttranslate.text('B00_960yes' if self.menu_position_uci960 else 'B00_960no')
            else:
                text = self.dgttranslate.text('Y10_error960')

        elif self.state == MenuState.POS_READ:
            text = self.dgttranslate.text('B00_nofunction')

        elif self.state == MenuState.TIME:
            self.state = MenuState.POS
            self.menu_top = TopLoop.prev(self.menu_top)
            text = self.dgttranslate.text(self.menu_top.value)

        elif self.state == MenuState.TIME_BLITZ:
            self.state = MenuState.TIME_FIXED
            self.menu_time_mode = TimeModeLoop.prev(self.menu_time_mode)
            text = self.dgttranslate.text(self.menu_time_mode.value)

        elif self.state == MenuState.TIME_BLITZ_CTRL:
            self.menu_time_blitz = (self.menu_time_blitz - 1) % len(self.tc_blitz_map)
            text = self.dgttranslate.text('B00_tc_blitz', self.tc_blitz_list[self.menu_time_blitz])

        elif self.state == MenuState.TIME_FISCH:
            self.state = MenuState.TIME_BLITZ
            self.menu_time_mode = TimeModeLoop.prev(self.menu_time_mode)
            text = self.dgttranslate.text(self.menu_time_mode.value)

        elif self.state == MenuState.TIME_FISCH_CTRL:
            self.menu_time_fisch = (self.menu_time_fisch - 1) % len(self.tc_fisch_map)
            text = self.dgttranslate.text('B00_tc_fisch', self.tc_fisch_list[self.menu_time_fisch])

        elif self.state == MenuState.TIME_FIXED:
            self.state = MenuState.TIME_DEPTH
            self.menu_time_mode = TimeModeLoop.prev(self.menu_time_mode)
            text = self.dgttranslate.text(self.menu_time_mode.value)

        elif self.state == MenuState.TIME_FIXED_CTRL:
            self.menu_time_fixed = (self.menu_time_fixed - 1) % len(self.tc_fixed_map)
            text = self.dgttranslate.text('B00_tc_fixed', self.tc_fixed_list[self.menu_time_fixed])

        elif self.state == MenuState.TIME_TOURN:
            self.state = MenuState.TIME_FISCH
            self.menu_time_mode = TimeModeLoop.prev(self.menu_time_mode)
            text = self.dgttranslate.text(self.menu_time_mode.value)

        elif self.state == MenuState.TIME_TOURN_CTRL:
            self.menu_time_tourn = (self.menu_time_tourn - 1) % len(self.tc_tourn_map)
            text = self.dgttranslate.text('B00_tc_tourn', self.tc_tourn_list[self.menu_time_tourn])

        elif self.state == MenuState.TIME_DEPTH:
            self.state = MenuState.TIME_TOURN
            self.menu_time_mode = TimeModeLoop.prev(self.menu_time_mode)
            text = self.dgttranslate.text(self.menu_time_mode.value)

        elif self.state == MenuState.TIME_DEPTH_CTRL:
            self.menu_time_depth = (self.menu_time_depth - 1) % len(self.tc_depth_map)
            text = self.dgttranslate.text('B00_tc_depth', self.tc_depth_list[self.menu_time_depth])

        elif self.state == MenuState.BOOK:
            self.state = MenuState.TIME
            self.menu_top = TopLoop.prev(self.menu_top)
            text = self.dgttranslate.text(self.menu_top.value)

        elif self.state == MenuState.BOOK_NAME:
            self.menu_book = (self.menu_book - 1) % len(self.all_books)
            text = self._get_current_book_name()

        elif self.state == MenuState.ENGINE:
            self.state = MenuState.BOOK
            self.menu_top = TopLoop.prev(self.menu_top)
            text = self.dgttranslate.text(self.menu_top.value)

        elif self.state == MenuState.ENG_MODERN:
            self.state = MenuState.ENG_FAV
            self.menu_engine = EngineTopLoop.prev(self.menu_engine)
            text = self.dgttranslate.text(self.menu_engine.value)

        elif self.state == MenuState.ENG_MODERN_NAME:
            self.menu_modern_engine_index = (self.menu_modern_engine_index - 1) % len(self.installed_modern_engines)
            text = self._get_current_modern_engine_name()

        elif self.state == MenuState.ENG_MODERN_NAME_LEVEL:
            level_dict = self.installed_modern_engines[self.menu_modern_engine_index]['level_dict']
            self.menu_modern_engine_level = (self.menu_modern_engine_level - 1) % len(level_dict)
            msg = sorted(level_dict)[self.menu_modern_engine_level]
            text = self.dgttranslate.text('B00_level', msg)

        elif self.state == MenuState.ENG_RETRO:
            self.state = MenuState.ENG_MODERN
            self.menu_engine = EngineTopLoop.prev(self.menu_engine)
            text = self.dgttranslate.text(self.menu_engine.value)

        elif self.state == MenuState.ENG_RETRO_NAME:
            self.menu_retro_engine_index = (self.menu_retro_engine_index - 1) % len(self.installed_retro_engines)
            text = self._get_current_retro_engine_name()

        elif self.state == MenuState.ENG_RETRO_NAME_LEVEL:
            retro_level_dict = self.installed_retro_engines[self.menu_retro_engine_index]['level_dict']
            self.menu_retro_engine_level = (self.menu_retro_engine_level - 1) % len(retro_level_dict)
            msg = sorted(retro_level_dict)[self.menu_retro_engine_level]
            text = self.dgttranslate.text('B00_level', msg)

        elif self.state == MenuState.ENG_FAV:
            self.state = MenuState.ENG_RETRO
            self.menu_engine = EngineTopLoop.prev(self.menu_engine)
            text = self.dgttranslate.text(self.menu_engine.value)

        elif self.state == MenuState.ENG_FAV_NAME:
            self.menu_fav_engine_index = (self.menu_fav_engine_index - 1) % len(self.installed_fav_engines)
            text = self._get_current_fav_engine_name()

        elif self.state == MenuState.ENG_FAV_NAME_LEVEL:
            retro_level_dict = self.installed_fav_engines[self.menu_fav_engine_index]['level_dict']
            self.menu_fav_engine_level = (self.menu_fav_engine_level - 1) % len(retro_level_dict)
            msg = sorted(retro_level_dict)[self.menu_fav_engine_level]
            text = self.dgttranslate.text('B00_level', msg)

        elif self.state == MenuState.SYS:
            self.state = MenuState.ENGINE
            self.menu_top = TopLoop.prev(self.menu_top)
            text = self.dgttranslate.text(self.menu_top.value)

        elif self.state == MenuState.SYS_INFO:
            self.state = MenuState.SYS_EBOARD
            self.menu_system = SystemLoop.prev(self.menu_system)
            text = self.dgttranslate.text(self.menu_system.value)

        elif self.state == MenuState.SYS_INFO_VERS:
            self.state = MenuState.SYS_INFO_BATTERY
            self.menu_system_info = InfoLoop.prev(self.menu_system_info)
            text = self.dgttranslate.text(self.menu_system_info.value)

        elif self.state == MenuState.SYS_INFO_IP:
            self.state = MenuState.SYS_INFO_VERS
            self.menu_system_info = InfoLoop.prev(self.menu_system_info)
            text = self.dgttranslate.text(self.menu_system_info.value)

        elif self.state == MenuState.SYS_INFO_BATTERY:
            self.state = MenuState.SYS_INFO_IP
            self.menu_system_info = InfoLoop.prev(self.menu_system_info)
            text = self.dgttranslate.text(self.menu_system_info.value)

        elif self.state == MenuState.SYS_SOUND:
            self.state = MenuState.SYS_INFO
            self.menu_system = SystemLoop.prev(self.menu_system)
            text = self.dgttranslate.text(self.menu_system.value)

        elif self.state == MenuState.SYS_SOUND_BEEP:
            self.menu_system_sound = BeepLoop.prev(self.menu_system_sound)
            text = self.dgttranslate.text(self.menu_system_sound.value)

        elif self.state == MenuState.SYS_LANG:
            self.state = MenuState.SYS_SOUND
            self.menu_system = SystemLoop.prev(self.menu_system)
            text = self.dgttranslate.text(self.menu_system.value)

        elif self.state == MenuState.SYS_LANG_NAME:
            self.menu_system_language = LanguageLoop.prev(self.menu_system_language)
            text = self.dgttranslate.text(self.menu_system_language.value)

        elif self.state == MenuState.SYS_LOG:
            self.state = MenuState.SYS_LANG
            self.menu_system = SystemLoop.prev(self.menu_system)
            text = self.dgttranslate.text(self.menu_system.value)

        elif self.state == MenuState.SYS_VOICE:
            self.state = MenuState.SYS_LOG
            self.menu_system = SystemLoop.prev(self.menu_system)
            text = self.dgttranslate.text(self.menu_system.value)

        elif self.state == MenuState.SYS_VOICE_USER:
            self.state = MenuState.SYS_VOICE_COMP
            self.menu_system_voice = VoiceLoop.prev(self.menu_system_voice)
            text = self.dgttranslate.text(self.menu_system_voice.value)

        elif self.state == MenuState.SYS_VOICE_USER_MUTE:
            self.menu_system_voice_user_active = not self.menu_system_voice_user_active
            msg = 'on' if self.menu_system_voice_user_active else 'off'
            text = self.dgttranslate.text('B00_voice_' + msg)

        elif self.state == MenuState.SYS_VOICE_USER_MUTE_LANG:
            self.menu_system_voice_user_lang = (self.menu_system_voice_user_lang - 1) % len(self.voices_conf)
            vkey = self.voices_conf.keys()[self.menu_system_voice_user_lang]
            text = self.dgttranslate.text('B00_language_' + vkey + '_menu')  # voice using same as language

        elif self.state == MenuState.SYS_VOICE_USER_MUTE_LANG_SPEAK:
            vkey = self.voices_conf.keys()[self.menu_system_voice_user_lang]
            speakers = self.voices_conf[vkey]
            self.menu_system_voice_user_speak = (self.menu_system_voice_user_speak - 1) % len(speakers)
            text = self._get_current_speaker(speakers, self.menu_system_voice_user_speak)

        elif self.state == MenuState.SYS_VOICE_COMP:
            self.state = MenuState.SYS_VOICE_SPEED
            self.menu_system_voice = VoiceLoop.prev(self.menu_system_voice)
            text = self.dgttranslate.text(self.menu_system_voice.value)

        elif self.state == MenuState.SYS_VOICE_COMP_MUTE:
            self.menu_system_voice_comp_active = not self.menu_system_voice_comp_active
            msg = 'on' if self.menu_system_voice_comp_active else 'off'
            text = self.dgttranslate.text('B00_voice_' + msg)

        elif self.state == MenuState.SYS_VOICE_COMP_MUTE_LANG:
            self.menu_system_voice_comp_lang = (self.menu_system_voice_comp_lang - 1) % len(self.voices_conf)
            vkey = self.voices_conf.keys()[self.menu_system_voice_comp_lang]
            text = self.dgttranslate.text('B00_language_' + vkey + '_menu')  # voice using same as language

        elif self.state == MenuState.SYS_VOICE_COMP_MUTE_LANG_SPEAK:
            vkey = self.voices_conf.keys()[self.menu_system_voice_comp_lang]
            speakers = self.voices_conf[vkey]
            self.menu_system_voice_comp_speak = (self.menu_system_voice_comp_speak - 1) % len(speakers)
            text = self._get_current_speaker(speakers, self.menu_system_voice_comp_speak)

        elif self.state == MenuState.SYS_VOICE_SPEED:
            self.state = MenuState.SYS_VOICE_VOLUME
            self.menu_system_voice = VoiceLoop.prev(self.menu_system_voice)
            text = self.dgttranslate.text(self.menu_system_voice.value)

        elif self.state == MenuState.SYS_VOICE_SPEED_FACTOR:
            self.menu_system_voice_speedfactor = (self.menu_system_voice_speedfactor - 1) % 10
            text = self.dgttranslate.text('B00_voice_speed', str(self.menu_system_voice_speedfactor))

        elif self.state == MenuState.SYS_VOICE_VOLUME:
            self.state = MenuState.SYS_VOICE_USER
            self.menu_system_voice = VoiceLoop.prev(self.menu_system_voice)
            text = self.dgttranslate.text(self.menu_system_voice.value)

        elif self.state == MenuState.SYS_VOICE_VOLUME_FACTOR:
            self.menu_system_voice_volumefactor = (self.menu_system_voice_volumefactor - 1) % 11
            text = self.dgttranslate.text('B00_voice_volume', str(self.menu_system_voice_volumefactor))

        elif self.state == MenuState.SYS_DISP:
            self.state = MenuState.SYS_VOICE
            self.menu_system = SystemLoop.prev(self.menu_system)
            text = self.dgttranslate.text(self.menu_system.value)

        elif self.state == MenuState.SYS_DISP_PONDER:
            self.state = MenuState.SYS_DISP_NOTATION
            self.menu_system_display = DisplayLoop.prev(self.menu_system_display)
            text = self.dgttranslate.text(self.menu_system_display.value)

        elif self.state == MenuState.SYS_DISP_PONDER_INTERVAL:
            self.menu_system_display_ponderinterval -= 1
            if self.menu_system_display_ponderinterval < 1:
                self.menu_system_display_ponderinterval = 8
            text = self.dgttranslate.text('B00_ponder_interval', str(self.menu_system_display_ponderinterval))

        elif self.state == MenuState.SYS_DISP_CONFIRM:
            self.state = MenuState.SYS_DISP_PONDER
            self.menu_system_display = DisplayLoop.prev(self.menu_system_display)
            text = self.dgttranslate.text(self.menu_system_display.value)

        elif self.state == MenuState.SYS_DISP_CONFIRM_YESNO:
            self.menu_system_display_confirm = not self.menu_system_display_confirm
            msg = 'off' if self.menu_system_display_confirm else 'on'
            text = self.dgttranslate.text('B00_confirm_' + msg)

        elif self.state == MenuState.SYS_DISP_ENGINENAME:
            self.state = MenuState.SYS_DISP_CONFIRM
            self.menu_system_display = DisplayLoop.prev(self.menu_system_display)
            text = self.dgttranslate.text(self.menu_system_display.value)

        elif self.state == MenuState.SYS_DISP_ENGINENAME_YESNO:
            self.menu_system_display_enginename = not self.menu_system_display_enginename
            msg = 'on' if self.menu_system_display_enginename else 'off'
            text = self.dgttranslate.text('B00_enginename_' + msg)

        elif self.state == MenuState.SYS_DISP_CAPITAL:
            self.state = MenuState.SYS_DISP_ENGINENAME
            self.menu_system_display = DisplayLoop.prev(self.menu_system_display)
            text = self.dgttranslate.text(self.menu_system_display.value)

        elif self.state == MenuState.SYS_DISP_CAPTIAL_YESNO:
            self.menu_system_display_capital = not self.menu_system_display_capital
            msg = 'on' if self.menu_system_display_capital else 'off'
            text = self.dgttranslate.text('B00_capital_' + msg)

        elif self.state == MenuState.SYS_DISP_NOTATION:
            self.state = MenuState.SYS_DISP_CAPITAL
            self.menu_system_display = DisplayLoop.prev(self.menu_system_display)
            text = self.dgttranslate.text(self.menu_system_display.value)

        elif self.state == MenuState.SYS_DISP_NOTATION_MOVE:
            self.menu_system_display_notation = not self.menu_system_display_notation
            msg = 'long' if self.menu_system_display_notation else 'short'
            text = self.dgttranslate.text('B00_notation_' + msg)

        elif self.state == MenuState.SYS_EBOARD:
            self.state = MenuState.SYS_DISP
            self.menu_system = SystemLoop.prev(self.menu_system)
            text = self.dgttranslate.text(self.menu_system.value)

        elif self.state == MenuState.SYS_EBOARD_TYPE:
            self.menu_system_eboard_type = EBoardLoop.prev(self.menu_system_eboard_type)
            text = self.dgttranslate.text(self.menu_system_eboard_type.value)

        else:  # Default
            pass
        self.current_text = text
        return text

    def main_right(self):
        """Change the menu state after RIGHT action."""
        text = self.dgttranslate.text('Y00_errormenu')
        if False:  # switch-case
            pass
        elif self.state == MenuState.TOP:
            pass

        elif self.state == MenuState.GAME:
            self.state = MenuState.MODE
            self.menu_top = TopLoop.next(self.menu_top)
            text = self.dgttranslate.text(self.menu_top.value)

        elif self.state == MenuState.GAME_GAMESAVE:
            self.state = MenuState.GAME_GAMEREAD
            self.menu_game = GameLoop.next(self.menu_game)
            text = self.dgttranslate.text(self.menu_game.value)

        elif self.state == MenuState.GAME_GAMESAVE_GAME1:
            self.state = MenuState.GAME_GAMESAVE_GAME2
            self.menu_game_save = GameSaveLoop.next(self.menu_game_save)
            text = self.dgttranslate.text(self.menu_game_save.value)

        elif self.state == MenuState.GAME_GAMESAVE_GAME2:
            self.state = MenuState.GAME_GAMESAVE_GAME3
            self.menu_game_save = GameSaveLoop.next(self.menu_game_save)
            text = self.dgttranslate.text(self.menu_game_save.value)

        elif self.state == MenuState.GAME_GAMESAVE_GAME3:
            self.state = MenuState.GAME_GAMESAVE_GAME1
            self.menu_game_save = GameSaveLoop.next(self.menu_game_save)
            text = self.dgttranslate.text(self.menu_game_save.value)

        elif self.state == MenuState.GAME_GAMEREAD:
            self.state = MenuState.GAME_GAMEALTMOVE
            self.menu_game = GameLoop.next(self.menu_game)
            text = self.dgttranslate.text(self.menu_game.value)

        elif self.state == MenuState.GAME_GAMEREAD_GAMELAST:
            self.state = MenuState.GAME_GAMEREAD_GAME1
            self.menu_game_read = GameReadLoop.next(self.menu_game_read)
            text = self.dgttranslate.text(self.menu_game_read.value)

        elif self.state == MenuState.GAME_GAMEREAD_GAME1:
            self.state = MenuState.GAME_GAMEREAD_GAME2
            self.menu_game_read = GameReadLoop.next(self.menu_game_read)
            text = self.dgttranslate.text(self.menu_game_read.value)

        elif self.state == MenuState.GAME_GAMEREAD_GAME2:
            self.state = MenuState.GAME_GAMEREAD_GAME3
            self.menu_game_read = GameReadLoop.next(self.menu_game_read)
            text = self.dgttranslate.text(self.menu_game_read.value)

        elif self.state == MenuState.GAME_GAMEREAD_GAME3:
            self.state = MenuState.GAME_GAMEREAD_GAMELAST
            self.menu_game_read = GameReadLoop.next(self.menu_game_read)
            text = self.dgttranslate.text(self.menu_game_read.value)

        elif self.state == MenuState.GAME_GAMECONTLAST:
            self.state = MenuState.GAME_GAMESAVE
            self.menu_game = GameLoop.next(self.menu_game)
            text = self.dgttranslate.text(self.menu_game.value)

        elif self.state == MenuState.GAME_GAMEALTMOVE:
            self.state = MenuState.GAME_GAMECONTLAST
            self.menu_game = GameLoop.next(self.menu_game)
            text = self.dgttranslate.text(self.menu_game.value)

        elif self.state == MenuState.GAME_GAMEALTMOVE_ONOFF:
            self.menu_game_altmove = not self.menu_game_altmove
            msg = 'on' if self.menu_game_altmove else 'off'
            text = self.dgttranslate.text('B00_game_altmove_' + msg)

        elif self.state == MenuState.GAME_GAMECONTLAST_ONOFF:
            self.menu_game_contlast = not self.menu_game_contlast
            msg = 'on' if self.menu_game_contlast else 'off'
            text = self.dgttranslate.text('B00_game_contlast_' + msg)

        elif self.state == MenuState.PICOTUTOR:
            self.state = MenuState.GAME
            self.menu_top = TopLoop.next(self.menu_top)
            text = self.dgttranslate.text(self.menu_top.value)

        elif self.state == MenuState.PICOTUTOR_PICOWATCHER:
            self.state = MenuState.PICOTUTOR_PICOCOACH
            self.menu_picotutor = PicoTutor.COACH
            text = self.dgttranslate.text(self.menu_picotutor.value)

        elif self.state == MenuState.PICOTUTOR_PICOWATCHER_ONOFF:
            self.menu_picotutor_picowatcher = not self.menu_picotutor_picowatcher
            msg = 'on' if self.menu_picotutor_picowatcher else 'off'
            text = self.dgttranslate.text('B00_picowatcher_' + msg)

        elif self.state == MenuState.PICOTUTOR_PICOCOACH:
            self.state = MenuState.PICOTUTOR_PICOEXPLORER
            self.menu_picotutor = PicoTutor.EXPLORER
            text = self.dgttranslate.text(self.menu_picotutor.value)

        elif self.state == MenuState.PICOTUTOR_PICOCOACH_ONOFF:
            self.menu_picotutor_picocoach = not self.menu_picotutor_picocoach
            msg = 'on' if self.menu_picotutor_picocoach else 'off'
            text = self.dgttranslate.text('B00_picocoach_' + msg)

        elif self.state == MenuState.PICOTUTOR_PICOEXPLORER:
            self.state = MenuState.PICOTUTOR_PICOCOMMENT
            self.menu_picotutor = PicoTutor.COMMENT
            text = self.dgttranslate.text(self.menu_picotutor.value)

        elif self.state == MenuState.PICOTUTOR_PICOEXPLORER_ONOFF:
            self.menu_picotutor_picoexplorer = not self.menu_picotutor_picoexplorer
            msg = 'on' if self.menu_picotutor_picoexplorer else 'off'
            text = self.dgttranslate.text('B00_picoexplorer_' + msg)

        elif self.state == MenuState.PICOTUTOR_PICOCOMMENT:
            self.state = MenuState.PICOTUTOR_PICOWATCHER
            self.menu_picotutor = PicoTutor.WATCHER
            text = self.dgttranslate.text(self.menu_picotutor.value)

        elif self.state == MenuState.PICOTUTOR_PICOCOMMENT_OFF:
            self.state = MenuState.PICOTUTOR_PICOCOMMENT_ON_ENG
            self.menu_picotutor_picocomment = PicoCommentLoop.next(self.menu_picotutor_picocomment)
            text = self.dgttranslate.text(self.menu_picotutor_picocomment.value)

        elif self.state == MenuState.PICOTUTOR_PICOCOMMENT_ON_ENG:
            self.state = MenuState.PICOTUTOR_PICOCOMMENT_ON_ALL
            self.menu_picotutor_picocomment = PicoCommentLoop.next(self.menu_picotutor_picocomment)
            text = self.dgttranslate.text(self.menu_picotutor_picocomment.value)

        elif self.state == MenuState.PICOTUTOR_PICOCOMMENT_ON_ALL:
            self.state = MenuState.PICOTUTOR_PICOCOMMENT_OFF
            self.menu_picotutor_picocomment = PicoCommentLoop.next(self.menu_picotutor_picocomment)
            text = self.dgttranslate.text(self.menu_picotutor_picocomment.value)

        elif self.state == MenuState.MODE:
            self.state = MenuState.POS
            self.menu_top = TopLoop.next(self.menu_top)
            text = self.dgttranslate.text(self.menu_top.value)

        elif self.state == MenuState.MODE_TYPE:
            self.menu_mode = ModeLoop.next(self.menu_mode)
            text = self.dgttranslate.text(self.menu_mode.value)

        elif self.state == MenuState.POS:
            self.state = MenuState.TIME
            self.menu_top = TopLoop.next(self.menu_top)
            text = self.dgttranslate.text(self.menu_top.value)

        elif self.state == MenuState.POS_COL:
            self.menu_position_whitetomove = not self.menu_position_whitetomove
            text = self.dgttranslate.text('B00_sidewhite' if self.menu_position_whitetomove else 'B00_sideblack')

        elif self.state == MenuState.POS_REV:
            self.menu_position_reverse = not self.menu_position_reverse
            text = self.dgttranslate.text('B00_bw' if self.menu_position_reverse else 'B00_wb')

        elif self.state == MenuState.POS_UCI:
            if self.engine_has_960:
                self.menu_position_uci960 = not self.menu_position_uci960
                text = self.dgttranslate.text('B00_960yes' if self.menu_position_uci960 else 'B00_960no')
            else:
                text = self.dgttranslate.text('Y10_error960')

        elif self.state == MenuState.POS_READ:
            text = self.dgttranslate.text('B10_nofunction')

        elif self.state == MenuState.TIME:
            self.state = MenuState.BOOK
            self.menu_top = TopLoop.next(self.menu_top)
            text = self.dgttranslate.text(self.menu_top.value)

        elif self.state == MenuState.TIME_BLITZ:
            self.state = MenuState.TIME_FISCH
            self.menu_time_mode = TimeModeLoop.next(self.menu_time_mode)
            text = self.dgttranslate.text(self.menu_time_mode.value)

        elif self.state == MenuState.TIME_BLITZ_CTRL:
            self.menu_time_blitz = (self.menu_time_blitz + 1) % len(self.tc_blitz_map)
            text = self.dgttranslate.text('B00_tc_blitz', self.tc_blitz_list[self.menu_time_blitz])

        elif self.state == MenuState.TIME_FISCH:
            self.state = MenuState.TIME_TOURN
            self.menu_time_mode = TimeModeLoop.next(self.menu_time_mode)
            text = self.dgttranslate.text(self.menu_time_mode.value)

        elif self.state == MenuState.TIME_FISCH_CTRL:
            self.menu_time_fisch = (self.menu_time_fisch + 1) % len(self.tc_fisch_map)
            text = self.dgttranslate.text('B00_tc_fisch', self.tc_fisch_list[self.menu_time_fisch])

        elif self.state == MenuState.TIME_FIXED:
            self.state = MenuState.TIME_BLITZ
            self.menu_time_mode = TimeModeLoop.next(self.menu_time_mode)
            text = self.dgttranslate.text(self.menu_time_mode.value)

        elif self.state == MenuState.TIME_FIXED_CTRL:
            self.menu_time_fixed = (self.menu_time_fixed + 1) % len(self.tc_fixed_map)
            text = self.dgttranslate.text('B00_tc_fixed', self.tc_fixed_list[self.menu_time_fixed])

        elif self.state == MenuState.TIME_TOURN:
            self.state = MenuState.TIME_DEPTH
            self.menu_time_mode = TimeModeLoop.next(self.menu_time_mode)
            text = self.dgttranslate.text(self.menu_time_mode.value)

        elif self.state == MenuState.TIME_TOURN_CTRL:
            self.menu_time_tourn = (self.menu_time_tourn + 1) % len(self.tc_tourn_map)
            text = self.dgttranslate.text('B00_tc_tourn', self.tc_tourn_list[self.menu_time_tourn])

        elif self.state == MenuState.TIME_DEPTH:
            self.state = MenuState.TIME_FIXED
            self.menu_time_mode = TimeModeLoop.next(self.menu_time_mode)
            text = self.dgttranslate.text(self.menu_time_mode.value)

        elif self.state == MenuState.TIME_DEPTH_CTRL:
            self.menu_time_depth = (self.menu_time_depth + 1) % len(self.tc_depth_map)
            text = self.dgttranslate.text('B00_tc_depth', self.tc_depth_list[self.menu_time_depth])

        elif self.state == MenuState.BOOK:
            self.state = MenuState.ENGINE
            self.menu_top = TopLoop.next(self.menu_top)
            text = self.dgttranslate.text(self.menu_top.value)

        elif self.state == MenuState.BOOK_NAME:
            self.menu_book = (self.menu_book + 1) % len(self.all_books)
            text = self._get_current_book_name()

        elif self.state == MenuState.ENGINE:
            self.state = MenuState.SYS
            self.menu_top = TopLoop.next(self.menu_top)
            text = self.dgttranslate.text(self.menu_top.value)

        elif self.state == MenuState.ENG_MODERN:
            self.state = MenuState.ENG_RETRO
            self.menu_engine = EngineTopLoop.next(self.menu_engine)
            text = self.dgttranslate.text(self.menu_engine.value)

        elif self.state == MenuState.ENG_MODERN_NAME:
            self.menu_modern_engine_index = (self.menu_modern_engine_index + 1) % len(self.installed_modern_engines)
            text = self._get_current_modern_engine_name()

        elif self.state == MenuState.ENG_MODERN_NAME_LEVEL:
            level_dict = self.installed_modern_engines[self.menu_modern_engine_index]['level_dict']
            self.menu_modern_engine_level = (self.menu_modern_engine_level + 1) % len(level_dict)
            msg = sorted(level_dict)[self.menu_modern_engine_level]
            text = self.dgttranslate.text('B00_level', msg)

        elif self.state == MenuState.ENG_RETRO:
            self.state = MenuState.ENG_FAV
            self.menu_engine = EngineTopLoop.next(self.menu_engine)
            text = self.dgttranslate.text(self.menu_engine.value)

        elif self.state == MenuState.ENG_RETRO_NAME:
            self.menu_retro_engine_index = (self.menu_retro_engine_index + 1) % len(self.installed_retro_engines)
            text = self._get_current_retro_engine_name()

        elif self.state == MenuState.ENG_RETRO_NAME_LEVEL:
            retro_level_dict = self.installed_retro_engines[self.menu_retro_engine_index]['level_dict']
            self.menu_retro_engine_level = (self.menu_retro_engine_level + 1) % len(retro_level_dict)
            msg = sorted(retro_level_dict)[self.menu_retro_engine_level]
            text = self.dgttranslate.text('B00_level', msg)

        elif self.state == MenuState.ENG_FAV:
            self.state = MenuState.ENG_MODERN
            self.menu_engine = EngineTopLoop.next(self.menu_engine)
            text = self.dgttranslate.text(self.menu_engine.value)

        elif self.state == MenuState.ENG_FAV_NAME:
            self.menu_fav_engine_index = (self.menu_fav_engine_index + 1) % len(self.installed_fav_engines)
            text = self._get_current_fav_engine_name()

        elif self.state == MenuState.ENG_FAV_NAME_LEVEL:
            retro_level_dict = self.installed_fav_engines[self.menu_fav_engine_index]['level_dict']
            self.menu_fav_engine_level = (self.menu_fav_engine_level + 1) % len(retro_level_dict)
            msg = sorted(retro_level_dict)[self.menu_fav_engine_level]
            text = self.dgttranslate.text('B00_level', msg)

        elif self.state == MenuState.SYS:
            self.state = MenuState.PICOTUTOR
            self.menu_top = TopLoop.next(self.menu_top)
            text = self.dgttranslate.text(self.menu_top.value)

        elif self.state == MenuState.SYS_INFO:
            self.state = MenuState.SYS_SOUND
            self.menu_system = SystemLoop.next(self.menu_system)
            text = self.dgttranslate.text(self.menu_system.value)

        elif self.state == MenuState.SYS_INFO_VERS:
            self.state = MenuState.SYS_INFO_IP
            self.menu_system_info = InfoLoop.next(self.menu_system_info)
            text = self.dgttranslate.text(self.menu_system_info.value)

        elif self.state == MenuState.SYS_INFO_IP:
            self.state = MenuState.SYS_INFO_BATTERY
            self.menu_system_info = InfoLoop.next(self.menu_system_info)
            text = self.dgttranslate.text(self.menu_system_info.value)

        elif self.state == MenuState.SYS_INFO_BATTERY:
            self.state = MenuState.SYS_INFO_VERS
            self.menu_system_info = InfoLoop.next(self.menu_system_info)
            text = self.dgttranslate.text(self.menu_system_info.value)

        elif self.state == MenuState.SYS_SOUND:
            self.state = MenuState.SYS_LANG
            self.menu_system = SystemLoop.next(self.menu_system)
            text = self.dgttranslate.text(self.menu_system.value)

        elif self.state == MenuState.SYS_SOUND_BEEP:
            self.menu_system_sound = BeepLoop.next(self.menu_system_sound)
            text = self.dgttranslate.text(self.menu_system_sound.value)

        elif self.state == MenuState.SYS_LANG:
            self.state = MenuState.SYS_LOG
            self.menu_system = SystemLoop.next(self.menu_system)
            text = self.dgttranslate.text(self.menu_system.value)

        elif self.state == MenuState.SYS_LANG_NAME:
            self.menu_system_language = LanguageLoop.next(self.menu_system_language)
            text = self.dgttranslate.text(self.menu_system_language.value)

        elif self.state == MenuState.SYS_LOG:
            self.state = MenuState.SYS_VOICE
            self.menu_system = SystemLoop.next(self.menu_system)
            text = self.dgttranslate.text(self.menu_system.value)

        elif self.state == MenuState.SYS_VOICE:
            self.state = MenuState.SYS_DISP
            self.menu_system = SystemLoop.next(self.menu_system)
            text = self.dgttranslate.text(self.menu_system.value)

        elif self.state == MenuState.SYS_VOICE_USER:
            self.state = MenuState.SYS_VOICE_VOLUME
            self.menu_system_voice = VoiceLoop.next(self.menu_system_voice)
            text = self.dgttranslate.text(self.menu_system_voice.value)

        elif self.state == MenuState.SYS_VOICE_USER_MUTE:
            self.menu_system_voice_user_active = not self.menu_system_voice_user_active
            msg = 'on' if self.menu_system_voice_user_active else 'off'
            text = self.dgttranslate.text('B00_voice_' + msg)

        elif self.state == MenuState.SYS_VOICE_USER_MUTE_LANG:
            self.menu_system_voice_user_lang = (self.menu_system_voice_user_lang + 1) % len(self.voices_conf)
            vkey = self.voices_conf.keys()[self.menu_system_voice_user_lang]
            text = self.dgttranslate.text('B00_language_' + vkey + '_menu')  # voice using same as language

        elif self.state == MenuState.SYS_VOICE_USER_MUTE_LANG_SPEAK:
            vkey = self.voices_conf.keys()[self.menu_system_voice_user_lang]
            speakers = self.voices_conf[vkey]
            self.menu_system_voice_user_speak = (self.menu_system_voice_user_speak + 1) % len(speakers)
            text = self._get_current_speaker(speakers, self.menu_system_voice_user_speak)

        elif self.state == MenuState.SYS_VOICE_COMP:
            self.state = MenuState.SYS_VOICE_USER
            self.menu_system_voice = VoiceLoop.next(self.menu_system_voice)
            text = self.dgttranslate.text(self.menu_system_voice.value)

        elif self.state == MenuState.SYS_VOICE_COMP_MUTE:
            self.menu_system_voice_comp_active = not self.menu_system_voice_comp_active
            msg = 'on' if self.menu_system_voice_comp_active else 'off'
            text = self.dgttranslate.text('B00_voice_' + msg)

        elif self.state == MenuState.SYS_VOICE_COMP_MUTE_LANG:
            self.menu_system_voice_comp_lang = (self.menu_system_voice_comp_lang + 1) % len(self.voices_conf)
            vkey = self.voices_conf.keys()[self.menu_system_voice_comp_lang]
            text = self.dgttranslate.text('B00_language_' + vkey + '_menu')  # voice using same as language

        elif self.state == MenuState.SYS_VOICE_COMP_MUTE_LANG_SPEAK:
            vkey = self.voices_conf.keys()[self.menu_system_voice_comp_lang]
            speakers = self.voices_conf[vkey]
            self.menu_system_voice_comp_speak = (self.menu_system_voice_comp_speak + 1) % len(speakers)
            text = self._get_current_speaker(speakers, self.menu_system_voice_comp_speak)

        elif self.state == MenuState.SYS_VOICE_SPEED:
            self.state = MenuState.SYS_VOICE_COMP
            self.menu_system_voice = VoiceLoop.next(self.menu_system_voice)
            text = self.dgttranslate.text(self.menu_system_voice.value)

        elif self.state == MenuState.SYS_VOICE_SPEED_FACTOR:
            self.menu_system_voice_speedfactor = (self.menu_system_voice_speedfactor + 1) % 10
            text = self.dgttranslate.text('B00_voice_speed', str(self.menu_system_voice_speedfactor))

        elif self.state == MenuState.SYS_VOICE_VOLUME:
            self.state = MenuState.SYS_VOICE_SPEED
            self.menu_system_voice = VoiceLoop.next(self.menu_system_voice)
            text = self.dgttranslate.text(self.menu_system_voice.value)

        elif self.state == MenuState.SYS_VOICE_VOLUME_FACTOR:
            self.menu_system_voice_volumefactor = (self.menu_system_voice_volumefactor + 1) % 11
            text = self.dgttranslate.text('B00_voice_volume', str(self.menu_system_voice_volumefactor))

        elif self.state == MenuState.SYS_DISP:
            self.state = MenuState.SYS_EBOARD
            self.menu_system = SystemLoop.next(self.menu_system)
            text = self.dgttranslate.text(self.menu_system.value)

        elif self.state == MenuState.SYS_DISP_PONDER:
            self.state = MenuState.SYS_DISP_CONFIRM
            self.menu_system_display = DisplayLoop.next(self.menu_system_display)
            text = self.dgttranslate.text(self.menu_system_display.value)

        elif self.state == MenuState.SYS_DISP_PONDER_INTERVAL:
            self.menu_system_display_ponderinterval += 1
            if self.menu_system_display_ponderinterval > 8:
                self.menu_system_display_ponderinterval = 1
            text = self.dgttranslate.text('B00_ponder_interval', str(self.menu_system_display_ponderinterval))

        elif self.state == MenuState.SYS_DISP_CONFIRM:
            self.state = MenuState.SYS_DISP_ENGINENAME
            self.menu_system_display = DisplayLoop.next(self.menu_system_display)
            text = self.dgttranslate.text(self.menu_system_display.value)

        elif self.state == MenuState.SYS_DISP_CONFIRM_YESNO:
            self.menu_system_display_confirm = not self.menu_system_display_confirm
            msg = 'off' if self.menu_system_display_confirm else 'on'
            text = self.dgttranslate.text('B00_confirm_' + msg)

        elif self.state == MenuState.SYS_DISP_ENGINENAME:
            self.state = MenuState.SYS_DISP_CAPITAL
            self.menu_system_display = DisplayLoop.next(self.menu_system_display)
            text = self.dgttranslate.text(self.menu_system_display.value)

        elif self.state == MenuState.SYS_DISP_ENGINENAME_YESNO:
            self.menu_system_display_enginename = not self.menu_system_display_enginename
            msg = 'on' if self.menu_system_display_enginename else 'off'
            text = self.dgttranslate.text('B00_enginename_' + msg)

        elif self.state == MenuState.SYS_DISP_CAPITAL:
            self.state = MenuState.SYS_DISP_NOTATION
            self.menu_system_display = DisplayLoop.next(self.menu_system_display)
            text = self.dgttranslate.text(self.menu_system_display.value)

        elif self.state == MenuState.SYS_DISP_CAPTIAL_YESNO:
            self.menu_system_display_capital = not self.menu_system_display_capital
            msg = 'on' if self.menu_system_display_capital else 'off'
            text = self.dgttranslate.text('B00_capital_' + msg)

        elif self.state == MenuState.SYS_DISP_NOTATION:
            self.state = MenuState.SYS_DISP_PONDER
            self.menu_system_display = DisplayLoop.next(self.menu_system_display)
            text = self.dgttranslate.text(self.menu_system_display.value)

        elif self.state == MenuState.SYS_DISP_NOTATION_MOVE:
            self.menu_system_display_notation = not self.menu_system_display_notation
            msg = 'long' if self.menu_system_display_notation else 'short'
            text = self.dgttranslate.text('B00_notation_' + msg)

        elif self.state == MenuState.SYS_EBOARD:
            self.state = MenuState.SYS_INFO
            self.menu_system = SystemLoop.next(self.menu_system)
            text = self.dgttranslate.text(self.menu_system.value)

        elif self.state == MenuState.SYS_EBOARD_TYPE:
            self.menu_system_eboard_type = EBoardLoop.next(self.menu_system_eboard_type)
            text = self.dgttranslate.text(self.menu_system_eboard_type.value)

        else:  # Default
            pass
        self.current_text = text
        return text

    def main_middle(self, dev):
        """Change the menu state after MIDDLE action."""
        def _exit_position():
            self.state = MenuState.POS_READ
            return self.main_down()

        if self.inside_picochess_time(dev):
            text = self.updt_middle(dev)
        else:
            text = self.dgttranslate.text('B00_nofunction')
            if False:  # switch-case
                pass
            elif self.state == MenuState.POS:
                text = _exit_position()

            elif self.state == MenuState.POS_COL:
                text = _exit_position()

            elif self.state == MenuState.POS_REV:
                text = _exit_position()

            elif self.state == MenuState.POS_UCI:
                text = _exit_position()

            elif self.state == MenuState.POS_READ:
                text = _exit_position()

            else:  # Default
                pass
        self.current_text = text
        return text

    def updt_middle(self, dev):
        """Change the menu state after MIDDLE action."""
        self.updt_devs.add(dev)
        text = self.dgttranslate.text('B00_updt_version', self.updt_tags[self.updt_version][1], devs=self.updt_devs)
        text.rd = ClockIcons.DOT
        logging.debug('enter update menu dev: %s', dev)
        self.updt_top = True
        return text

    def updt_right(self):
        """Change the menu state after RIGHT action."""
        self.updt_version = (self.updt_version + 1) % len(self.updt_tags)
        text = self.dgttranslate.text('B00_updt_version', self.updt_tags[self.updt_version][1], devs=self.updt_devs)
        text.rd = ClockIcons.DOT
        return text

    def updt_left(self):
        """Change the menu state after LEFT action."""
        self.updt_version = (self.updt_version - 1) % len(self.updt_tags)
        text = self.dgttranslate.text('B00_updt_version', self.updt_tags[self.updt_version][1], devs=self.updt_devs)
        text.rd = ClockIcons.DOT
        return text

    def updt_down(self, dev):
        """Change the menu state after DOWN action."""
        logging.debug('leave update menu dev: %s', dev)
        self.updt_top = False
        self.updt_devs.discard(dev)
        self.enter_top_menu()
        return self.updt_tags[self.updt_version][0]

    def updt_up(self, dev):
        """Change the menu state after UP action."""
        logging.debug('leave update menu dev: %s', dev)
        self.updt_top = False
        self.updt_devs.discard(dev)
        text = self.enter_top_menu()
        return text

    def inside_main_menu(self):
        """Check if currently inside the menu."""
        return self.state != MenuState.TOP

    def get_current_text(self):
        """Return the current text."""
        return self.current_text
