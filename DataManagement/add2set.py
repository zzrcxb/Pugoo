from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from .converter import SGF2Json
from .sgfreader import SGF
from HashSys.hashsys import *
from .file_errors import *
import os

from .__init__ import *


def add2set(in_path, f_format=None, source=None, debug=False):
    if debug:
        print(db_url)
    # Deal with database
    engine = create_engine(db_url)
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    if in_path.find(raw_path[1:-1]) == -1:
        in_folder = in_path
        in_path = raw_path + in_folder
    if debug:
        print('in_path=', in_path)

    for root, dirs, files in os.walk(in_path):
        for file in files:
            # Specific format
            if f_format:
                if not file.lower().endswith(f_format.lower()):
                    continue
                raw_name = file.replace('.' + f_format, '')
            else:  # Don't care about format
                raw_name = file
            file_path = root + os.sep + file
            if debug:
                print('file_path=', file_path)
            sgf = SGF()
            content = sgf.load(file_path)
            if not content:
                if debug:
                    print(file_path, 'Content error')
                continue  # Load failed
            try:
                sgf.get_labels()
                if debug:
                    print(sgf.labels)
            except FileContentError:
                if debug:
                    print('Content Error while get_labels')
                continue
            except FileFormatError:
                if debug:
                    print('Format Error while get_labels')
                continue

            go_base = SGF2Json(content, sgf.labels, raw_name)
            if not go_base:
                if debug:
                    print(file_path, 'Convert error')
                continue
            file_hash = get_file_md5(file_path)
            if not move_file_by_hash(file_hash, tmp_path + raw_name + '.bg'):
                if debug:
                    print(file_path, 'Move file error')
                continue
            if debug:
                print('File hash is', file_hash)
            go_base.filehash = file_hash
            go_base.filesource = repr(source)
            go_base.rawfilepath = file_path
            try:
                session.add(go_base)
            except IntegrityError:
                if debug:
                    print(file_path, 'Already existed')
                continue
    session.commit()