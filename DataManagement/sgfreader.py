import re
from .file_errors import *
from config import RESIGN
import os
from .__init__ import *


class SGF:
    def __init__(self):
        self.utf_8 = True
        self.gb2312 = True
        self.labels = {}
        self.loaded = False
        self.komi = None
        self.rule = None
        self.size = None
        self.handicap = None

    def load(self, file_path, buf_size=65536):
        try:
            with open(file_path, 'r') as f:
                raw = f.read(buf_size)
                while True:
                    data = f.read(buf_size)
                    if not data:
                        break
                    raw += data
                self.sgf = raw
        except IOError as e:
            print(e)
            return None
        except UnicodeDecodeError:
            raise FileDecodeError()

        self.loaded = True
        return self.sgf

    def get_labels(self):
        if not self.loaded:
            return False
        pattern = re.compile(r'([A-Z][A-Z])(\[)([^\]]+)(\])')
        labels = pattern.findall(self.sgf)
        for label in labels:
            self.labels[label[0]] = label[2]
        self.labels['RU'] = self.get_ru(self.labels.get('RU', None))
        self.labels['RE'] = self.get_re(self.labels.get('RE', None))
        self.labels['KM'] = self.get_komi(self.labels.get('KM', None))
        self.labels['SZ'] = self.get_sz(self.labels.get('SZ', None))
        self.labels['HA'] = self.get_ha(self.labels.get('HA', None))

    def get_ru(self, rule):
        if self.rule:
            return self.rule
        elif not rule:
            if self.rule:
                return self.rule
            else:
                raise FileLabelMissed()
        elif rule.lower() == 'chinese':
            return 'Chinese'
        elif rule.lower() == 'japanese':
            return 'Japanese'
        elif rule.lower() == 'korean':
            return 'Korean'
        else:
            return 'Unknown'

    def get_komi(self, komi):
        if self.komi:
            return self.komi
        elif not komi:
            if self.komi:
                return self.komi
            else:
                raise FileLabelMissed()
        else:
            try:
                return float(komi)
            except ValueError:
                raise FileKomiError()

    def get_re(self, result):
        if not result:
            raise FileLabelMissed()

        try:
            winner = result.split('+')[0]
            value = result.split('+')[1]
        except IndexError:
            raise FileFormatError()

        try:
            value = float(value)
        except ValueError:
            if value.lower() == 'r' or value.lower() == 'resign':
                value = RESIGN
            else:
                raise FileResultError()

        if winner.lower() == 'w':
            value = - value
        return value

    def get_sz(self, size):
        if self.size:
            return self.size
        elif not size:
            if self.size:
                return self.size
            else:
                raise FileLabelMissed()
        else:
            try:
                return int(size)
            except ValueError:
                raise FileSizeError()

    def get_ha(self, handicap):
        if self.handicap:
            return self.handicap
        elif not handicap:
            return 0
        else:
            try:
                return int(handicap)
            except ValueError:
                raise FileHandicapError()
