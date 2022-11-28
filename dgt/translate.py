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

import logging
from dgt.util import Beep, BeepLevel
from dgt.api import Dgt


class DgtTranslate(object):

    """Handle translations for clock texts or moves."""
    def __init__(self, beep_config: str, beep_level: int, language: str, picochess_version: str):
        self.ConfigToBeep = {'all': Beep.ON, 'none': Beep.OFF, 'some': Beep.SOME}
        self.beep = self.ConfigToBeep[beep_config]
        self.beep_level = beep_level
        self.language = language
        self.version = picochess_version
        self.capital = False  # Set from dgt.menu lateron
        self.notation = False  # Set from dgt.menu lateron

    def beep_to_config(self, beep: Beep):
        """Transfer beep to dict."""
        return dict(zip(self.ConfigToBeep.values(), self.ConfigToBeep.keys()))[beep]

    def bl(self, beeplevel: BeepLevel):
        """Transfer beeplevel to bool."""
        if self.beep == Beep.ON:
            return True
        if self.beep == Beep.OFF:
            return False
        return bool(self.beep_level & beeplevel.value)

    def set_beep(self, beep: Beep):
        """Set beep."""
        self.beep = beep

    def set_language(self, language: str):
        """Set language."""
        self.language = language

    def set_capital(self, capital: bool):
        """Set capital letters."""
        self.capital = capital

    def capital_text(self, text: Dgt.DISPLAY_TEXT) -> Dgt.DISPLAY_TEXT:
        """Transfer text to capital text or not."""
        if self.capital:
            text.medium_text = text.medium_text.upper()
            text.large_text = text.large_text.upper()
        return text

    def set_notation(self, notation: bool):
        """Set notation."""
        self.notation = notation

    def text(self, str_code: str, msg='', devs=None):
        """Return standard text for clock display."""
        if devs is None:  # prevent W0102 error
            devs = {'ser', 'i2c', 'web'}

        entxt = detxt = nltxt = frtxt = estxt = ittxt = None  # error case

        (code, text_id) = str_code.split('_', 1)
        if code[0] == 'B':
            beep = self.bl(BeepLevel.BUTTON)
        elif code[0] == 'N':
            beep = self.bl(BeepLevel.NO)
        elif code[0] == 'Y':
            beep = self.bl(BeepLevel.YES)
        elif code[0] == 'K':
            beep = self.bl(BeepLevel.OKAY)
        elif code[0] == 'C':
            beep = self.bl(BeepLevel.CONFIG)
        elif code[0] == 'M':
            beep = self.bl(BeepLevel.MAP)
        else:
            beep = False
        maxtime = int(code[1:]) / 10
        wait = False

        if text_id == 'default':
            entxt = Dgt.DISPLAY_TEXT(large_text=msg[:38], medium_text=msg[:8], small_text=msg[:6])
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'onlineuser':
            l_len = len(msg) - 1
            l_msg = msg[:l_len]
            msg = l_msg.ljust(11, ' ')
            entxt = Dgt.DISPLAY_TEXT(large_text=msg[:38], medium_text=msg[:8], small_text=msg[:6])
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'pgngame_end':
            entxt = Dgt.DISPLAY_TEXT(large_text='End of Game', medium_text='Game End', small_text='ended ')
            detxt = Dgt.DISPLAY_TEXT(large_text='Partie Ende', medium_text='Par.Ende', small_text='P.Ende')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Fine partit', medium_text='Fine par', small_text='F.part')
        if text_id == 'timecontrol_check':
            if 'TC' == msg:
                entxt = Dgt.DISPLAY_TEXT(large_text='Time Control', medium_text='T.Control', small_text='timeco')
                detxt = Dgt.DISPLAY_TEXT(large_text='Zeitkontrolle', medium_text='Zeitkont.', small_text='Z.Kont')
                nltxt = entxt
                frtxt = entxt
                estxt = entxt
                ittxt = Dgt.DISPLAY_TEXT(large_text='Contr.Tempo', medium_text='Con.Tempo', small_text='C.Temp')
            elif 'M' == msg[0]:
                l_msg = msg[1:] + 'min'
                l_msg = l_msg.ljust(11, ' ')
                entxt = Dgt.DISPLAY_TEXT(large_text=l_msg[:38], medium_text=l_msg[:8], small_text=l_msg[:6])
                detxt = entxt
                nltxt = entxt
                frtxt = entxt
                estxt = entxt
                ittxt = entxt
            elif 'A' == msg[0]:
                l_msg = 'Add ' + msg[1:]
                l_msg = l_msg.ljust(11, ' ')
                entxt = Dgt.DISPLAY_TEXT(large_text=l_msg[:38], medium_text=l_msg[:8], small_text=l_msg[:6])
                detxt = entxt
                nltxt = entxt
                frtxt = entxt
                estxt = entxt
                ittxt = entxt
            else:
                entxt = Dgt.DISPLAY_TEXT(large_text=msg[:38], medium_text=msg[:8], small_text=msg[:6])
                detxt = entxt
                nltxt = entxt
                frtxt = entxt
                estxt = entxt
                ittxt = entxt
        if text_id == 'okpicocomment':
            entxt = Dgt.DISPLAY_TEXT(large_text='Comment ok ', medium_text='Comm ok ', small_text='com ok')
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'picowatcher':
            entxt = Dgt.DISPLAY_TEXT(large_text='Pico Watcher', medium_text='Watcher ', small_text='watchr')
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'okpicowatcher':
            entxt = Dgt.DISPLAY_TEXT(large_text='Watcher ok ', medium_text='Watcherok', small_text='w: ok')
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'picowatcher_on':
            entxt = Dgt.DISPLAY_TEXT(large_text='Watcher on ', medium_text='Watch on', small_text='w on  ')
            detxt = Dgt.DISPLAY_TEXT(large_text='Watcher ein', medium_text='Watc aus', small_text='w aus ')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Watcher si ', medium_text='Watch si', small_text='w si  ')
        if text_id == 'picowatcher_off':
            entxt = Dgt.DISPLAY_TEXT(large_text='Watcher off', medium_text='Watchoff', small_text='w  off')
            detxt = Dgt.DISPLAY_TEXT(large_text='Watcher aus', medium_text='Watchaus', small_text='w  aus')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Watcher no ', medium_text='Watch no', small_text='w no  ')
        if text_id == 'picocoach':
            entxt = Dgt.DISPLAY_TEXT(large_text='Pico Coach  ', medium_text='PCoach  ', small_text='Pcoach')
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'okpicocoach':
            entxt = Dgt.DISPLAY_TEXT(large_text='Coach ok   ', medium_text='Coach ok', small_text='c ok  ')
            detxt = Dgt.DISPLAY_TEXT(large_text='Coach ok   ', medium_text='Coach ok', small_text='c ok  ')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Coach ok   ', medium_text='Coach ok', small_text='c ok  ')
        if text_id == 'picocoach_on':
            entxt = Dgt.DISPLAY_TEXT(large_text='Coach on  ', medium_text='Coach on ', small_text='c on  ')
            detxt = Dgt.DISPLAY_TEXT(large_text='Coach ein ', medium_text='Coach ein', small_text='c ein ')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Coach si  ', medium_text='Coach si ', small_text='c si  ')
        if text_id == 'picocoach_off':
            entxt = Dgt.DISPLAY_TEXT(large_text='Coach off  ', medium_text='Coachoff', small_text='c  off')
            detxt = Dgt.DISPLAY_TEXT(large_text='Coach aus  ', medium_text='Coachaus', small_text='c  aus')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Coach no  ', medium_text='Coach  no', small_text='co  no')
        if text_id == 'okpicotutor':
            entxt = Dgt.DISPLAY_TEXT(large_text='PicTutor ok', medium_text='Tutor ok', small_text='tut ok')
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'picoexplorer':
            entxt = Dgt.DISPLAY_TEXT(large_text='Pico Explorer', medium_text='Explorer', small_text='explor')
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'picoexplorer_on':
            entxt = Dgt.DISPLAY_TEXT(large_text='Explorer on', medium_text='Expl on ', small_text='ex on ')
            detxt = Dgt.DISPLAY_TEXT(large_text='Explorer ein', medium_text='Expl ein', small_text='ex ein')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Explorer si', medium_text='Expl si ', small_text='ex si ')
        if text_id == 'picoexplorer_off':
            entxt = Dgt.DISPLAY_TEXT(large_text='Explorer off', medium_text='Expl off', small_text='ex off')
            detxt = Dgt.DISPLAY_TEXT(large_text='Explorer aus', medium_text='Expl aus', small_text='ex aus')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Explorer no', medium_text='Expl  no', small_text='exp no')
        if text_id == 'okpicoexplorer':
            entxt = Dgt.DISPLAY_TEXT(large_text='Explorer ok', medium_text='Expl ok ', small_text='exp ok')
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'position_fail':
            beep = False
            if 'clear' in msg:
                entxt = Dgt.DISPLAY_TEXT(large_text=msg, medium_text=msg, small_text=msg)
                text_de = 'Leere ' + msg[-2:]
                detxt = Dgt.DISPLAY_TEXT(large_text=text_de, medium_text=text_de, small_text=text_de)
                nltxt = entxt
                frtxt = entxt
                estxt = entxt
                ittxt = entxt
            elif 'put' in msg:
                piece = msg[4]
                if piece.islower():
                    piece_en = 'b ' + piece.upper()
                    if piece == 'q':
                        piece_de = 's ' + 'D'
                    elif piece == 'r':
                        piece_de = 's ' + 'T'
                    elif piece == 'b':
                        piece_de = 's ' + 'L'
                    elif piece == 'n':
                        piece_de = 's ' + 'S'
                    elif piece == 'p':
                        piece_de = 's ' + 'B'
                    elif piece == 'K':
                        piece_de = 's ' + 'K'
                    else:
                        piece_de = 's?'
                else:
                    piece_en = 'w ' + piece.upper()
                    if piece == 'Q':
                        piece_de = 'w ' + 'D'
                    elif piece == 'R':
                        piece_de = 'w ' + 'T'
                    elif piece == 'B':
                        piece_de = 'w ' + 'L'
                    elif piece == 'N':
                        piece_de = 'w ' + 'S'
                    elif piece == 'P':
                        piece_de = 'w ' + 'B'
                    elif piece == 'K':
                        piece_de = 'w ' + 'K'
                    else:
                        piece_de = 'w?'
                text_de_m = piece_de + msg[-2:]
                text_de = 'setze ' + text_de_m
                text_en_m = piece_en + msg[-2:]
                text_en = 'put ' + text_en_m
                entxt = Dgt.DISPLAY_TEXT(large_text=text_en, medium_text=text_en_m, small_text=text_en_m)
                detxt = Dgt.DISPLAY_TEXT(large_text=text_de, medium_text=text_de_m, small_text=text_de_m)
                nltxt = entxt
                frtxt = entxt
                estxt = entxt
                ittxt = entxt
        if text_id == 'picotutor_msg':
            if msg == 'POSOK':
                entxt = Dgt.DISPLAY_TEXT(large_text='Position ok', medium_text='Posit ok', small_text='POS ok')
                detxt = entxt
                nltxt = entxt
                frtxt = entxt
                estxt = entxt
                ittxt = entxt
            elif msg == 'ACTIVE':
                entxt = Dgt.DISPLAY_TEXT(large_text='Pico Tutor on', medium_text='Tutor on', small_text='tut.on')
                detxt = Dgt.DISPLAY_TEXT(large_text='Pico Tutor an', medium_text='Tutor an', small_text='tut.an')
                nltxt = entxt
                frtxt = entxt
                estxt = entxt
                ittxt = Dgt.DISPLAY_TEXT(large_text='Pico Tutor si', medium_text='Tutor si', small_text='tut.si')
            elif 'PICMATE' in msg:
                msg_list = msg.split('_')
                l_msg = 'Mate in ' + msg_list[1]
                m_msg = 'Mate ' + msg_list[1]
                s_msg = 'Mate' + msg_list[1]
                l_msgd = 'Matt in ' + msg_list[1]
                m_msgd = 'Matt ' + msg_list[1]
                s_msgd = 'Matt' + msg_list[1]
                entxt = Dgt.DISPLAY_TEXT(large_text=l_msg, medium_text=m_msg, small_text=s_msg)
                detxt = Dgt.DISPLAY_TEXT(large_text=l_msgd, medium_text=m_msgd, small_text=s_msgd)
                nltxt = entxt
                frtxt = entxt
                estxt = entxt
                ittxt = entxt
            elif 'USRMATE' in msg:
                msg_list = msg.split('_')
                l_msg = 'Mate in ' + msg_list[1]
                m_msg = 'Mate ' + msg_list[1]
                s_msg = 'Mate' + msg_list[1]
                l_msgd = 'Matt in ' + msg_list[1]
                m_msgd = 'Matt ' + msg_list[1]
                s_msgd = 'Matt' + msg_list[1]
                entxt = Dgt.DISPLAY_TEXT(large_text=l_msg, medium_text=m_msg, small_text=s_msg)
                detxt = Dgt.DISPLAY_TEXT(large_text=l_msgd, medium_text=m_msgd, small_text=s_msgd)
                nltxt = entxt
                frtxt = entxt
                estxt = entxt
                ittxt = entxt
            elif msg == 'ANALYSIS':
                entxt = Dgt.DISPLAY_TEXT(large_text='Pico Tutor', medium_text='PicTutor', small_text='PTutor')
                detxt = entxt
                nltxt = entxt
                frtxt = entxt
                estxt = entxt
                ittxt = entxt
            elif 'HINT' in msg:
                beep = False
                l_msg = 'hint ' + msg[4:]
                l_msg = l_msg.ljust(11, ' ')
                l_move_g = msg[4:]
                l_move_g = l_move_g.replace('N', 'S')
                l_move_g = l_move_g.replace('Q', 'D')
                l_move_g = l_move_g.replace('R', 'T')
                l_move_g = l_move_g.replace('B', 'L')
                l_move_g = l_move_g.replace('P', 'B')
                l_msg_g = 'Tipp ' + l_move_g
                l_msg_g = l_msg_g.ljust(11, ' ')
                m_move_g = msg[4:]
                m_move_g = l_move_g.replace('N', 'S')
                m_move_g = l_move_g.replace('Q', 'D')
                m_move_g = l_move_g.replace('R', 'T')
                m_move_g = l_move_g.replace('B', 'L')
                m_move_g = l_move_g.replace('P', 'B')
                if len(msg[4:]) > 4:
                    m_msg = 'hnt' + msg[4:]
                    m_msg_g = 'Tip' + m_move_g
                elif len(msg[4:]) > 3:
                    m_msg = 'hint' + msg[4:]
                    m_msg_g = 'Tipp' + m_move_g
                else:
                    m_msg = 'hint ' + msg[4:]
                    m_msg_g = 'Tipp ' + m_move_g
                m_msg = m_msg.ljust(8, ' ')
                m_msg_g = m_msg_g.ljust(8, ' ')
                entxt = Dgt.DISPLAY_TEXT(large_text=l_msg[:38], medium_text=m_msg[:8], small_text=m_msg[:6])
                detxt = Dgt.DISPLAY_TEXT(large_text=l_msg_g[:38], medium_text=m_msg_g[:8], small_text=m_msg_g[:6])
                nltxt = entxt
                frtxt = entxt
                estxt = entxt
                ittxt = entxt
            elif 'THREAT' in msg:
                beep = False
                if len(msg[6:]) > 4:
                    l_msg = 'threat' + msg[6:]
                    m_msg = 'tht' + msg[6:]
                elif len(msg[6:]) > 3:
                    l_msg = 'threat ' + msg[6:]
                    m_msg = 'thrt' + msg[6:]
                else:
                    l_msg = 'threat ' + msg[6:]
                    m_msg = 'thrt ' + msg[6:]
                l_msg = l_msg.ljust(11, ' ')
                m_msg = m_msg.ljust(8, ' ')
                l_move_g = msg[6:]
                l_move_g = l_move_g.replace('N', 'S')
                l_move_g = l_move_g.replace('Q', 'D')
                l_move_g = l_move_g.replace('R', 'T')
                l_move_g = l_move_g.replace('B', 'L')
                l_move_g = l_move_g.replace('P', 'B')
                m_move_g = msg[6:]
                m_move_g = l_move_g.replace('N', 'S')
                m_move_g = l_move_g.replace('Q', 'D')
                m_move_g = l_move_g.replace('R', 'T')
                m_move_g = l_move_g.replace('B', 'L')
                m_move_g = l_move_g.replace('P', 'B')
                if len(msg[6:]) > 5:
                    l_msg_g = 'droht' + l_move_g
                else:
                    l_msg_g = 'droht ' + l_move_g
                l_msg_g = l_msg_g.ljust(11, ' ')
                m_msg_g = m_move_g
                m_msg_g = m_msg_g.ljust(8, ' ')
                entxt = Dgt.DISPLAY_TEXT(large_text=l_msg[:38], medium_text=m_msg[:8], small_text=m_msg[:6])
                detxt = Dgt.DISPLAY_TEXT(large_text=l_msg_g[:38], medium_text=m_msg_g[:8], small_text=m_msg_g[:6])
                nltxt = entxt
                frtxt = entxt
                estxt = entxt
                ittxt = entxt
            elif 'BEST' in msg:
                beep = False
                l_msg = 'hint ' + msg[4:]
                l_msg = l_msg.ljust(11, ' ')
                l_move_g = msg[4:]
                l_move_g = l_move_g.replace('N', 'S')
                l_move_g = l_move_g.replace('Q', 'D')
                l_move_g = l_move_g.replace('R', 'T')
                l_move_g = l_move_g.replace('B', 'L')
                l_move_g = l_move_g.replace('P', 'B')
                l_msg_g = 'Tipp ' + l_move_g
                l_msg_g = l_msg_g.ljust(11, ' ')
                m_move_g = msg[4:]
                m_move_g = l_move_g.replace('N', 'S')
                m_move_g = l_move_g.replace('Q', 'D')
                m_move_g = l_move_g.replace('R', 'T')
                m_move_g = l_move_g.replace('B', 'L')
                m_move_g = l_move_g.replace('P', 'B')
                if len(msg[4:]) > 4:
                    m_msg = 'hnt' + msg[4:]
                    m_msg_g = 'Tip' + m_move_g
                elif len(msg[4:]) > 3:
                    m_msg = 'hint' + msg[4:]
                    m_msg_g = 'Tipp' + m_move_g
                else:
                    m_msg = 'hint ' + msg[4:]
                    m_msg_g = 'Tipp ' + m_move_g
                m_msg = m_msg.ljust(8, ' ')
                m_msg_g = m_msg_g.ljust(8, ' ')
                entxt = Dgt.DISPLAY_TEXT(large_text=l_msg[:38], medium_text=m_msg[:8], small_text=m_msg[:6])
                detxt = Dgt.DISPLAY_TEXT(large_text=l_msg_g[:38], medium_text=m_msg_g[:8], small_text=m_msg_g[:6])
                nltxt = entxt
                frtxt = entxt
                estxt = entxt
                ittxt = entxt
            elif 'POS' in msg:
                beep = False
                l_msg = 'eval ' + msg[3:]
                l_msg = l_msg.ljust(11, ' ')
                l_msg_de = 'Wert ' + msg[3:]
                l_msg_de = l_msg_de.ljust(11, ' ')
                m_msg = 'eval' + msg[3:]
                m_msg = m_msg.ljust(8, ' ')
                m_msg_de = 'Wert' + msg[3:]
                m_msg_de = m_msg_de.ljust(8, ' ')
                entxt = Dgt.DISPLAY_TEXT(large_text=l_msg[:38], medium_text=m_msg[:8], small_text=m_msg[:6])
                detxt = Dgt.DISPLAY_TEXT(large_text=l_msg_de[:38], medium_text=m_msg_de[:8], small_text=m_msg_de[:6])
                nltxt = entxt
                frtxt = entxt
                estxt = entxt
                ittxt = entxt
            else:
                l_msg = 'PicTutor ' + msg[:2]
                l_msg = l_msg.ljust(11, ' ')
                m_msg = 'Tutor ' + msg[:2]
                m_msg = m_msg.ljust(9, ' ')
                s_msg = 'Tut ' + msg[:2]
                s_msg = s_msg.ljust(6, ' ')
                entxt = Dgt.DISPLAY_TEXT(large_text=l_msg, medium_text=m_msg, small_text=s_msg)
                detxt = entxt
                nltxt = entxt
                frtxt = entxt
                estxt = entxt
                ittxt = entxt
        if text_id == 'login':
            entxt = Dgt.DISPLAY_TEXT(large_text='login...   ', medium_text='login...', small_text='login ')
            detxt = Dgt.DISPLAY_TEXT(large_text='login...   ', medium_text='login...', small_text='login ')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'serverfailed':
            entxt = Dgt.DISPLAY_TEXT(large_text='Server Error', medium_text='sevr err', small_text='serror')
            detxt = Dgt.DISPLAY_TEXT(large_text='Server Fehler', medium_text='ServFehl', small_text='sFehle')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'userfailed':
            entxt = Dgt.DISPLAY_TEXT(large_text='login error', medium_text='loginerr', small_text='lgerr ')
            detxt = Dgt.DISPLAY_TEXT(large_text='Login Fehler', medium_text='LoginFeh', small_text='LFehlr')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'noopponent':
            entxt = Dgt.DISPLAY_TEXT(large_text='no opponent', medium_text='no oppon', small_text='no opp')
            detxt = Dgt.DISPLAY_TEXT(large_text='kein Gegner', medium_text='kein Geg', small_text='k.Gegn')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='no avversar', medium_text='no avver', small_text='no avv')
        if text_id == 'newposition':
            entxt = Dgt.DISPLAY_TEXT(large_text='new Position', medium_text='newPosit', small_text='newPos')
            detxt = Dgt.DISPLAY_TEXT(large_text='neue Stellung', medium_text='neueStlg', small_text='neuStl')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='nuo Posizion', medium_text='nuoPosiz', small_text='nuoPos')
        if text_id == 'enginename':
            entxt = Dgt.DISPLAY_TEXT(large_text=msg, medium_text=msg[:8], small_text=msg[:6])
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'restoregame':
            entxt = Dgt.DISPLAY_TEXT(large_text='last game  ', medium_text='lastGame', small_text='l.game')
            detxt = Dgt.DISPLAY_TEXT(large_text='Letztes Spiel', medium_text='letSpiel', small_text='lSpiel')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Ult.Partita', medium_text='UltParti', small_text='u.part')
        if text_id == 'seeking':
            entxt = Dgt.DISPLAY_TEXT(large_text='seeking... ', medium_text='seeking ', small_text='seek..')
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'enginesetup':
            entxt = Dgt.DISPLAY_TEXT(large_text='Engine Setup', medium_text='EngSetup', small_text='setup ')
            detxt = Dgt.DISPLAY_TEXT(large_text='Engine Konfiguration', medium_text='Eng.konf', small_text='e.konf')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Conf.Motore', medium_text='ConfMoto', small_text='config')
        if text_id == 'moveretry':
            entxt = Dgt.DISPLAY_TEXT(large_text='wrong move ', medium_text='wrongMov', small_text='wrong')
            detxt = Dgt.DISPLAY_TEXT(large_text='falscher Zug', medium_text='falsch.Z', small_text='falsch')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='mossa errat', medium_text='mossErra', small_text='errat ')
        if text_id == 'movewrong':
            entxt = Dgt.DISPLAY_TEXT(large_text='wrong move ', medium_text='wrongMov', small_text='wrong ')
            detxt = Dgt.DISPLAY_TEXT(large_text='falscher Zug', medium_text='falsch.Z', small_text='falsch')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='mossa errat', medium_text='mossErra', small_text='errat ')
        if text_id == 'goodbye':
            entxt = Dgt.DISPLAY_TEXT(large_text='Good bye   ', medium_text='Good bye', small_text='bye   ')
            detxt = Dgt.DISPLAY_TEXT(large_text='Tschüss   ', medium_text='Tschuess', small_text='tschau')
            nltxt = Dgt.DISPLAY_TEXT(large_text='tot ziens  ', medium_text='totziens', small_text='dag   ')
            frtxt = Dgt.DISPLAY_TEXT(large_text='au revoir  ', medium_text='a plus  ', small_text='bye   ')
            estxt = Dgt.DISPLAY_TEXT(large_text='adios      ', medium_text='adios   ', small_text='adios ')
            ittxt = Dgt.DISPLAY_TEXT(large_text='arrivederci', medium_text='a presto', small_text='ciao  ')
        if text_id == 'pleasewait':
            entxt = Dgt.DISPLAY_TEXT(large_text='please wait', medium_text='pls wait', small_text='wait  ')
            detxt = Dgt.DISPLAY_TEXT(large_text='bitte warten', medium_text='warten  ', small_text='warten')
            nltxt = Dgt.DISPLAY_TEXT(large_text='wacht even ', medium_text='wachten ', small_text='wacht ')
            frtxt = Dgt.DISPLAY_TEXT(large_text='patientez  ', medium_text='patience', small_text='patien')
            estxt = Dgt.DISPLAY_TEXT(large_text='espere     ', medium_text='espere  ', small_text='espere')
            ittxt = Dgt.DISPLAY_TEXT(large_text='un momento ', medium_text='attendi ', small_text='attesa')
        if text_id == 'nomove':
            entxt = Dgt.DISPLAY_TEXT(large_text='no move    ', medium_text='no move ', small_text='nomove')
            detxt = Dgt.DISPLAY_TEXT(large_text='Kein Zug   ', medium_text='Kein Zug', small_text='kn zug')
            nltxt = Dgt.DISPLAY_TEXT(large_text='Geen zet   ', medium_text='Geen zet', small_text='gn zet')
            frtxt = Dgt.DISPLAY_TEXT(large_text='pas de mouv', medium_text='pas mvt ', small_text='pasmvt')
            estxt = Dgt.DISPLAY_TEXT(large_text='sin mov    ', medium_text='sin mov ', small_text='no mov')
            ittxt = Dgt.DISPLAY_TEXT(large_text='no mossa   ', medium_text='no mossa', small_text='nmossa')
        if text_id == 'wb':
            entxt = Dgt.DISPLAY_TEXT(large_text=' W       B ', medium_text=' W     B', small_text='wh  bl')
            detxt = Dgt.DISPLAY_TEXT(large_text=' W       S ', medium_text=' W     S', small_text='we  sc')
            nltxt = Dgt.DISPLAY_TEXT(large_text=' W       Z ', medium_text=' W     Z', small_text='wi  zw')
            frtxt = Dgt.DISPLAY_TEXT(large_text=' B       N ', medium_text=' B     N', small_text='bl  no')
            estxt = Dgt.DISPLAY_TEXT(large_text=' B       N ', medium_text=' B     N', small_text='bl  ne')
            ittxt = Dgt.DISPLAY_TEXT(large_text=' B       N ', medium_text=' B     N', small_text='bi  ne')
        if text_id == 'bw':
            entxt = Dgt.DISPLAY_TEXT(large_text=' B       W ', medium_text=' B     W', small_text='bl  wh')
            detxt = Dgt.DISPLAY_TEXT(large_text=' S       W ', medium_text=' S     W', small_text='sc  we')
            nltxt = Dgt.DISPLAY_TEXT(large_text=' Z       W ', medium_text=' Z     W', small_text='zw  wi')
            frtxt = Dgt.DISPLAY_TEXT(large_text=' N       B ', medium_text=' N     B', small_text='no  bl')
            estxt = Dgt.DISPLAY_TEXT(large_text=' N       B ', medium_text=' N     B', small_text='ne  bl')
            ittxt = Dgt.DISPLAY_TEXT(large_text=' N       B ', medium_text=' N     B', small_text='ne  bi')
        if text_id == '960no':
            entxt = Dgt.DISPLAY_TEXT(large_text='uci960 no  ', medium_text='960 no  ', small_text='960 no')
            detxt = Dgt.DISPLAY_TEXT(large_text='uci960 nein', medium_text='960 nein', small_text='960 nn')
            nltxt = Dgt.DISPLAY_TEXT(large_text='uci960 nee ', medium_text='960 nee ', small_text='960nee')
            frtxt = Dgt.DISPLAY_TEXT(large_text='uci960 non ', medium_text='960 non ', small_text='960non')
            estxt = Dgt.DISPLAY_TEXT(large_text='uci960 no  ', medium_text='960 no  ', small_text='960 no')
            ittxt = Dgt.DISPLAY_TEXT(large_text='uci960 no  ', medium_text='960 no  ', small_text='960 no')
        if text_id == '960yes':
            entxt = Dgt.DISPLAY_TEXT(large_text='uci960 yes ', medium_text='960 yes ', small_text='960yes')
            detxt = Dgt.DISPLAY_TEXT(large_text='uci960 ja  ', medium_text='960 ja  ', small_text='960 ja')
            nltxt = Dgt.DISPLAY_TEXT(large_text='uci960 ja  ', medium_text='960 ja  ', small_text='960 ja')
            frtxt = Dgt.DISPLAY_TEXT(large_text='uci960 oui ', medium_text='960 oui ', small_text='960oui')
            estxt = Dgt.DISPLAY_TEXT(large_text='uci960 si  ', medium_text='960 si  ', small_text='960 si')
            ittxt = Dgt.DISPLAY_TEXT(large_text='uci960 si  ', medium_text='960 si  ', small_text='960 si')
        if text_id == 'picochess':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(large_text='PicoChess ' + self.version, medium_text='pico ' + self.version, small_text='pic' + self.version)
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'nofunction':
            entxt = Dgt.DISPLAY_TEXT(large_text='no function', medium_text='no funct', small_text='nofunc')
            detxt = Dgt.DISPLAY_TEXT(large_text='Keine Funktion', medium_text='KeineFkt', small_text='kn fkt')
            nltxt = Dgt.DISPLAY_TEXT(large_text='Geenfunctie', medium_text='Geen fnc', small_text='gn fnc')
            frtxt = Dgt.DISPLAY_TEXT(large_text='no fonction', medium_text='no fonct', small_text='nofonc')
            estxt = Dgt.DISPLAY_TEXT(large_text='sin funcion', medium_text='sin func', small_text='nofunc')
            ittxt = Dgt.DISPLAY_TEXT(large_text='no funzione', medium_text='no funz ', small_text='nofunz')
        if text_id == 'erroreng':
            entxt = Dgt.DISPLAY_TEXT(large_text='err engine ', medium_text='err engn', small_text='erreng')
            detxt = Dgt.DISPLAY_TEXT(large_text='err engine ', medium_text='err engn', small_text='erreng')
            nltxt = Dgt.DISPLAY_TEXT(large_text='fout engine', medium_text='fout eng', small_text='e fout')
            frtxt = Dgt.DISPLAY_TEXT(large_text='err moteur ', medium_text='err mot ', small_text='errmot')
            estxt = Dgt.DISPLAY_TEXT(large_text='error motor', medium_text='err mot ', small_text='errmot')
            ittxt = Dgt.DISPLAY_TEXT(large_text='err motore ', medium_text='err moto', small_text='errmot')
        if text_id == 'okengine':
            entxt = Dgt.DISPLAY_TEXT(large_text='ok engine  ', medium_text='okengine', small_text='ok eng')
            detxt = Dgt.DISPLAY_TEXT(large_text='ok engine  ', medium_text='okengine', small_text='ok eng')
            nltxt = Dgt.DISPLAY_TEXT(large_text='ok engine  ', medium_text='okengine', small_text='ok eng')
            frtxt = Dgt.DISPLAY_TEXT(large_text='ok moteur  ', medium_text='ok mot  ', small_text='ok mot')
            estxt = Dgt.DISPLAY_TEXT(large_text='ok motor   ', medium_text='ok motor', small_text='ok mot')
            ittxt = Dgt.DISPLAY_TEXT(large_text='ok motore  ', medium_text='ok motor', small_text='ok mot')
        if text_id == 'okmode':
            entxt = Dgt.DISPLAY_TEXT(large_text='ok mode    ', medium_text='ok mode ', small_text='okmode')
            detxt = Dgt.DISPLAY_TEXT(large_text='ok Modus   ', medium_text='ok Modus', small_text='okmode')
            nltxt = Dgt.DISPLAY_TEXT(large_text='ok modus   ', medium_text='ok modus', small_text='okmode')
            frtxt = Dgt.DISPLAY_TEXT(large_text='ok mode    ', medium_text='ok mode ', small_text='okmode')
            estxt = Dgt.DISPLAY_TEXT(large_text='ok modo    ', medium_text='ok modo ', small_text='okmodo')
            ittxt = Dgt.DISPLAY_TEXT(large_text='ok modo    ', medium_text='ok modo ', small_text='okmodo')
        if text_id == 'okbook':
            entxt = Dgt.DISPLAY_TEXT(large_text='ok book    ', medium_text='ok book ', small_text='okbook')
            detxt = Dgt.DISPLAY_TEXT(large_text='ok Buch    ', medium_text='ok Buch ', small_text='okbuch')
            nltxt = Dgt.DISPLAY_TEXT(large_text='ok boek    ', medium_text='ok boek ', small_text='okboek')
            frtxt = Dgt.DISPLAY_TEXT(large_text='ok livre   ', medium_text='ok livre', small_text='ok liv')
            estxt = Dgt.DISPLAY_TEXT(large_text='ok libro   ', medium_text='ok libro', small_text='oklibr')
            ittxt = Dgt.DISPLAY_TEXT(large_text='ok libroape', medium_text='ok libro', small_text='oklibr')
        if text_id == 'noipadr':
            entxt = Dgt.DISPLAY_TEXT(large_text='no IP address ', medium_text='no IPadr', small_text='no ip ')
            detxt = Dgt.DISPLAY_TEXT(large_text='Keine IP Adresse', medium_text='Keine IP', small_text='kn ip ')
            nltxt = Dgt.DISPLAY_TEXT(large_text='Geen IPadr ', medium_text='Geen IP ', small_text='gn ip ')
            frtxt = Dgt.DISPLAY_TEXT(large_text='pas d IP   ', medium_text='pas d IP', small_text='pd ip ')
            estxt = Dgt.DISPLAY_TEXT(large_text='no IP dir  ', medium_text='no IP   ', small_text='no ip ')
            ittxt = Dgt.DISPLAY_TEXT(large_text='no indir ip', medium_text='no ip   ', small_text='no ip ')
        if text_id == 'exitmenu':
            entxt = Dgt.DISPLAY_TEXT(large_text='exit menu  ', medium_text='exitmenu', small_text='exit m')
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'errormenu':
            entxt = Dgt.DISPLAY_TEXT(large_text='error menu ', medium_text='err menu', small_text='errmen')
            detxt = Dgt.DISPLAY_TEXT(large_text='error Menu ', medium_text='err Menu', small_text='errmen')
            nltxt = Dgt.DISPLAY_TEXT(large_text='fout menu  ', medium_text='foutmenu', small_text='fout m')
            frtxt = Dgt.DISPLAY_TEXT(large_text='error menu ', medium_text='err menu', small_text='pd men')
            estxt = Dgt.DISPLAY_TEXT(large_text='error menu ', medium_text='err menu', small_text='errmen')
            ittxt = Dgt.DISPLAY_TEXT(large_text='errore menu', medium_text='err menu', small_text='errmen')
        if text_id == 'sidewhite':
            entxt = Dgt.DISPLAY_TEXT(large_text='side to move White', medium_text='side W  ', small_text='side w')
            detxt = Dgt.DISPLAY_TEXT(large_text='Weiß am Zug   ', medium_text='W am Zug', small_text=' w zug')
            nltxt = Dgt.DISPLAY_TEXT(large_text='wit aan zet', medium_text='wit zet ', small_text=' w zet')
            frtxt = Dgt.DISPLAY_TEXT(large_text='aux blancs ', medium_text='mvt bl  ', small_text='mvt bl')
            estxt = Dgt.DISPLAY_TEXT(large_text='lado blanco', medium_text='lado W  ', small_text='lado w')
            ittxt = Dgt.DISPLAY_TEXT(large_text='lato bianco', medium_text='lato b  ', small_text='lato b')
        if text_id == 'sideblack':
            entxt = Dgt.DISPLAY_TEXT(large_text='side to move Black', medium_text='side B  ', small_text='side b')
            detxt = Dgt.DISPLAY_TEXT(large_text='Schwarz am Zug   ', medium_text='S am Zug', small_text=' s zug')
            nltxt = Dgt.DISPLAY_TEXT(large_text='zw aan zet ', medium_text='zw zet  ', small_text=' z zet')
            frtxt = Dgt.DISPLAY_TEXT(large_text='aux noirs  ', medium_text='mvt n   ', small_text='mvt n ')
            estxt = Dgt.DISPLAY_TEXT(large_text='lado negro ', medium_text='lado B  ', small_text='lado b')
            ittxt = Dgt.DISPLAY_TEXT(large_text='lato nero  ', medium_text='lato n  ', small_text='lato n')
        if text_id == 'scanboard':
            entxt = Dgt.DISPLAY_TEXT(large_text='scan board ', medium_text='scan    ', small_text='scan  ')
            detxt = Dgt.DISPLAY_TEXT(large_text='lese Stellung', medium_text='lese Stl', small_text='lese s')
            nltxt = Dgt.DISPLAY_TEXT(large_text='scan bord  ', medium_text='scan    ', small_text='scan  ')
            frtxt = Dgt.DISPLAY_TEXT(large_text='scan echiq ', medium_text='scan    ', small_text='scan  ')
            estxt = Dgt.DISPLAY_TEXT(large_text='escan tabl ', medium_text='escan   ', small_text='escan ')
            ittxt = Dgt.DISPLAY_TEXT(large_text='scan scacch', medium_text='scan    ', small_text='scan  ')
        if text_id == 'illegalpos':
            entxt = Dgt.DISPLAY_TEXT(large_text='invalid position', medium_text='invalid ', small_text='badpos')
            detxt = Dgt.DISPLAY_TEXT(large_text='illegale Position', medium_text='illegal ', small_text='errpos')
            nltxt = Dgt.DISPLAY_TEXT(large_text='ongeldig   ', medium_text='ongeldig', small_text='ongeld')
            frtxt = Dgt.DISPLAY_TEXT(large_text='illegale   ', medium_text='illegale', small_text='pos il')
            estxt = Dgt.DISPLAY_TEXT(large_text='illegal pos', medium_text='ileg pos', small_text='errpos')
            ittxt = Dgt.DISPLAY_TEXT(large_text='pos illegal', medium_text='illegale', small_text='errpos')
        if text_id == 'error960':
            entxt = Dgt.DISPLAY_TEXT(large_text='err uci960 ', medium_text='err 960 ', small_text='err960')
            detxt = Dgt.DISPLAY_TEXT(large_text='err uci960 ', medium_text='err 960 ', small_text='err960')
            nltxt = Dgt.DISPLAY_TEXT(large_text='fout uci960', medium_text='fout 960', small_text='err960')
            frtxt = Dgt.DISPLAY_TEXT(large_text='err uci960 ', medium_text='err 960 ', small_text='err960')
            estxt = Dgt.DISPLAY_TEXT(large_text='err uci960 ', medium_text='err 960 ', small_text='err960')
            ittxt = Dgt.DISPLAY_TEXT(large_text='errore 960 ', medium_text='erro 960', small_text='err960')
        if text_id == 'oktime':
            entxt = Dgt.DISPLAY_TEXT(large_text='ok time    ', medium_text='ok time ', small_text='ok tim')
            detxt = Dgt.DISPLAY_TEXT(large_text='ok Zeit    ', medium_text='ok Zeit ', small_text='okzeit')
            nltxt = Dgt.DISPLAY_TEXT(large_text='ok tyd     ', medium_text='ok tyd  ', small_text='ok tyd')
            frtxt = Dgt.DISPLAY_TEXT(large_text='ok temps   ', medium_text='ok temps', small_text='ok tps')
            estxt = Dgt.DISPLAY_TEXT(large_text='ok tiempo  ', medium_text='okTiempo', small_text='ok tpo')
            ittxt = Dgt.DISPLAY_TEXT(large_text='ok tempo   ', medium_text='ok tempo', small_text='oktemp')
        if text_id == 'okbeep':
            entxt = Dgt.DISPLAY_TEXT(large_text='ok beep    ', medium_text='ok beep ', small_text='okbeep')
            detxt = Dgt.DISPLAY_TEXT(large_text='ok Töne   ', medium_text='ok Toene', small_text='ok ton')
            nltxt = Dgt.DISPLAY_TEXT(large_text='ok piep    ', medium_text='ok piep ', small_text='okpiep')
            frtxt = Dgt.DISPLAY_TEXT(large_text='ok sons    ', medium_text='ok sons ', small_text='oksons')
            estxt = Dgt.DISPLAY_TEXT(large_text='ok beep    ', medium_text='ok beep ', small_text='okbeep')
            ittxt = Dgt.DISPLAY_TEXT(large_text='ok beep    ', medium_text='ok beep ', small_text='okbeep')
        if text_id == 'okpico':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(large_text='ok pico    ', medium_text='ok pico ', small_text='okpico')
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'okuser':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(large_text='ok player  ', medium_text='okplayer', small_text='okplay')
            detxt = Dgt.DISPLAY_TEXT(large_text='ok Spieler ', medium_text='ok Splr ', small_text='oksplr')
            nltxt = Dgt.DISPLAY_TEXT(large_text='ok Speler  ', medium_text='okSpeler', small_text='oksplr')
            frtxt = Dgt.DISPLAY_TEXT(large_text='ok joueur  ', medium_text='okjoueur', small_text='ok jr ')
            estxt = Dgt.DISPLAY_TEXT(large_text='ok usuario ', medium_text='okusuari', small_text='okuser')
            ittxt = Dgt.DISPLAY_TEXT(large_text='ok utente  ', medium_text='ok utent', small_text='okuten')
        if text_id == 'okmove':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(large_text='ok move    ', medium_text='ok move ', small_text='okmove')
            detxt = Dgt.DISPLAY_TEXT(large_text='ok Zug     ', medium_text='ok Zug  ', small_text='ok zug')
            nltxt = Dgt.DISPLAY_TEXT(large_text='ok zet     ', medium_text='ok zet  ', small_text='ok zet')
            frtxt = Dgt.DISPLAY_TEXT(large_text='ok mouv    ', medium_text='ok mouv ', small_text='ok mvt')
            estxt = Dgt.DISPLAY_TEXT(large_text='ok jugada  ', medium_text='okjugada', small_text='ok jug')
            ittxt = Dgt.DISPLAY_TEXT(large_text='mossa ok   ', medium_text='mossa ok', small_text='ok mos')
        if text_id == 'altmove':
            entxt = Dgt.DISPLAY_TEXT(large_text='alternative move  ', medium_text='alt move', small_text='altmov')
            detxt = Dgt.DISPLAY_TEXT(large_text='altnativer Zug', medium_text='alt Zug ', small_text='altzug')
            nltxt = Dgt.DISPLAY_TEXT(large_text='andere zet ', medium_text='alt zet ', small_text='altzet')
            frtxt = Dgt.DISPLAY_TEXT(large_text='autre mouv ', medium_text='alt move', small_text='altmov')
            estxt = Dgt.DISPLAY_TEXT(large_text='altn jugada', medium_text='altjugad', small_text='altjug')
            ittxt = Dgt.DISPLAY_TEXT(large_text='mossa alter', medium_text='mossa al', small_text='mosalt')
        if text_id == 'newgame':
            wait = True  # in case of GAME_ENDS before, wait for "abort"
            entxt = Dgt.DISPLAY_TEXT(large_text='new Game   ', medium_text='new Game', small_text='newgam')
            detxt = Dgt.DISPLAY_TEXT(large_text='neues Spiel', medium_text='neuesSpl', small_text='neuspl')
            nltxt = Dgt.DISPLAY_TEXT(large_text='nieuw party', medium_text='nw party', small_text='nwpart')
            frtxt = Dgt.DISPLAY_TEXT(large_text='nvl partie ', medium_text='nvl part', small_text='newgam')
            estxt = Dgt.DISPLAY_TEXT(large_text='nuev partid', medium_text='nuevpart', small_text='nuepar')
            ittxt = Dgt.DISPLAY_TEXT(large_text='nuova parti', medium_text='nuo part', small_text='nuopar')
        if text_id == 'ucigame':
            wait = True
            msg = msg.rjust(3)
            entxt = Dgt.DISPLAY_TEXT(large_text='new Game' + msg, medium_text='Game ' + msg, small_text='gam' + msg)
            detxt = Dgt.DISPLAY_TEXT(large_text='neues Spiel' + msg, medium_text='Spiel' + msg, small_text='spl' + msg)
            nltxt = Dgt.DISPLAY_TEXT(large_text='nw party' + msg, medium_text='party' + msg, small_text='par' + msg)
            frtxt = Dgt.DISPLAY_TEXT(large_text='nvl part' + msg, medium_text='part ' + msg, small_text='gam' + msg)
            estxt = Dgt.DISPLAY_TEXT(large_text='partid  ' + msg, medium_text='part ' + msg, small_text='par' + msg)
            ittxt = Dgt.DISPLAY_TEXT(large_text='nuo part' + msg, medium_text='part ' + msg, small_text='par' + msg)
        if text_id == 'takeback':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(large_text='takeback   ', medium_text='takeback', small_text='takbak')
            detxt = Dgt.DISPLAY_TEXT(large_text='Rücknahme ', medium_text='Rcknahme', small_text='rueckn')
            nltxt = Dgt.DISPLAY_TEXT(large_text='zet terug  ', medium_text='zetterug', small_text='terug ')
            frtxt = Dgt.DISPLAY_TEXT(large_text='retour     ', medium_text='retour  ', small_text='retour')
            estxt = Dgt.DISPLAY_TEXT(large_text='retrocede  ', medium_text='atras   ', small_text='atras ')
            ittxt = Dgt.DISPLAY_TEXT(large_text='ritorna    ', medium_text='ritorna ', small_text='ritorn')
        if text_id == 'bookmove':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(large_text='book       ', medium_text='book    ', small_text='book  ')
            detxt = Dgt.DISPLAY_TEXT(large_text='Buch       ', medium_text='Buch    ', small_text='buch  ')
            nltxt = Dgt.DISPLAY_TEXT(large_text='boek       ', medium_text='boek    ', small_text='boek  ')
            frtxt = Dgt.DISPLAY_TEXT(large_text='livre      ', medium_text='livre   ', small_text='livre ')
            estxt = Dgt.DISPLAY_TEXT(large_text='libro      ', medium_text='libro   ', small_text='libro ')
            ittxt = Dgt.DISPLAY_TEXT(large_text='libro      ', medium_text='libro   ', small_text='libro ')
        if text_id == 'setpieces':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(large_text='set pieces ', medium_text='set pcs ', small_text='setpcs')
            detxt = Dgt.DISPLAY_TEXT(large_text='Stellung aufbauen', medium_text='aufbauen', small_text='aufbau')
            nltxt = Dgt.DISPLAY_TEXT(large_text='zet stukken', medium_text='zet stkn', small_text='zet st')
            frtxt = Dgt.DISPLAY_TEXT(large_text='placer pcs ', medium_text='set pcs ', small_text='setpcs')
            estxt = Dgt.DISPLAY_TEXT(large_text='hasta piez ', medium_text='hasta pz', small_text='hastap')
            ittxt = Dgt.DISPLAY_TEXT(large_text='sistema pez', medium_text='sistpezz', small_text='sispez')
        if text_id == 'errorjack':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(large_text='error jack ', medium_text='err jack', small_text='jack  ')
            detxt = Dgt.DISPLAY_TEXT(large_text='err Kabel  ', medium_text='errKabel', small_text='errkab')
            nltxt = Dgt.DISPLAY_TEXT(large_text='fout Kabel ', medium_text='errKabel', small_text='errkab')
            frtxt = Dgt.DISPLAY_TEXT(large_text='jack error ', medium_text='jack err', small_text='jack  ')
            estxt = Dgt.DISPLAY_TEXT(large_text='jack error ', medium_text='jack err', small_text='jack  ')
            ittxt = Dgt.DISPLAY_TEXT(large_text='errore jack', medium_text='err jack', small_text='jack  ')
        if text_id == 'errorroom':
            entxt = Dgt.DISPLAY_TEXT(large_text='error room ', medium_text='err room', small_text='noroom')
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'errormode':
            entxt = Dgt.DISPLAY_TEXT(large_text='error mode ', medium_text='err mode', small_text='errmod')
            detxt = Dgt.DISPLAY_TEXT(large_text='error Modus', medium_text='errModus', small_text='errmod')
            nltxt = Dgt.DISPLAY_TEXT(large_text='fout modus ', medium_text='fout mod', small_text='errmod')
            frtxt = Dgt.DISPLAY_TEXT(large_text='error mode ', medium_text='err mode', small_text='errmod')
            estxt = Dgt.DISPLAY_TEXT(large_text='error modo ', medium_text='err modo', small_text='errmod')
            ittxt = Dgt.DISPLAY_TEXT(large_text='errore modo', medium_text='err modo', small_text='errmod')
        if text_id == 'level':
            if msg.startswith('Elo@'):
                msg = str(int(msg[4:])).rjust(4)
                entxt = Dgt.DISPLAY_TEXT(large_text='Elo ' + msg, medium_text='Elo ' + msg, small_text='el' + msg)
                detxt = entxt
                nltxt = entxt
                frtxt = entxt
                estxt = entxt
                ittxt = entxt
            elif msg.startswith('Level@'):
                msg = str(int(msg[6:])).rjust(2)
                entxt = Dgt.DISPLAY_TEXT(large_text='level    ' + msg, medium_text='level ' + msg, small_text='lvl ' + msg)
                detxt = Dgt.DISPLAY_TEXT(large_text='Level    ' + msg, medium_text='Level ' + msg, small_text='stf ' + msg)
                nltxt = entxt
                frtxt = Dgt.DISPLAY_TEXT(large_text='niveau   ' + msg, medium_text='niveau' + msg, small_text='niv ' + msg)
                estxt = Dgt.DISPLAY_TEXT(large_text='nivel    ' + msg, medium_text='nivel ' + msg, small_text='nvl ' + msg)
                ittxt = Dgt.DISPLAY_TEXT(large_text='livello  ' + msg, medium_text='livel ' + msg, small_text='liv ' + msg)
            else:
                entxt = Dgt.DISPLAY_TEXT(large_text=msg, medium_text=msg[:8], small_text=msg[:6])
                detxt = entxt
                nltxt = entxt
                frtxt = entxt
                estxt = entxt
                ittxt = entxt
        if text_id == 'mate':
            entxt = Dgt.DISPLAY_TEXT(large_text='mate in ' + msg, medium_text='mate ' + msg, small_text='mat' + msg)
            detxt = Dgt.DISPLAY_TEXT(large_text='Matt in ' + msg, medium_text='Matt ' + msg, small_text='mat' + msg)
            nltxt = Dgt.DISPLAY_TEXT(large_text='mat in  ' + msg, medium_text='mat  ' + msg, small_text='mat' + msg)
            frtxt = Dgt.DISPLAY_TEXT(large_text='mat en  ' + msg, medium_text='mat  ' + msg, small_text='mat' + msg)
            estxt = Dgt.DISPLAY_TEXT(large_text='mate en ' + msg, medium_text='mate ' + msg, small_text='mat' + msg)
            ittxt = Dgt.DISPLAY_TEXT(large_text='matto in' + msg, medium_text='matto' + msg, small_text='mat' + msg)
        if text_id == 'score':
            text_s = 'no scr' if msg is None else str(msg).rjust(6)
            text_m = 'no score' if msg is None else str(msg).rjust(8)
            text_l = 'no score' if msg is None else str(msg).rjust(11)
            entxt = Dgt.DISPLAY_TEXT(large_text=text_l, medium_text=text_m, small_text=text_s)
            text_s = 'kein W' if msg is None else str(msg).rjust(6)
            text_m = 'keinWert' if msg is None else str(msg).rjust(8)
            text_l = 'kein Wert' if msg is None else str(msg).rjust(11)
            detxt = Dgt.DISPLAY_TEXT(large_text=text_l, medium_text=text_m, small_text=text_s)
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'top_mode_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Mode       ', medium_text='Mode    ', small_text='mode  ')
            detxt = Dgt.DISPLAY_TEXT(large_text='Modus      ', medium_text='Modus   ', small_text='modus ')
            nltxt = Dgt.DISPLAY_TEXT(large_text='Modus      ', medium_text='Modus   ', small_text='modus ')
            frtxt = Dgt.DISPLAY_TEXT(large_text='Mode       ', medium_text='Mode    ', small_text='mode  ')
            estxt = Dgt.DISPLAY_TEXT(large_text='Modo       ', medium_text='Modo    ', small_text='modo  ')
            ittxt = Dgt.DISPLAY_TEXT(large_text='Modo       ', medium_text='Modo    ', small_text='modo  ')
        if text_id == 'top_position_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Position   ', medium_text='Position', small_text='posit ')
            detxt = Dgt.DISPLAY_TEXT(large_text='Position   ', medium_text='Position', small_text='positn')
            nltxt = Dgt.DISPLAY_TEXT(large_text='Stelling   ', medium_text='Stelling', small_text='stelng')
            frtxt = Dgt.DISPLAY_TEXT(large_text='Position   ', medium_text='Position', small_text='posit ')
            estxt = Dgt.DISPLAY_TEXT(large_text='Posicion   ', medium_text='Posicion', small_text='posic ')
            ittxt = Dgt.DISPLAY_TEXT(large_text='Posizione  ', medium_text='Posizion', small_text='posizi')
        if text_id == 'top_time_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Time       ', medium_text='Time    ', small_text='time  ')
            detxt = Dgt.DISPLAY_TEXT(large_text='Zeit       ', medium_text='Zeit    ', small_text='zeit  ')
            nltxt = Dgt.DISPLAY_TEXT(large_text='Tyd        ', medium_text='Tyd     ', small_text='tyd   ')
            frtxt = Dgt.DISPLAY_TEXT(large_text='Temps      ', medium_text='Temps   ', small_text='temps ')
            estxt = Dgt.DISPLAY_TEXT(large_text='Tiempo     ', medium_text='Tiempo  ', small_text='tiempo')
            ittxt = Dgt.DISPLAY_TEXT(large_text='Tempo      ', medium_text='Tempo   ', small_text='tempo ')
        if text_id == 'top_book_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Book       ', medium_text='Book    ', small_text='book  ')
            detxt = Dgt.DISPLAY_TEXT(large_text='Buch       ', medium_text='Buch    ', small_text='buch  ')
            nltxt = Dgt.DISPLAY_TEXT(large_text='Boek       ', medium_text='Boek    ', small_text='boek  ')
            frtxt = Dgt.DISPLAY_TEXT(large_text='Livre      ', medium_text='Livre   ', small_text='livre ')
            estxt = Dgt.DISPLAY_TEXT(large_text='Libro      ', medium_text='Libro   ', small_text='libro ')
            ittxt = Dgt.DISPLAY_TEXT(large_text='Libro      ', medium_text='Libro   ', small_text='libro ')
        if text_id == 'top_engine_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Engine     ', medium_text='Engine  ', small_text='engine')
            detxt = Dgt.DISPLAY_TEXT(large_text='Engine     ', medium_text='Engine  ', small_text='engine')
            nltxt = Dgt.DISPLAY_TEXT(large_text='Engine     ', medium_text='Engine  ', small_text='engine')
            frtxt = Dgt.DISPLAY_TEXT(large_text='Moteur     ', medium_text='Moteur  ', small_text='moteur')
            estxt = Dgt.DISPLAY_TEXT(large_text='Motor      ', medium_text='Motor   ', small_text='motor ')
            ittxt = Dgt.DISPLAY_TEXT(large_text='Motore     ', medium_text='Motore  ', small_text='motore')
        if text_id == 'engine_menu_modern':
            entxt = Dgt.DISPLAY_TEXT(large_text='Modern Engines', medium_text='Modern  ', small_text='modern')
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'engine_menu_retro':
            entxt = Dgt.DISPLAY_TEXT(large_text='Retro Engines', medium_text='Retro   ', small_text='retro ')
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'engine_menu_favorites':
            entxt = Dgt.DISPLAY_TEXT(large_text='Favorites  ', medium_text='Favorite', small_text='favor.')
            detxt = Dgt.DISPLAY_TEXT(large_text='Favoriten  ', medium_text='Favorite', small_text='Favor.')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'top_system_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='System     ', medium_text='System  ', small_text='system')
            detxt = Dgt.DISPLAY_TEXT(large_text='System     ', medium_text='System  ', small_text='system')
            nltxt = Dgt.DISPLAY_TEXT(large_text='Systeem    ', medium_text='Systeem ', small_text='system')
            frtxt = Dgt.DISPLAY_TEXT(large_text='Systeme    ', medium_text='Systeme ', small_text='system')
            estxt = Dgt.DISPLAY_TEXT(large_text='Sistema    ', medium_text='Sistema ', small_text='sistem')
            ittxt = Dgt.DISPLAY_TEXT(large_text='Sistema    ', medium_text='Sistema ', small_text='sistem')
        if text_id == 'top_game_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Game SetUp ', medium_text='GameSet.', small_text='game  ')
            detxt = Dgt.DISPLAY_TEXT(large_text='Partie     ', medium_text='Partie  ', small_text='partie')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Partita    ', medium_text='Partita ', small_text='partit')
        if text_id == 'game_save_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Save Game  ', medium_text='SaveGame', small_text='save  ')
            detxt = Dgt.DISPLAY_TEXT(large_text='Speichern  ', medium_text='Sichern ', small_text='sicher')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Salva Parti', medium_text='SalvaPar', small_text='salva ')
        if text_id == 'game_save_game1':
            entxt = Dgt.DISPLAY_TEXT(large_text='Game 1     ', medium_text='Game 1  ', small_text='game 1')
            detxt = Dgt.DISPLAY_TEXT(large_text='Spiel 1    ', medium_text='Spiel 1 ', small_text='spiel1')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Partita 1  ', medium_text='Partita1', small_text='part 1')
        if text_id == 'game_save_game2':
            entxt = Dgt.DISPLAY_TEXT(large_text='Game 2     ', medium_text='Game 2  ', small_text='game 2')
            detxt = Dgt.DISPLAY_TEXT(large_text='Spiel 2    ', medium_text='Spiel 2 ', small_text='spiel2')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Partita 2  ', medium_text='Partita2', small_text='part 2')
        if text_id == 'game_save_game3':
            entxt = Dgt.DISPLAY_TEXT(large_text='Game 3     ', medium_text='Game 3  ', small_text='game 3')
            detxt = Dgt.DISPLAY_TEXT(large_text='Spiel 3    ', medium_text='Spiel 3 ', small_text='spiel3')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Partita 3  ', medium_text='Partita3', small_text='part 3')
        if text_id == 'oksavegame':
            entxt = Dgt.DISPLAY_TEXT(large_text='ok save    ', medium_text='ok save ', small_text='oksave')
            detxt = Dgt.DISPLAY_TEXT(large_text='ok sichern ', medium_text='ok sich ', small_text='oksich')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='ok salva   ', medium_text='ok salva', small_text='oksalv')
        if text_id == 'game_read_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Read Game  ', medium_text='ReadGame', small_text='read  ')
            detxt = Dgt.DISPLAY_TEXT(large_text='Einlesen   ', medium_text='Einlesen', small_text='lesen ')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Leggi Parti', medium_text='LeggiPar', small_text='leggip')
        if text_id == 'game_read_gamelast':
            entxt = Dgt.DISPLAY_TEXT(large_text='last Game  ', medium_text='last Game', small_text='Lgame')
            detxt = Dgt.DISPLAY_TEXT(large_text='Letzte Partie', medium_text='letztPart', small_text='letzt')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Ult Partita', medium_text='ult Parti', small_text='Upart')
        if text_id == 'game_read_game1':
            entxt = Dgt.DISPLAY_TEXT(large_text='Game 1     ', medium_text='Game 1  ', small_text='game 1')
            detxt = Dgt.DISPLAY_TEXT(large_text='Spiel 1    ', medium_text='Spiel 1 ', small_text='spiel1')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Partita 1  ', medium_text='Partita1', small_text='part 1')
        if text_id == 'game_read_game2':
            entxt = Dgt.DISPLAY_TEXT(large_text='Game 2     ', medium_text='Game 2  ', small_text='game 2')
            detxt = Dgt.DISPLAY_TEXT(large_text='Spiel 2    ', medium_text='Spiel 2 ', small_text='spiel2')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Partita 2  ', medium_text='Partita2', small_text='part 2')
        if text_id == 'game_read_game3':
            entxt = Dgt.DISPLAY_TEXT(large_text='Game 3     ', medium_text='Game 3  ', small_text='game 3')
            detxt = Dgt.DISPLAY_TEXT(large_text='Spiel 3    ', medium_text='Spiel 3 ', small_text='spiel3')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Partita 3  ', medium_text='Partita3', small_text='part 3')
        if text_id == 'okreadgame':
            entxt = Dgt.DISPLAY_TEXT(large_text='ok read    ', medium_text='ok read ', small_text='okread')
            detxt = Dgt.DISPLAY_TEXT(large_text='ok lesen   ', medium_text='ok lesen', small_text='ok les')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='ok leggiPar', medium_text='ok leggi', small_text='oklegg')
        if text_id == 'game_altmove_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Alternative Move', medium_text='Alt.Move', small_text='altmov')
            detxt = Dgt.DISPLAY_TEXT(large_text='Alternativer Zug ', medium_text='Alt. Zug', small_text='altzug')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='MossaAltern', medium_text='MossaAlt', small_text='mosalt')
        if text_id == 'game_altmove_on':
            entxt = Dgt.DISPLAY_TEXT(large_text='Alternative Move on', medium_text='AltMovon', small_text='amovon')
            detxt = Dgt.DISPLAY_TEXT(large_text='Alternativer Zug ein', medium_text='a.Zugein', small_text='azugan')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Mos.Alt. si', medium_text='MosAltsi', small_text='moalsi')
        if text_id == 'game_altmove_off':
            entxt = Dgt.DISPLAY_TEXT(large_text='Alternative Move off', medium_text='AltMooff', small_text='amvoff')
            detxt = Dgt.DISPLAY_TEXT(large_text='Alternativer Zug aus', medium_text='a.Zugaus', small_text='azgaus')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Mos.Alt. no', medium_text='MosAltno', small_text='moalno')
        if text_id == 'okaltmove':
            entxt = Dgt.DISPLAY_TEXT(large_text='Alt.Move ok', medium_text='AltMovok', small_text='amv ok')
            detxt = Dgt.DISPLAY_TEXT(large_text='Alt.Zug  ok', medium_text='a.Zug ok', small_text='azg ok')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Mos.Alt. ok', medium_text='MosAltok', small_text='moalok')
        if text_id == 'game_contlast_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Continue Game  ', medium_text='contGame', small_text='contgm')
            detxt = Dgt.DISPLAY_TEXT(large_text='Fortsetzen ', medium_text='fortsetz', small_text='fortse')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Cont.Partit', medium_text='contPart', small_text='contpa')
        if text_id == 'game_contlast_on':
            entxt = Dgt.DISPLAY_TEXT(large_text='Continue Game on', medium_text='Cont.on ', small_text='con.on')
            detxt = Dgt.DISPLAY_TEXT(large_text='Fortsetzen ein', medium_text='fort.ein', small_text='frt an')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Cont.Par.si', medium_text='conParsi', small_text='copasi')
        if text_id == 'game_contlast_off':
            entxt = Dgt.DISPLAY_TEXT(large_text='Continue Game off', medium_text='Cont.off', small_text='conoff')
            detxt = Dgt.DISPLAY_TEXT(large_text='Fortsetzen aus', medium_text='fort.aus', small_text='frtaus')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Cont.Par.no', medium_text='conParno', small_text='copano')
        if text_id == 'okcontlast':
            entxt = Dgt.DISPLAY_TEXT(large_text='Continue Game ok', medium_text='Cont. ok', small_text='contok')
            detxt = Dgt.DISPLAY_TEXT(large_text='Fortsetzen ok', medium_text='Cont. ok', small_text='contok')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Cont.Par.ok', medium_text='conParok', small_text='copaok')
        if text_id == 'top_picotutor_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Pico Tutor  ', medium_text='PicTutor', small_text='tutor ')
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'picotutor_picowatcher_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Pico Watcher', medium_text='PicWatch', small_text='watch ')
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'picotutor_picocoach_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Pico Coach  ', medium_text='PicCoach', small_text='coach ')
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'picotutor_picoexplorer_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Pico Explorer', medium_text='Explorer', small_text='explor')
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'picotutor_picocomment_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Pico Comments', medium_text='Comment ', small_text='commnt')
            detxt = Dgt.DISPLAY_TEXT(large_text='Pico Kommentare', medium_text='Komment ', small_text='Kommnt')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'picocomment':
            entxt = Dgt.DISPLAY_TEXT(large_text='Pico Comments', medium_text='Comment ', small_text='commnt')
            detxt = Dgt.DISPLAY_TEXT(large_text='Pico Kommentare', medium_text='Komment ', small_text='Kommnt')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'picocomment_off':
            entxt = Dgt.DISPLAY_TEXT(large_text='all off    ', medium_text='all off ', small_text='alloff')
            detxt = Dgt.DISPLAY_TEXT(large_text='alle aus   ', medium_text='alle aus', small_text='aus   ')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='tutto  off ', medium_text='tutt off', small_text='tutoff')
        if text_id == 'picocomment_on_eng':
            entxt = Dgt.DISPLAY_TEXT(large_text='single on ', medium_text='singleOn', small_text='singleon')
            detxt = Dgt.DISPLAY_TEXT(large_text='einzel an ', medium_text='einzelAn', small_text='einzelan')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='singolo on', medium_text='singleOn', small_text='singleon')
        if text_id == 'picocomment_on_all':
            entxt = Dgt.DISPLAY_TEXT(large_text='all on     ', medium_text='all on  ', small_text='all on')
            detxt = Dgt.DISPLAY_TEXT(large_text='alle an    ', medium_text='alle an ', small_text='alleAn')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='tutto   on ', medium_text='tutto on', small_text='tutton')
        if text_id == 'mode_normal_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Normal     ', medium_text='Normal  ', small_text='normal')
            detxt = Dgt.DISPLAY_TEXT(large_text='Normal     ', medium_text='Normal  ', small_text='normal')
            nltxt = Dgt.DISPLAY_TEXT(large_text='Normaal    ', medium_text='Normaal ', small_text='normal')
            frtxt = Dgt.DISPLAY_TEXT(large_text='Normal     ', medium_text='Normal  ', small_text='normal')
            estxt = Dgt.DISPLAY_TEXT(large_text='Normal     ', medium_text='Normal  ', small_text='normal')
            ittxt = Dgt.DISPLAY_TEXT(large_text='Normale    ', medium_text='Normale ', small_text='normal')
        if text_id == 'mode_training_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Training   ', medium_text='Training', small_text='train')
            detxt = Dgt.DISPLAY_TEXT(large_text='Training   ', medium_text='Training', small_text='train')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'mode_brain_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Ponder on  ', medium_text='PonderOn', small_text='ponder')
            detxt = Dgt.DISPLAY_TEXT(large_text='Ponder an  ', medium_text='PonderAn', small_text='ponder')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'mode_analysis_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Move hint  ', medium_text='MoveHint', small_text='mvhint')
            detxt = Dgt.DISPLAY_TEXT(large_text='Zugvorschlag ', medium_text='ZugVor. ', small_text='zugvor')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Suggeriment', medium_text='Suggerim', small_text='sugger')
        if text_id == 'mode_kibitz_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Evaluation Score ', medium_text='Score   ', small_text='score ')
            detxt = Dgt.DISPLAY_TEXT(large_text='Bewertung  ', medium_text='Bewert. ', small_text='bewert')
            nltxt = entxt
            frtxt = Dgt.DISPLAY_TEXT(large_text='Evaluer    ', medium_text='Evaluer ', small_text='evalue')
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Valutazione', medium_text='Valutazi', small_text='valuta')
        if text_id == 'mode_observe_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Observe    ', medium_text='Observe ', small_text='observ')
            detxt = Dgt.DISPLAY_TEXT(large_text='Beobachten ', medium_text='Beobacht', small_text='beob. ')
            nltxt = Dgt.DISPLAY_TEXT(large_text='Observeren ', medium_text='Observr ', small_text='observ')
            frtxt = Dgt.DISPLAY_TEXT(large_text='Observer   ', medium_text='Observer', small_text='observ')
            estxt = Dgt.DISPLAY_TEXT(large_text='Observa    ', medium_text='Observa ', small_text='observ')
            ittxt = Dgt.DISPLAY_TEXT(large_text='Osserva    ', medium_text='Osserva ', small_text='osserv')
        if text_id == 'mode_remote_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Remote     ', medium_text='Remote  ', small_text='remote')
            detxt = Dgt.DISPLAY_TEXT(large_text='Remote     ', medium_text='Remote  ', small_text='remote')
            nltxt = Dgt.DISPLAY_TEXT(large_text='Remote     ', medium_text='Remote  ', small_text='remote')
            frtxt = Dgt.DISPLAY_TEXT(large_text='Remote     ', medium_text='Remote  ', small_text='remote')
            estxt = Dgt.DISPLAY_TEXT(large_text='Remoto     ', medium_text='Remoto  ', small_text='remoto')
            ittxt = Dgt.DISPLAY_TEXT(large_text='Remoto     ', medium_text='Remoto  ', small_text='remoto')
        if text_id == 'mode_ponder_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Analysis   ', medium_text='Analysis', small_text='analys')
            detxt = Dgt.DISPLAY_TEXT(large_text='Analyse    ', medium_text='Analyse ', small_text='analys')
            nltxt = Dgt.DISPLAY_TEXT(large_text='Analyseren ', medium_text='Analyse ', small_text='analys')
            frtxt = Dgt.DISPLAY_TEXT(large_text='Analyser   ', medium_text='Analyser', small_text='analys')
            estxt = Dgt.DISPLAY_TEXT(large_text='Analisis   ', medium_text='Analisis', small_text='analis')
            ittxt = Dgt.DISPLAY_TEXT(large_text='Analisi    ', medium_text='Analisi ', small_text='Analis')
        if text_id == 'timemode_fixed_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Move time  ', medium_text='Movetime', small_text='move t')
            detxt = Dgt.DISPLAY_TEXT(large_text='Zeit pro Zug ', medium_text='Zugzeit ', small_text='zug z ')
            nltxt = Dgt.DISPLAY_TEXT(large_text='Zet tyd    ', medium_text='Zet tyd ', small_text='zet   ')
            frtxt = Dgt.DISPLAY_TEXT(large_text='Mouv temps ', medium_text='Mouv tem', small_text='mouv  ')
            estxt = Dgt.DISPLAY_TEXT(large_text='Mov tiempo ', medium_text='mov tiem', small_text='mov   ')
            ittxt = Dgt.DISPLAY_TEXT(large_text='Mossa tempo', medium_text='Mosstemp', small_text='mostem')
        if text_id == 'timemode_blitz_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Game time  ', medium_text='Gametime', small_text='game t')
            detxt = Dgt.DISPLAY_TEXT(large_text='Spielzeit pro Partie  ', medium_text='Spielz  ', small_text='spielz')
            nltxt = Dgt.DISPLAY_TEXT(large_text='Spel tyd   ', medium_text='Spel tyd', small_text='spel  ')
            frtxt = Dgt.DISPLAY_TEXT(large_text='Partie temp', medium_text='Partie  ', small_text='partie')
            estxt = Dgt.DISPLAY_TEXT(large_text='Partid     ', medium_text='Partid  ', small_text='partid')
            ittxt = Dgt.DISPLAY_TEXT(large_text='Game tempo ', medium_text='Gametemp', small_text='gamtem')
        if text_id == 'timemode_fischer_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Fischer    ', medium_text='Fischer ', small_text='fischr')
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'timemode_tourn_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Tournament Levels', medium_text='Tournamnt', small_text='tourn ')
            detxt = Dgt.DISPLAY_TEXT(large_text='Turnierstufen', medium_text='Turnier  ', small_text='turnr ')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='LiveTorneo', medium_text='LivTorneo', small_text='torneo')
        if text_id == 'timemode_depth_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='SearchDepth', medium_text='Depth   ', small_text='Depth ')
            detxt = Dgt.DISPLAY_TEXT(large_text='Suchtiefe  ', medium_text='Suchtief', small_text='tiefe ')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Profondita ', medium_text='Profondi', small_text='profon')
        if text_id == 'info_version_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Version    ', medium_text='Version ', small_text='vers  ')
            detxt = Dgt.DISPLAY_TEXT(large_text='Version    ', medium_text='Version ', small_text='vers  ')
            nltxt = Dgt.DISPLAY_TEXT(large_text='Versie     ', medium_text='Versie  ', small_text='versie')
            frtxt = Dgt.DISPLAY_TEXT(large_text='Version    ', medium_text='Version ', small_text='vers  ')
            estxt = Dgt.DISPLAY_TEXT(large_text='Version    ', medium_text='Version ', small_text='vers  ')
            ittxt = Dgt.DISPLAY_TEXT(large_text='Versione   ', medium_text='Versione', small_text='versio')
        if text_id == 'info_ipadr_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='IP adress show ', medium_text='IP adr  ', small_text='ip adr')
            detxt = Dgt.DISPLAY_TEXT(large_text='IP Adresse anzeigen', medium_text='IP adr  ', small_text='ip adr')
            nltxt = Dgt.DISPLAY_TEXT(large_text='IP address ', medium_text='IP adr  ', small_text='ip adr')
            frtxt = Dgt.DISPLAY_TEXT(large_text='Adr IP     ', medium_text='Adr IP  ', small_text='adr ip')
            estxt = Dgt.DISPLAY_TEXT(large_text='IP dir     ', medium_text='IP dir  ', small_text='ip dir')
            ittxt = Dgt.DISPLAY_TEXT(large_text='ind IP     ', medium_text='ind IP  ', small_text='ind ip')
        if text_id == 'info_battery_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='BT battery status', medium_text='Battery ', small_text='bt bat')
            detxt = Dgt.DISPLAY_TEXT(large_text='BT Ladezustand', medium_text='Batterie', small_text='bt bat')
            nltxt = Dgt.DISPLAY_TEXT(large_text='BT batterij', medium_text='batterij', small_text='bt bat')
            frtxt = Dgt.DISPLAY_TEXT(large_text='BT batterie', medium_text='batterie', small_text='bt bat')
            estxt = Dgt.DISPLAY_TEXT(large_text='BT bateria ', medium_text='bateria ', small_text='bt bat')
            ittxt = Dgt.DISPLAY_TEXT(large_text='BT batteria', medium_text='batteria', small_text='bt bat')
        if text_id == 'system_sound_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Sound      ', medium_text='Sound   ', small_text='sound ')
            detxt = Dgt.DISPLAY_TEXT(large_text='Töne      ', medium_text='Toene   ', small_text='toene ')
            nltxt = Dgt.DISPLAY_TEXT(large_text='Geluid     ', medium_text='Geluid  ', small_text='geluid')
            frtxt = Dgt.DISPLAY_TEXT(large_text='Sons       ', medium_text='Sons    ', small_text='sons  ')
            estxt = Dgt.DISPLAY_TEXT(large_text='Sonido     ', medium_text='Sonido  ', small_text='sonido')
            ittxt = Dgt.DISPLAY_TEXT(large_text='Suoni      ', medium_text='Suoni   ', small_text='suoni ')
        if text_id == 'system_language_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Language   ', medium_text='Language', small_text='lang  ')
            detxt = Dgt.DISPLAY_TEXT(large_text='Sprache    ', medium_text='Sprache ', small_text='sprach')
            nltxt = Dgt.DISPLAY_TEXT(large_text='Taal       ', medium_text='Taal    ', small_text='taal  ')
            frtxt = Dgt.DISPLAY_TEXT(large_text='Langue     ', medium_text='Langue  ', small_text='langue')
            estxt = Dgt.DISPLAY_TEXT(large_text='Idioma     ', medium_text='Idioma  ', small_text='idioma')
            ittxt = Dgt.DISPLAY_TEXT(large_text='Lingua     ', medium_text='Lingua  ', small_text='lingua')
        if text_id == 'system_logfile_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Log file   ', medium_text='Log file', small_text='logfil')
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'system_info_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Information', medium_text='Informat', small_text='inform')
            detxt = Dgt.DISPLAY_TEXT(large_text='Information', medium_text='Informat', small_text='inform')
            nltxt = Dgt.DISPLAY_TEXT(large_text='Informatie ', medium_text='Informat', small_text='inform')
            frtxt = Dgt.DISPLAY_TEXT(large_text='Information', medium_text='Informat', small_text='inform')
            estxt = Dgt.DISPLAY_TEXT(large_text='Informacion', medium_text='Informac', small_text='inform')
            ittxt = Dgt.DISPLAY_TEXT(large_text='Informazion', medium_text='Informaz', small_text='inform')
        if text_id == 'system_voice_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Voice      ', medium_text='Voice   ', small_text='voice ')
            detxt = Dgt.DISPLAY_TEXT(large_text='Stimme     ', medium_text='Stimme  ', small_text='stimme')
            nltxt = Dgt.DISPLAY_TEXT(large_text='Stem       ', medium_text='Stem    ', small_text='stem  ')
            frtxt = Dgt.DISPLAY_TEXT(large_text='Voix       ', medium_text='Voix    ', small_text='voix  ')
            estxt = Dgt.DISPLAY_TEXT(large_text='Voz        ', medium_text='Voz     ', small_text='voz   ')
            ittxt = Dgt.DISPLAY_TEXT(large_text='Voce       ', medium_text='Voce    ', small_text='voce  ')
        if text_id == 'system_display_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Display    ', medium_text='Display ', small_text='dsplay')
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'system_eboard_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='E-Board    ', medium_text='E-Board ', small_text='eboard')
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'eboard_dgt_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='DGT        ', medium_text='DGT     ', small_text='dgt   ')
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'eboard_certabo_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Certabo    ', medium_text='Certabo ', small_text='certab')
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'eboard_chesslink_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='ChessLink  ', medium_text='ChessLnk', small_text='cheslk')
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'eboard_chessnut_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Chessnut   ', medium_text='Chessnut', small_text='chesnt')
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'gameresult_mate':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(large_text='Checkmate  ', medium_text='mate    ', small_text='mate  ')
            detxt = Dgt.DISPLAY_TEXT(large_text='Schachmatt ', medium_text='Matt    ', small_text='matt  ')
            nltxt = Dgt.DISPLAY_TEXT(large_text='mat        ', medium_text='mat     ', small_text='mat   ')
            frtxt = Dgt.DISPLAY_TEXT(large_text='mat        ', medium_text='mat     ', small_text='mat   ')
            estxt = Dgt.DISPLAY_TEXT(large_text='mate       ', medium_text='mate    ', small_text='mate  ')
            ittxt = Dgt.DISPLAY_TEXT(large_text='matto      ', medium_text='matto   ', small_text='matto ')
        if text_id == 'gameresult_stalemate':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(large_text='Stalemate  ', medium_text='stalemat', small_text='stale ')
            detxt = Dgt.DISPLAY_TEXT(large_text='Patt       ', medium_text='Patt    ', small_text='patt  ')
            nltxt = Dgt.DISPLAY_TEXT(large_text='patstelling', medium_text='pat     ', small_text='pat   ')
            frtxt = Dgt.DISPLAY_TEXT(large_text='pat        ', medium_text='pat     ', small_text='pat   ')
            estxt = Dgt.DISPLAY_TEXT(large_text='ahogado    ', medium_text='ahogado ', small_text='ahogad')
            ittxt = Dgt.DISPLAY_TEXT(large_text='stallo     ', medium_text='stallo  ', small_text='stallo')
        if text_id == 'gameresult_time':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(large_text='Time       ', medium_text='time    ', small_text='time  ')
            detxt = Dgt.DISPLAY_TEXT(large_text='Zeit       ', medium_text='Zeit    ', small_text='zeit  ')
            nltxt = Dgt.DISPLAY_TEXT(large_text='tyd        ', medium_text='tyd     ', small_text='tyd   ')
            frtxt = Dgt.DISPLAY_TEXT(large_text='tombe      ', medium_text='tombe   ', small_text='tombe ')
            estxt = Dgt.DISPLAY_TEXT(large_text='tiempo     ', medium_text='tiempo  ', small_text='tiempo')
            ittxt = Dgt.DISPLAY_TEXT(large_text='tempo      ', medium_text='tempo   ', small_text='tempo ')
        if text_id == 'gameresult_material':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(large_text='Material   ', medium_text='material', small_text='materi')
            detxt = Dgt.DISPLAY_TEXT(large_text='Material   ', medium_text='Material', small_text='materi')
            nltxt = Dgt.DISPLAY_TEXT(large_text='materiaal  ', medium_text='material', small_text='materi')
            frtxt = Dgt.DISPLAY_TEXT(large_text='materiel   ', medium_text='materiel', small_text='materl')
            estxt = Dgt.DISPLAY_TEXT(large_text='material   ', medium_text='material', small_text='mater ')
            ittxt = Dgt.DISPLAY_TEXT(large_text='materiale  ', medium_text='material', small_text='materi')
        if text_id == 'gameresult_moves':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(large_text='75 moves   ', medium_text='75 moves', small_text='75 mov')
            detxt = Dgt.DISPLAY_TEXT(large_text='75 Züge    ', medium_text='75 Zuege', small_text='75 zug')
            nltxt = Dgt.DISPLAY_TEXT(large_text='75 zetten  ', medium_text='75zetten', small_text='75 zet')
            frtxt = Dgt.DISPLAY_TEXT(large_text='75 mouv    ', medium_text='75 mouv ', small_text='75 mvt')
            estxt = Dgt.DISPLAY_TEXT(large_text='75 mov     ', medium_text='75 mov  ', small_text='75 mov')
            ittxt = Dgt.DISPLAY_TEXT(large_text='75 mosse   ', medium_text='75 mosse', small_text='75 mos')
        if text_id == 'gameresult_repetition':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(large_text='Threefold repetition ', medium_text='rep pos ', small_text='reppos')
            detxt = Dgt.DISPLAY_TEXT(large_text='3fache Stellungswiederholung ', medium_text='Wiederhg', small_text='wdrhlg')
            nltxt = Dgt.DISPLAY_TEXT(large_text='zetherhalin', medium_text='herhalin', small_text='herhal')
            frtxt = Dgt.DISPLAY_TEXT(large_text='3ieme rep  ', medium_text='3iem rep', small_text=' 3 rep')
            estxt = Dgt.DISPLAY_TEXT(large_text='repeticion ', medium_text='repite 3', small_text='rep 3 ')
            ittxt = Dgt.DISPLAY_TEXT(large_text='3 ripetiz  ', medium_text='3 ripeti', small_text='3 ripe')
        if text_id == 'gameresult_abort':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(large_text='abort game ', medium_text='abort   ', small_text='abort ')
            detxt = Dgt.DISPLAY_TEXT(large_text='Spielabbruch', medium_text='Abbruch ', small_text='abbrch')
            nltxt = Dgt.DISPLAY_TEXT(large_text='afbreken   ', medium_text='afbreken', small_text='afbrek')
            frtxt = Dgt.DISPLAY_TEXT(large_text='sortir     ', medium_text='sortir  ', small_text='sortir')
            estxt = Dgt.DISPLAY_TEXT(large_text='abortar    ', medium_text='abortar ', small_text='abort ')
            ittxt = Dgt.DISPLAY_TEXT(large_text='interrompi ', medium_text='interrom', small_text='interr')
        if text_id == 'gameresult_white':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(large_text='White wins ', medium_text='W wins  ', small_text='w wins')
            detxt = Dgt.DISPLAY_TEXT(large_text='Weiß gewinnt ', medium_text='W Gewinn', small_text=' w gew')
            nltxt = Dgt.DISPLAY_TEXT(large_text='wit wint   ', medium_text='wit wint', small_text='w wint')
            frtxt = Dgt.DISPLAY_TEXT(large_text='B gagne    ', medium_text='B gagne ', small_text='b gagn')
            estxt = Dgt.DISPLAY_TEXT(large_text='B ganan    ', medium_text='B ganan ', small_text='b gana')
            ittxt = Dgt.DISPLAY_TEXT(large_text='B vince    ', medium_text='B vince ', small_text='b vinc')
        if text_id == 'gameresult_black':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(large_text='Black wins ', medium_text='B wins  ', small_text='b wins')
            detxt = Dgt.DISPLAY_TEXT(large_text='Schwarz gewinnt', medium_text='S Gewinn', small_text=' s gew')
            nltxt = Dgt.DISPLAY_TEXT(large_text='zwart wint ', medium_text='zw wint ', small_text='z wint')
            frtxt = Dgt.DISPLAY_TEXT(large_text='N gagne    ', medium_text='N gagne ', small_text='n gagn')
            estxt = Dgt.DISPLAY_TEXT(large_text='N ganan    ', medium_text='N ganan ', small_text='n gana')
            ittxt = Dgt.DISPLAY_TEXT(large_text='N vince    ', medium_text='N vince ', small_text='n vinc')
        if text_id == 'gameresult_draw':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(large_text='draw       ', medium_text='draw    ', small_text='draw  ')
            detxt = Dgt.DISPLAY_TEXT(large_text='Remis      ', medium_text='Remis   ', small_text='remis ')
            nltxt = Dgt.DISPLAY_TEXT(large_text='remise     ', medium_text='remise  ', small_text='remise')
            frtxt = Dgt.DISPLAY_TEXT(large_text='nulle      ', medium_text='nulle   ', small_text='nulle ')
            estxt = Dgt.DISPLAY_TEXT(large_text='tablas     ', medium_text='tablas  ', small_text='tablas')
            ittxt = Dgt.DISPLAY_TEXT(large_text='patta      ', medium_text='patta   ', small_text='patta ')
        if text_id == 'gameresult_unknown':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(large_text='no result  ', medium_text='noresult', small_text='no res')
            detxt = Dgt.DISPLAY_TEXT(large_text='kein Ergebnis', medium_text='kein Erg', small_text='kein E')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='ness risult', medium_text='norisult', small_text='no ris')
        if text_id == 'playmode_white_user':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(large_text='Player White   ', medium_text='player W', small_text='white ')
            detxt = Dgt.DISPLAY_TEXT(large_text='Spieler Weiß  ', medium_text='SpielerW', small_text='splr w')
            nltxt = Dgt.DISPLAY_TEXT(large_text='speler wit ', medium_text='speler W', small_text='splr w')
            frtxt = Dgt.DISPLAY_TEXT(large_text='joueur B   ', medium_text='joueur B', small_text='blancs')
            estxt = Dgt.DISPLAY_TEXT(large_text='jugador B  ', medium_text='jugad B ', small_text='juga b')
            ittxt = Dgt.DISPLAY_TEXT(large_text='gioc bianco', medium_text='gi bianc', small_text='gioc b')
        if text_id == 'playmode_black_user':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(large_text='player Black   ', medium_text='player B', small_text='black ')
            detxt = Dgt.DISPLAY_TEXT(large_text='Spieler Schwarz  ', medium_text='SpielerS', small_text='splr s')
            nltxt = Dgt.DISPLAY_TEXT(large_text='speler zw  ', medium_text='speler z', small_text='splr z')
            frtxt = Dgt.DISPLAY_TEXT(large_text='joueur n   ', medium_text='joueur n', small_text='noirs ')
            estxt = Dgt.DISPLAY_TEXT(large_text='jugador n  ', medium_text='jugad n ', small_text='juga n')
            ittxt = Dgt.DISPLAY_TEXT(large_text='gioc nero  ', medium_text='gi nero ', small_text='gioc n')
        if text_id == 'language_en_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='English    ', medium_text='English ', small_text='englsh')
            detxt = Dgt.DISPLAY_TEXT(large_text='Englisch   ', medium_text='Englisch', small_text='en    ')
            nltxt = Dgt.DISPLAY_TEXT(large_text='Engels     ', medium_text='Engels  ', small_text='engels')
            frtxt = Dgt.DISPLAY_TEXT(large_text='Anglais    ', medium_text='Anglais ', small_text='anglai')
            estxt = Dgt.DISPLAY_TEXT(large_text='Ingles     ', medium_text='Ingles  ', small_text='ingles')
            ittxt = Dgt.DISPLAY_TEXT(large_text='Inglese    ', medium_text='Inglese ', small_text='ingles')
        if text_id == 'language_de_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='German     ', medium_text='German  ', small_text='german')
            detxt = Dgt.DISPLAY_TEXT(large_text='Deutsch    ', medium_text='Deutsch ', small_text='de    ')
            nltxt = Dgt.DISPLAY_TEXT(large_text='Duits      ', medium_text='Duits   ', small_text='duits ')
            frtxt = Dgt.DISPLAY_TEXT(large_text='Allemand   ', medium_text='Allemand', small_text='allema')
            estxt = Dgt.DISPLAY_TEXT(large_text='Aleman     ', medium_text='Aleman  ', small_text='aleman')
            ittxt = Dgt.DISPLAY_TEXT(large_text='Tedesco    ', medium_text='Tedesco ', small_text='tedesc')
        if text_id == 'language_nl_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Dutch      ', medium_text='Dutch   ', small_text='dutch ')
            detxt = Dgt.DISPLAY_TEXT(large_text='Niederldsch', medium_text='Niederl ', small_text='nl    ')
            nltxt = Dgt.DISPLAY_TEXT(large_text='Nederlands ', medium_text='Nederl  ', small_text='nederl')
            frtxt = Dgt.DISPLAY_TEXT(large_text='Neerlandais', medium_text='Neerlnd ', small_text='neer  ')
            estxt = Dgt.DISPLAY_TEXT(large_text='Holandes   ', medium_text='Holandes', small_text='holand')
            ittxt = Dgt.DISPLAY_TEXT(large_text='Olandese   ', medium_text='Olandese', small_text='olande')
        if text_id == 'language_fr_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='French     ', medium_text='French  ', small_text='french')
            detxt = Dgt.DISPLAY_TEXT(large_text='Franzosisch', medium_text='Franzsch', small_text='fr    ')
            nltxt = Dgt.DISPLAY_TEXT(large_text='Frans      ', medium_text='Frans   ', small_text='frans ')
            frtxt = Dgt.DISPLAY_TEXT(large_text='Francais   ', medium_text='Francais', small_text='france')
            estxt = Dgt.DISPLAY_TEXT(large_text='Frances    ', medium_text='Frances ', small_text='franc ')
            ittxt = Dgt.DISPLAY_TEXT(large_text='Francese   ', medium_text='Francese', small_text='france')
        if text_id == 'language_es_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Spanish    ', medium_text='Spanish ', small_text='spanis')
            detxt = Dgt.DISPLAY_TEXT(large_text='Spanisch   ', medium_text='Spanisch', small_text='es    ')
            nltxt = Dgt.DISPLAY_TEXT(large_text='Spaans     ', medium_text='Spaans  ', small_text='spaans')
            frtxt = Dgt.DISPLAY_TEXT(large_text='Espagnol   ', medium_text='Espagnol', small_text='espag ')
            estxt = Dgt.DISPLAY_TEXT(large_text='Espanol    ', medium_text='Espanol ', small_text='esp   ')
            ittxt = Dgt.DISPLAY_TEXT(large_text='Spagnolo   ', medium_text='Spagnolo', small_text='spagno')
        if text_id == 'language_it_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Italian    ', medium_text='Italian ', small_text='italia')
            detxt = Dgt.DISPLAY_TEXT(large_text='Italienisch', medium_text='Italisch', small_text='it    ')
            nltxt = Dgt.DISPLAY_TEXT(large_text='Italiaans  ', medium_text='Italiaan', small_text='italia')
            frtxt = Dgt.DISPLAY_TEXT(large_text='Italien    ', medium_text='Italien ', small_text='ital  ')
            estxt = Dgt.DISPLAY_TEXT(large_text='Italiano   ', medium_text='Italiano', small_text='italia')
            ittxt = Dgt.DISPLAY_TEXT(large_text='Italiano   ', medium_text='Italiano', small_text='italia')
        if text_id == 'beep_off_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Never      ', medium_text='Never   ', small_text='never ')
            detxt = Dgt.DISPLAY_TEXT(large_text='Nie        ', medium_text='Nie     ', small_text='nie   ')
            nltxt = Dgt.DISPLAY_TEXT(large_text='Nooit      ', medium_text='Nooit   ', small_text='nooit ')
            frtxt = Dgt.DISPLAY_TEXT(large_text='Jamais     ', medium_text='Jamais  ', small_text='jamais')
            estxt = Dgt.DISPLAY_TEXT(large_text='Nunca      ', medium_text='Nunca   ', small_text='nunca ')
            ittxt = Dgt.DISPLAY_TEXT(large_text='Mai        ', medium_text='Mai     ', small_text='mai   ')
        if text_id == 'beep_some_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Sometimes  ', medium_text='Some    ', small_text='sonne ')
            detxt = Dgt.DISPLAY_TEXT(large_text='Manchmal   ', medium_text='Manchmal', small_text='manch ')
            nltxt = Dgt.DISPLAY_TEXT(large_text='Soms       ', medium_text='Soms    ', small_text='sons  ')
            frtxt = Dgt.DISPLAY_TEXT(large_text='Parfois    ', medium_text='Parfois ', small_text='parfoi')
            estxt = Dgt.DISPLAY_TEXT(large_text='A veces    ', medium_text='A veces ', small_text='aveces')
            ittxt = Dgt.DISPLAY_TEXT(large_text='a volte    ', medium_text='a volte ', small_text='avolte')
        if text_id == 'beep_on_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Always     ', medium_text='Always  ', small_text='always')
            detxt = Dgt.DISPLAY_TEXT(large_text='Immer      ', medium_text='Immer   ', small_text='immer ')
            nltxt = Dgt.DISPLAY_TEXT(large_text='Altyd      ', medium_text='Altyd   ', small_text='altyd ')
            frtxt = Dgt.DISPLAY_TEXT(large_text='Toujours   ', medium_text='Toujours', small_text='toujou')
            estxt = Dgt.DISPLAY_TEXT(large_text='Siempre    ', medium_text='Siempre ', small_text='siempr')
            ittxt = Dgt.DISPLAY_TEXT(large_text='Sempre     ', medium_text='Sempre  ', small_text='sempre')
        if text_id == 'oklang':
            entxt = Dgt.DISPLAY_TEXT(large_text='ok language', medium_text='ok lang ', small_text='oklang')
            detxt = Dgt.DISPLAY_TEXT(large_text='ok Sprache ', medium_text='okSprach', small_text='ok spr')
            nltxt = Dgt.DISPLAY_TEXT(large_text='ok taal    ', medium_text='ok taal ', small_text='oktaal')
            frtxt = Dgt.DISPLAY_TEXT(large_text='ok langue  ', medium_text='okLangue', small_text='oklang')
            estxt = Dgt.DISPLAY_TEXT(large_text='ok idioma  ', medium_text='okIdioma', small_text='oklang')
            ittxt = Dgt.DISPLAY_TEXT(large_text='lingua ok  ', medium_text='okLingua', small_text='okling')
        if text_id == 'okeboard':
            entxt = Dgt.DISPLAY_TEXT(large_text='ok eboard', medium_text='okeboard', small_text='ok brd')
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'oklogfile':
            entxt = Dgt.DISPLAY_TEXT(large_text='ok log file', medium_text='oklogfil', small_text='ok log')
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'voice_speed_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Voice speed', medium_text='Vc speed', small_text='vspeed')
            detxt = Dgt.DISPLAY_TEXT(large_text='Stimme - Geschwindigkeit', medium_text='StmGesch', small_text='stmges')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Veloci voce', medium_text='Vel voce', small_text='vevoce')
        if text_id == 'voice_speed':
            entxt = Dgt.DISPLAY_TEXT(large_text='VoiceSpeed' + msg, medium_text='Vspeed ' + msg, small_text='v spe' + msg)
            detxt = Dgt.DISPLAY_TEXT(large_text='Stimme - Geschwindigkeit' + msg, medium_text='StmGes ' + msg, small_text='stm g' + msg)
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Veloc voce' + msg, medium_text='Vevoce ' + msg, small_text='v voc' + msg)
        if text_id == 'okspeed':
            entxt = Dgt.DISPLAY_TEXT(large_text='ok voice sp', medium_text='ok speed', small_text='ok spe')
            detxt = Dgt.DISPLAY_TEXT(large_text='ok Stimme Geschwindigkeit', medium_text='okStmGes', small_text='okstmg')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='ok veloc vo', medium_text='ok veloc', small_text='ok vel')
        if text_id == 'voice_volume_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Voice Volume', medium_text='Vc vol  ', small_text='vs vol')
            detxt = Dgt.DISPLAY_TEXT(large_text='Lautstärke ', medium_text='Stm Vol ', small_text='st vol')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Volume voce', medium_text='Vol voce', small_text='vovoce')
        if text_id == 'voice_volume':
            entxt = Dgt.DISPLAY_TEXT(large_text='Voice Volume ' + msg, medium_text='Volume' + msg, small_text='vol ' + msg)
            detxt = Dgt.DISPLAY_TEXT(large_text='Lautstärke   ' + msg, medium_text='Volume' + msg, small_text='vol ' + msg)
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='VoluVoce ' + msg, medium_text='Volume' + msg, small_text='vol ' + msg)
        if text_id == 'okvolume':
            entxt = Dgt.DISPLAY_TEXT(large_text='ok volume  ', medium_text='ok vol  ', small_text='ok vol')
            detxt = Dgt.DISPLAY_TEXT(large_text='ok Volume  ', medium_text='ok vol  ', small_text='ok vol')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'voice_user_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='User voice ', medium_text='UserVoic', small_text='user v')
            detxt = Dgt.DISPLAY_TEXT(large_text='Spieler Stimme', medium_text='Splr Stm', small_text='splr s')
            nltxt = Dgt.DISPLAY_TEXT(large_text='Speler Stem', medium_text='SplrStem', small_text='splr s')
            frtxt = Dgt.DISPLAY_TEXT(large_text='Joueur Voix', medium_text='JourVoix', small_text='jour v')
            estxt = Dgt.DISPLAY_TEXT(large_text='Jugador Voz', medium_text='JugadVoz', small_text='juga v')
            ittxt = Dgt.DISPLAY_TEXT(large_text='Giocat Voce', medium_text='GiocVoce', small_text='gioc v')
        if text_id == 'voice_comp_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Pico voice ', medium_text='PicoVoic', small_text='pico v')
            detxt = Dgt.DISPLAY_TEXT(large_text='PicoChess Stimme', medium_text='Pico Stm', small_text='pico v')
            nltxt = Dgt.DISPLAY_TEXT(large_text='PicoChsStem', medium_text='PicoStem', small_text='pico s')
            frtxt = Dgt.DISPLAY_TEXT(large_text='PicoChsVoix', medium_text='PicoVoix', small_text='pico v')
            estxt = Dgt.DISPLAY_TEXT(large_text='PicoChs Voz', medium_text='Pico Voz', small_text='pico v')
            ittxt = Dgt.DISPLAY_TEXT(large_text='PicoChsVoce', medium_text='PicoVoce', small_text='pico v')
        if text_id == 'okvoice':
            # wait = True
            entxt = Dgt.DISPLAY_TEXT(large_text='ok Voice   ', medium_text='ok Voice', small_text='ok voc')
            detxt = Dgt.DISPLAY_TEXT(large_text='ok Stimme  ', medium_text='okStimme', small_text='ok stm')
            nltxt = Dgt.DISPLAY_TEXT(large_text='ok Stem    ', medium_text='ok Stem ', small_text='okstem')
            frtxt = Dgt.DISPLAY_TEXT(large_text='ok Voix    ', medium_text='ok Voix ', small_text='okvoix')
            estxt = Dgt.DISPLAY_TEXT(large_text='ok Voz     ', medium_text='ok Voz  ', small_text='ok voz')
            ittxt = Dgt.DISPLAY_TEXT(large_text='ok Voce    ', medium_text='ok Voce ', small_text='okvoce')
        if text_id == 'voice_on':
            entxt = Dgt.DISPLAY_TEXT(large_text='Voice  on  ', medium_text='Voice on', small_text='vc  on')
            detxt = Dgt.DISPLAY_TEXT(large_text='Stimme ein ', medium_text='Stim ein', small_text='st ein')
            nltxt = Dgt.DISPLAY_TEXT(large_text='Stem aan   ', medium_text='Stem aan', small_text='st aan')
            frtxt = Dgt.DISPLAY_TEXT(large_text='Voix allume', medium_text='Voix ete', small_text='vo ete')
            estxt = Dgt.DISPLAY_TEXT(large_text='Voz encend ', medium_text='Voz ence', small_text='vz enc')
            ittxt = Dgt.DISPLAY_TEXT(large_text='Voce attiva', medium_text='Voce att', small_text='vc att')
        if text_id == 'voice_off':
            entxt = Dgt.DISPLAY_TEXT(large_text='Voice off  ', medium_text='Voiceoff', small_text='vc off')
            detxt = Dgt.DISPLAY_TEXT(large_text='Stimme aus ', medium_text='Stim aus', small_text='st aus')
            nltxt = Dgt.DISPLAY_TEXT(large_text='Stem uit   ', medium_text='Stem uit', small_text='st uit')
            frtxt = Dgt.DISPLAY_TEXT(large_text='Voix eteint', medium_text='Voix ete', small_text='vo ete')
            estxt = Dgt.DISPLAY_TEXT(large_text='Voz apagada', medium_text='Voz apag', small_text='vz apa')
            ittxt = Dgt.DISPLAY_TEXT(large_text='Voce spenta', medium_text='Voce spe', small_text='vc spe')
        if text_id == 'okvolume':
            entxt = Dgt.DISPLAY_TEXT(large_text='ok Volume  ', medium_text='okVolume', small_text='ok vol')
            detxt = Dgt.DISPLAY_TEXT(large_text='ok Lautstärke ', medium_text='okLautst', small_text='ok Lau')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'voice_volume_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Voice Volume', medium_text='VoiceVol', small_text='voivol')
            detxt = Dgt.DISPLAY_TEXT(large_text='Lautstärke', medium_text='Lautstr ', small_text='lautst')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Volume voce', medium_text='Vol voce', small_text='vovoce')
        if text_id == 'display_ponder_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Ponder interval', medium_text='PondIntv', small_text='ponint')
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'okponder':
            entxt = Dgt.DISPLAY_TEXT(large_text='ok ponder interval', medium_text='okPondIv', small_text='ok int')
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'ponder_interval':
            entxt = Dgt.DISPLAY_TEXT(large_text='Ponder interval' + msg, medium_text='PondrIv' + msg, small_text='p int' + msg)
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'display_confirm_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Confirm msg', medium_text='Confirm ', small_text='confrm')
            detxt = Dgt.DISPLAY_TEXT(large_text='Zugbestätigung', medium_text='Zugbestg', small_text='zugbes')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Msg Conferm', medium_text='Conferma', small_text='confrm')
        if text_id == 'display_capital_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Capital letters', medium_text='Capital ', small_text='captal')
            detxt = Dgt.DISPLAY_TEXT(large_text='Großbuchstaben ', medium_text='Buchstab', small_text='buchst')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Maiuscolo  ', medium_text='Maiuscol', small_text='maiusc')
        if text_id == 'display_notation_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Move notation', medium_text='Notation', small_text='notati')
            detxt = Dgt.DISPLAY_TEXT(large_text='Zugnotation', medium_text='Notation', small_text='notati')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Notazione m', medium_text='Notazion', small_text='notazi')
        if text_id == 'okconfirm':
            entxt = Dgt.DISPLAY_TEXT(large_text='ok confirm ', medium_text='okConfrm', small_text='okconf')
            detxt = Dgt.DISPLAY_TEXT(large_text='ok Zugbestätigung ', medium_text='okZugbes', small_text='ok bes')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='ok conferma', medium_text='okConfrm', small_text='okconf')
        if text_id == 'confirm_on':
            entxt = Dgt.DISPLAY_TEXT(large_text='Confirm  on', medium_text='Conf  on', small_text='cnf on')
            detxt = Dgt.DISPLAY_TEXT(large_text='Zugbestätigung ein', medium_text='Best ein', small_text='besein')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Conferma si', medium_text='Conf  si', small_text='cnf si')
        if text_id == 'confirm_off':
            entxt = Dgt.DISPLAY_TEXT(large_text='Confirm off', medium_text='Conf off', small_text='cnfoff')
            detxt = Dgt.DISPLAY_TEXT(large_text='Zugbestätigung aus', medium_text='Best aus', small_text='besaus')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Conferma no', medium_text='Conf  no', small_text='cnf no')
        # molli show engine name
        if text_id == 'display_enginename_menu':
            entxt = Dgt.DISPLAY_TEXT(large_text='Show engine name', medium_text='Eng.name', small_text='engnam')
            detxt = Dgt.DISPLAY_TEXT(large_text='Engine-Name', medium_text='Eng.Name', small_text='engnam')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Nome Motore', medium_text='Nom.Moto', small_text='nommot')
        if text_id == 'okenginename':
            entxt = Dgt.DISPLAY_TEXT(large_text='ok enginge name', medium_text='okEngnam', small_text='okengn')
            detxt = Dgt.DISPLAY_TEXT(large_text='ok Engine-Name', medium_text='okEngNam', small_text='okengn')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='ok nom.moto', medium_text='okNommot', small_text='oknomo')
        if text_id == 'enginename_on':
            entxt = Dgt.DISPLAY_TEXT(large_text='Engine name on', medium_text='EngNam on', small_text='eng on')
            detxt = Dgt.DISPLAY_TEXT(large_text='Engine-Name an', medium_text='EngNam an', small_text='eng an')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Nom.Moto si', medium_text='NomMot si', small_text='mot si')
        if text_id == 'enginename_off':
            entxt = Dgt.DISPLAY_TEXT(large_text='Engine name off', medium_text='EngN off', small_text='engoff')
            detxt = Dgt.DISPLAY_TEXT(large_text='Engine-Name aus', medium_text='EngN aus', small_text='engaus')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Nom.Moto no', medium_text='NoMot no', small_text='mot no')
        if text_id == 'okcapital':
            entxt = Dgt.DISPLAY_TEXT(large_text='ok Capital Letters ', medium_text='ok Capt ', small_text='ok cap')
            detxt = Dgt.DISPLAY_TEXT(large_text='ok Großbuchstaben', medium_text='ok Bstab', small_text='ok bst')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='ok Maiuscol', medium_text='ok Maius', small_text='ok mai')
        if text_id == 'capital_on':
            entxt = Dgt.DISPLAY_TEXT(large_text='Capital letters on', medium_text='Capt  on', small_text='cap on')
            detxt = Dgt.DISPLAY_TEXT(large_text='Großbuchstaben ein', medium_text='Bstb ein', small_text='bstein')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Maiuscol si', medium_text='Maius si', small_text='mai si')
        if text_id == 'capital_off':
            entxt = Dgt.DISPLAY_TEXT(large_text='Capital letters off', medium_text='Capt off', small_text='capoff')
            detxt = Dgt.DISPLAY_TEXT(large_text='Großbuchstaben aus', medium_text='Bstb aus', small_text='bstaus')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Maiuscol no', medium_text='Maius no', small_text='mai no')
        if text_id == 'oknotation':
            entxt = Dgt.DISPLAY_TEXT(large_text='ok Notation', medium_text='ok Notat', small_text='ok  nt')
            detxt = Dgt.DISPLAY_TEXT(large_text='ok Notation', medium_text='ok Notat', small_text='ok  nt')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='ok Notazion', medium_text='ok Notaz', small_text='ok  nt')
        if text_id == 'notation_short':
            entxt = Dgt.DISPLAY_TEXT(large_text='Notation short', medium_text='Nt short', small_text='short ')
            detxt = Dgt.DISPLAY_TEXT(large_text='Notation kurz', medium_text='Ntn kurz', small_text='ntkurz')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Notaz corta', medium_text='Nt corta', small_text='corta ')
        if text_id == 'notation_long':
            entxt = Dgt.DISPLAY_TEXT(large_text='Notation long', medium_text='Nt  long', small_text='  long')
            detxt = Dgt.DISPLAY_TEXT(large_text='Notation lang', medium_text='Ntn lang', small_text='ntlang')
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Notaz lunga', medium_text='Nt lunga', small_text=' lunga')
        if text_id == 'tc_fixed':
            entxt = Dgt.DISPLAY_TEXT(large_text='Move time' + msg, medium_text='Move t' + msg, small_text='mov ' + msg)
            detxt = Dgt.DISPLAY_TEXT(large_text='Zugzeit  ' + msg, medium_text='Zug z ' + msg, small_text='zug ' + msg)
            nltxt = Dgt.DISPLAY_TEXT(large_text='Zet tyd  ' + msg, medium_text='Zet t ' + msg, small_text='zet ' + msg)
            frtxt = Dgt.DISPLAY_TEXT(large_text='Mouv     ' + msg, medium_text='Mouv  ' + msg, small_text='mouv' + msg)
            estxt = Dgt.DISPLAY_TEXT(large_text='Mov      ' + msg, medium_text='Mov   ' + msg, small_text='mov ' + msg)
            ittxt = Dgt.DISPLAY_TEXT(large_text='Moss temp' + msg, medium_text='Moss t' + msg, small_text='mos ' + msg)
        if text_id == 'tc_blitz':
            entxt = Dgt.DISPLAY_TEXT(large_text='Game time' + msg, medium_text='Game t' + msg, small_text='game' + msg)
            detxt = Dgt.DISPLAY_TEXT(large_text='Spielzeit' + msg, medium_text='Spielz' + msg, small_text='spl ' + msg)
            nltxt = Dgt.DISPLAY_TEXT(large_text='Spel tyd ' + msg, medium_text='Spel t' + msg, small_text='spel' + msg)
            frtxt = Dgt.DISPLAY_TEXT(large_text='Partie   ' + msg, medium_text='Partie' + msg, small_text='part' + msg)
            estxt = Dgt.DISPLAY_TEXT(large_text='Partid   ' + msg, medium_text='Partid' + msg, small_text='part' + msg)
            ittxt = Dgt.DISPLAY_TEXT(large_text='Game temp' + msg, medium_text='Game t' + msg, small_text='game' + msg)
        if text_id == 'tc_fisch':
            entxt = Dgt.DISPLAY_TEXT(large_text='Fischer ' + msg, medium_text='Fsh' + msg, small_text='f' + msg)
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'tc_tourn':  # molli tournament time control
            entxt = Dgt.DISPLAY_TEXT(large_text=msg[:38], medium_text=msg[:8], small_text=msg[:6])
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'tc_depth':  # support of depth per move search
            entxt = Dgt.DISPLAY_TEXT(large_text='Depth ' + msg, medium_text='Depth ' + msg, small_text='dep ' + msg)
            detxt = Dgt.DISPLAY_TEXT(large_text='Suchtiefe ' + msg, medium_text='Tiefe ' + msg, small_text='tief' + msg)
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = Dgt.DISPLAY_TEXT(large_text='Profo ' + msg, medium_text='Profo ' + msg, small_text='pro ' + msg)
        if text_id == 'noboard':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(large_text='no e-' + msg, medium_text='no' + msg, small_text=msg)
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
            ittxt = entxt
        if text_id == 'update':
            entxt = Dgt.DISPLAY_TEXT(large_text='updating pc', medium_text='updating', small_text='update')
            detxt = entxt
            nltxt = entxt
            frtxt = Dgt.DISPLAY_TEXT(large_text='actualisePc', medium_text='actualis', small_text='actual')
            estxt = Dgt.DISPLAY_TEXT(large_text='actualizoPc', medium_text='actualiz', small_text='actual')
            ittxt = Dgt.DISPLAY_TEXT(large_text='aggiornare ', medium_text='aggiorPc', small_text='aggior')
        if text_id == 'updt_version':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(large_text='Version ' + msg, medium_text='Vers ' + msg, small_text='ver' + msg)
            detxt = Dgt.DISPLAY_TEXT(large_text='Version ' + msg, medium_text='Vers ' + msg, small_text='ver' + msg)
            nltxt = Dgt.DISPLAY_TEXT(large_text='Versie  ' + msg, medium_text='Vers ' + msg, small_text='ver' + msg)
            frtxt = Dgt.DISPLAY_TEXT(large_text='Version ' + msg, medium_text='Vers ' + msg, small_text='ver' + msg)
            estxt = Dgt.DISPLAY_TEXT(large_text='Version ' + msg, medium_text='Vers ' + msg, small_text='ver' + msg)
            ittxt = Dgt.DISPLAY_TEXT(large_text='Versione' + msg, medium_text='Vers ' + msg, small_text='ver' + msg)
        if text_id == 'bat_percent':
            entxt = Dgt.DISPLAY_TEXT(large_text='battery ' + msg, medium_text='battr' + msg, small_text='bat' + msg)
            detxt = Dgt.DISPLAY_TEXT(large_text='Ladezustand' + msg, medium_text='Battr' + msg, small_text='bat' + msg)
            nltxt = Dgt.DISPLAY_TEXT(large_text='batterij' + msg, medium_text='battr' + msg, small_text='bat' + msg)
            frtxt = Dgt.DISPLAY_TEXT(large_text='batterie' + msg, medium_text='battr' + msg, small_text='bat' + msg)
            estxt = Dgt.DISPLAY_TEXT(large_text='bateria ' + msg, medium_text='battr' + msg, small_text='bat' + msg)
            ittxt = Dgt.DISPLAY_TEXT(large_text='batteria' + msg, medium_text='battr' + msg, small_text='bat' + msg)

        for txt in [entxt, detxt, nltxt, frtxt, estxt, ittxt]:
            if txt:
                txt.wait = wait
                txt.beep = beep
                txt.maxtime = maxtime
                txt.devs = devs

        if entxt is None:
            beep = self.bl(BeepLevel.YES)
            entxt = Dgt.DISPLAY_TEXT(large_text=text_id, medium_text=text_id, small_text=text_id, wait=False, beep=beep, maxtime=0, devs=devs)
            logging.warning('unknown text_id %s', text_id)
        if self.language == 'de' and detxt is not None:
            return self.capital_text(detxt)
        if self.language == 'nl' and nltxt is not None:
            return self.capital_text(nltxt)
        if self.language == 'fr' and frtxt is not None:
            return self.capital_text(frtxt)
        if self.language == 'es' and estxt is not None:
            return self.capital_text(estxt)
        if self.language == 'it' and ittxt is not None:
            return self.capital_text(ittxt)
        return self.capital_text(entxt)
