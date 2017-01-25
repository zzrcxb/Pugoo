from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from .sgfreader import SGF
from .gobase import GoBase
import os

from .__init__ import *


def add2set(in_path, f_format=None, source=None):
    # Deal with database
    engine = create_engine(db_url)
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    if in_path.find(raw_path) == -1:
        in_folder = in_path
        in_path = raw_path + in_folder

    for root, dirs, files in os.walk(in_path):
        for file in files:
            # Specific format
            if not f_format:
                if not file.lower().endswith(f_format.lower()):
                    continue
            else:  # Don't care about format
                pass
            file_path = root + os.sep + file
            sgf = SGF()
            content = sgf.load(file_path)
            if not content:
                continue  # Load failed
            sgf.get_labels()
            labels = sgf.labels



