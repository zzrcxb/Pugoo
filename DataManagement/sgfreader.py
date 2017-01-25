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

    def load(self, file_path, buf_size=65536):
        try:
            with open(file_path, 'rb') as f:
                raw = f.read(buf_size)
                while True:
                    data = f.read(buf_size)
                    if not data:
                        break
                    raw += data
                self.sgf = raw.decode('utf-8')
        except IOError as e:
            print(e)
            return None
        except UnicodeDecodeError:
            self.utf_8 = False
            try:
                with open(file_path, 'rb') as f:
                    raw = f.read(buf_size)
                    while True:
                        data = f.read(buf_size)
                        if not data:
                            break
                        raw += data
                    self.sgf = raw.decode('gb2312')
            except IOError as e:
                print(e)
                return None
            except UnicodeDecodeError:
                raise FileDecodeError()  # Annoying decode problem

        self.loaded = True
        return self.sgf

    def get_labels(self):
        if not self.loaded:
            return False
        pattern = re.compile(r'([A-Z][A-Z])(\[)([^\]]+)(\])')
        labels = pattern.findall(self.sgf)
        for label in labels:
            self.labels[label[0]] = label[2]


    def get_ru(self, rule):
        if self.rule:
            return self.rule
        elif not rule:
            return None
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
            return None
        else:
            try:
                return float(komi)
            except ValueError:
                raise FileKomiError()

    def get_re(self, result):
        if not result:
            return None

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
            return None
        else:
            try:
                return int(size)
            except ValueError:
                raise FileSizeError()
