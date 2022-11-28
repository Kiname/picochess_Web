import os

import unittest
from unittest.mock import patch

from dgt.menu import DgtMenu, MenuState
from dgt.translate import DgtTranslate
from uci.read import read_engine_ini


class TestDgtMenu(unittest.TestCase):

    def create_menu(self, machine_mock):
        machine_mock.return_value = '..' + os.sep + 'tests'  # return the tests path as the platform engine path
        modern_engines = read_engine_ini(filename='engines.ini')
        retro_engines = read_engine_ini(filename='retro.ini')
        favorite_engines = read_engine_ini(filename='favorites.ini')
        installed_engines = modern_engines + retro_engines

        trans = DgtTranslate('none', 0, 'en', 'version')
        menu = DgtMenu(False, 0, '', '', 0, False, False, '', None, False, 0, 'dgt', False, False, trans)
        menu.set_modern_engines(modern_engines)
        menu.set_retro_engines(retro_engines)
        menu.set_favorite_engines(favorite_engines)
        menu.installed_engines = installed_engines
        return menu

    @patch('platform.machine')
    def test_engine_menu_traversal(self, machine_mock):
        menu = self.create_menu(machine_mock)
        menu.set_state_current_engine()
        text = menu.get_current_engine_name()
        self.assertEqual('Lc0', text.large_text)
        menu.enter_top_menu()
        self.assertEqual(MenuState.TOP, menu.state)
        menu.main_down()
        # start with engine menu from top menu
        self.assertEqual(MenuState.ENGINE, menu.state)
        menu.main_right()
        self.assertEqual(MenuState.SYS, menu.state)
        menu.main_left()
        self.assertEqual(MenuState.ENGINE, menu.state)
        menu.main_left()
        self.assertEqual(MenuState.BOOK, menu.state)
        menu.main_right()
        self.assertEqual(MenuState.ENGINE, menu.state)
        menu.main_down()
        self.assertEqual(MenuState.ENG_MODERN, menu.state)
        menu.main_up()
        self.assertEqual(MenuState.ENGINE, menu.state)
        menu.main_down()
        self.assertEqual(MenuState.ENG_MODERN, menu.state)
        menu.main_right()
        self.assertEqual(MenuState.ENG_RETRO, menu.state)
        menu.main_up()
        self.assertEqual(MenuState.ENGINE, menu.state)
        menu.main_down()
        self.assertEqual(MenuState.ENG_RETRO, menu.state)
        menu.main_right()
        self.assertEqual(MenuState.ENG_FAV, menu.state)
        menu.main_up()
        self.assertEqual(MenuState.ENGINE, menu.state)
        menu.main_down()
        self.assertEqual(MenuState.ENG_FAV, menu.state)
        menu.main_right()
        self.assertEqual(MenuState.ENG_MODERN, menu.state)
        menu.main_left()
        self.assertEqual(MenuState.ENG_FAV, menu.state)
        menu.main_left()
        self.assertEqual(MenuState.ENG_RETRO, menu.state)
        menu.main_left()
        # modern engines
        self.assertEqual(MenuState.ENG_MODERN, menu.state)
        modern_engine_name = menu.main_down()
        self.assertEqual(MenuState.ENG_MODERN_NAME, menu.state)
        self.assertEqual('Lc0', modern_engine_name.large_text)
        modern_engine_name = menu.main_right()
        self.assertEqual('McBrain9932', modern_engine_name.large_text)
        modern_engine_name = menu.main_left()
        self.assertEqual('Lc0', modern_engine_name.large_text)
        menu.main_up()
        self.assertEqual(MenuState.ENG_MODERN, menu.state)
        menu.main_right()
        # retro engines
        self.assertEqual(MenuState.ENG_RETRO, menu.state)
        retro_engine_name = menu.main_down()
        self.assertEqual(MenuState.ENG_RETRO_NAME, menu.state)
        self.assertEqual('Mep.Academy', retro_engine_name.large_text)
        retro_engine_name = menu.main_right()
        self.assertEqual('M.Amsterdam', retro_engine_name.large_text)
        retro_engine_name = menu.main_left()
        self.assertEqual('Mep.Academy', retro_engine_name.large_text)
        menu.main_up()
        self.assertEqual(MenuState.ENG_RETRO, menu.state)
        menu.main_right()
        # favorite engines
        self.assertEqual(MenuState.ENG_FAV, menu.state)
        fav_engine_name = menu.main_down()
        self.assertEqual(MenuState.ENG_FAV_NAME, menu.state)
        self.assertEqual('Stockfish 15', fav_engine_name.large_text)
        fav_engine_name = menu.main_right()
        self.assertEqual('Rodent 4', fav_engine_name.large_text)
        fav_engine_name = menu.main_left()
        self.assertEqual('Stockfish 15', fav_engine_name.large_text)
        # level of a favorite engine
        level = menu.main_down()
        self.assertEqual(MenuState.ENG_FAV_NAME_LEVEL, menu.state)
        self.assertEqual('level     0', level.large_text)
        level = menu.main_right()
        self.assertEqual('level     1', level.large_text)
        level = menu.main_left()
        self.assertEqual('level     0', level.large_text)

        menu.main_up()
        self.assertEqual(MenuState.ENG_FAV_NAME, menu.state)
        menu.main_up()
        menu.main_right()
        modern_engine_name = menu.main_down()
        self.assertEqual(MenuState.ENG_MODERN_NAME, menu.state)
        self.assertEqual('Lc0', modern_engine_name.large_text)
        # level of a modern engine
        level = menu.main_down()
        self.assertEqual(MenuState.ENG_MODERN_NAME_LEVEL, menu.state)
        self.assertEqual('1 Core', level.large_text)
        level = menu.main_right()
        self.assertEqual('2 Cores', level.large_text)
        level = menu.main_left()
        self.assertEqual('1 Core', level.large_text)

        menu.main_up()
        self.assertEqual(MenuState.ENG_MODERN_NAME, menu.state)
        menu.main_up()
        menu.main_right()
        retro_engine_name = menu.main_down()
        self.assertEqual(MenuState.ENG_RETRO_NAME, menu.state)
        self.assertEqual('Mep.Academy', retro_engine_name.large_text)
        # level of a retro engine
        level = menu.main_down()
        self.assertEqual(MenuState.ENG_RETRO_NAME_LEVEL, menu.state)
        self.assertEqual('Level 00 - speed', level.large_text)
        level = menu.main_right()
        self.assertEqual('Level 01 - 5s move', level.large_text)
        level = menu.main_left()
        self.assertEqual('Level 00 - speed', level.large_text)

        menu.main_up()
        self.assertEqual(MenuState.ENG_RETRO_NAME, menu.state)

    @patch('platform.machine')
    def test_modern_engine_retrieval(self, machine_mock):
        menu = self.create_menu(machine_mock)
        menu.set_state_current_engine()
        menu.enter_top_menu()
        self.assertEqual('Engine', menu.main_down().large_text.strip())
        self.assertEqual('Modern Engines', menu.main_down().large_text)
        menu.main_down()  # first engine 'Lc0'
        self.assertEqual('zurichess', menu.main_left().large_text)  # last engine
        self.assertEqual('level     0', menu.main_down().large_text)  # level of zurichess
        self.assertFalse(menu.main_down())  # select zurichess engine
        self.assertEqual('zurichess', menu.get_current_engine_name().large_text)

        self.assertEqual('Engine', menu.main_down().large_text.strip())
        self.assertEqual('Modern Engines', menu.main_down().large_text)
        self.assertEqual('zurichess', menu.main_down().large_text)  # previously selected engine

    @patch('platform.machine')
    def test_retro_engine_retrieval(self, machine_mock):
        menu = self.create_menu(machine_mock)
        menu.set_state_current_engine()
        menu.enter_top_menu()
        self.assertEqual('Engine', menu.main_down().large_text.strip())
        self.assertEqual('Modern Engines', menu.main_down().large_text)
        self.assertEqual('Retro Engines', menu.main_right().large_text)
        menu.main_down()  # first retro engine 'Mep.Academy'
        self.assertEqual('Schachzwerg', menu.main_left().large_text)  # last retro engine
        self.assertFalse(menu.main_down())  # select Schachzwerg engine
        self.assertEqual('Schachzwerg', menu.get_current_engine_name().large_text)

        self.assertEqual('Engine', menu.main_down().large_text.strip())
        self.assertEqual('Retro Engines', menu.main_down().large_text)
        self.assertEqual('Schachzwerg', menu.main_down().large_text)  # previously selected engine

    @patch('platform.machine')
    def test_retro_engine_level_selection(self, machine_mock):
        menu = self.create_menu(machine_mock)
        menu.set_state_current_engine()
        menu.enter_top_menu()
        self.assertEqual('Engine', menu.main_down().large_text.strip())
        self.assertEqual('Modern Engines', menu.main_down().large_text)
        self.assertEqual('Retro Engines', menu.main_right().large_text)
        menu.main_down()  # first retro engine 'Mep.Academy'
        menu.main_right()  # second retro engine
        self.assertEqual('Mep. Milano', menu.main_right().large_text)  # third retro engine
        menu.main_down()  # level selection menu
        self.assertEqual('Level 10 - 60m game', menu.main_left().large_text)  # select level for engine 'Mep. Milano',
        self.assertFalse(menu.main_down())
        self.assertEqual('Mep. Milano', menu.get_current_engine_name().large_text)

        self.assertEqual('Engine', menu.main_down().large_text.strip())
        self.assertEqual('Retro Engines', menu.main_down().large_text)
        self.assertEqual('Mep. Milano', menu.main_down().large_text)  # previously selected engine
        self.assertEqual('Level 10 - 60m game', menu.main_down().large_text)  # previously selected engine level

    @patch('platform.machine')
    def test_modern_engine_after_retro(self, machine_mock):
        # select modern engine
        menu = self.create_menu(machine_mock)
        menu.set_state_current_engine()
        menu.enter_top_menu()
        self.assertEqual('Engine', menu.main_down().large_text.strip())
        self.assertEqual('Modern Engines', menu.main_down().large_text)
        menu.main_down()  # first engine 'Lc0'
        self.assertEqual('zurichess', menu.main_left().large_text)  # last engine
        self.assertEqual('level     0', menu.main_down().large_text)  # level of zurichess
        self.assertFalse(menu.main_down())  # select zurichess engine

        # select retro engine
        menu.enter_top_menu()
        self.assertEqual('Engine', menu.main_down().large_text.strip())
        self.assertEqual('Modern Engines', menu.main_down().large_text)
        self.assertEqual('Retro Engines', menu.main_right().large_text)
        menu.main_down()  # first retro engine 'Mep.Academy'
        self.assertEqual('Schachzwerg', menu.main_left().large_text)  # last retro engine
        self.assertFalse(menu.main_down())  # select Schachzwerg engine

        # re-select modern engine
        menu.enter_top_menu()
        self.assertEqual('Engine', menu.main_down().large_text.strip())
        self.assertEqual('Retro Engines', menu.main_down().large_text)
        self.assertEqual('Modern Engines', menu.main_left().large_text)
        self.assertEqual('zurichess', menu.main_down().large_text)  # previous modern engine
