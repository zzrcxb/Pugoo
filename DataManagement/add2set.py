from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from .converter import SGF2Json
from .sgfreader import SGF
from HashSys.hashsys import *
from .file_errors import *
import datetime
import os

from .__init__ import *


class Statistics:
    def __init__(self):
        self.total = 0
        self.valid = 0
        self.zh = 0
        self.jp = 0
        self.kr = 0
        self.ot = 0

        self.content_err = 0
        self.format_err = 0
        self.decode_err = 0
        self.label_missed = 0
        self.size_err = 0
        self.komi_err = 0
        self.res_err = 0
        self.step_err = 0

    def save_statistics(self, file_path):
        save_time = str(datetime.datetime.now()).replace(':', '_')
        if not file_path.endswith(os.sep):
            file_path = file_path + os.sep
        try:
            with open(file_path + 'log-' + save_time + '.txt', 'w') as f:
                f.write('=================Statistic info====================\n')
                f.write(
"""
Total: %d file(s)
Valid: %d file(s)
Chinese: %d file(s)
Japanese: %d file(s)
Korean: %d file(s)
Other: %d file(s)
==================Errors====================
Content error: %d file(s)
     Size error: %d file(s)
     Komi error: %d file(s)
     Result error: %d file(s)
     Label missed: %d file(s)
     Step error: %d file(s)
Decode error: %d file(s)
Format error: %d file(s)
""" % (self.total, self.valid, self.zh, self.jp, self.kr, self.ot, self.content_err, self.size_err, self.komi_err,
       self.res_err, self.label_missed, self.step_err,  self.decode_err, self.format_err))
                f.write('\n')
                f.write(save_time)
        except IOError as e:
            print(e)
            return None


def add2set(in_path, f_format=None, source=None, debug=False, log_path=None):
    if debug:
        print(db_url)
    ss = Statistics()
    # Deal with database
    engine = create_engine(db_url)
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    if in_path.find(raw_path[1:-1]) == -1:
        in_folder = in_path
        in_path = raw_path + in_folder

    for root, dirs, files in os.walk(in_path):
        for file in files:
            ss.total += 1
            # Specific format
            if f_format:
                if not file.lower().endswith(f_format.lower()):
                    continue
                raw_name = file.replace('.' + f_format, '')
            else:  # Don't care about format
                raw_name = file
            file_path = root + os.sep + file

            # Read sgf file
            sgf = SGF()
            try:
                content = sgf.load(file_path)
            except FileDecodeError:
                ss.decode_err += 1
                continue

            # Get labels
            try:
                sgf.get_labels()
            except FileResultError:
                ss.res_err += 1
                continue
            except FileKomiError:
                ss.komi_err += 1
                continue
            except FileSizeError:
                ss.size_err += 1
                continue
            except FileLabelMissed:
                ss.label_missed += 1
                continue
            except FileStepError:
                ss.step_err += 1
                continue
            except FileFormatError:
                ss.format_err += 1
                continue

            # Get base and convert
            try:
                go_base = SGF2Json(content, sgf.labels, raw_name)
            except FileStepError:
                ss.step_err += 1
            if not go_base:
                print(file_path, 'Convert error')
                continue

            # Move file and add to session
            file_hash = get_file_md5(file_path)
            if not move_file_by_hash(file_hash, tmp_path + raw_name + '.bg'):
                print(file_path, 'Move file error')
                continue
            go_base.filehash = file_hash
            go_base.filesource = repr(source)
            go_base.rawfilepath = file_path
            session.add(go_base)

            ss.valid += 1

    try:
        session.commit()
    except IntegrityError:
        print('Duplicated entry, build training data set failed')
        return None
    if log_path:
        ss.save_statistics(log_path)