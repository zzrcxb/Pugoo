from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *

TableBase = declarative_base()

class GoBase(TableBase):
    __tablename__ = 'training'
    filehash = Column(String(44), primary_key=True)
    fileformat = Column(String(10), default=None)
    filesource = Column(String(64), default=None)
    rawfilepath = Column(String(256), nullable=False)

    size = Column(Integer, nullable=False)
    rule = Column(String(32), nullable=False)
    komi = Column(Float, nullable=False)
    result = Column(Float, nullable=False)
    handicap = Column(Float, nullable=False)

    def __repr__(self):
        return '<GoBase(filehash = %s, fileformat = %s, filesource = %s, rawfilepath = %s, ' \
               'size = %s, rule = %s, komi = %s, result = %s)>' \
               % \
               (self.filehash, self.fileformatm, self.filesource,
                self.rawfilepath, self.size, self.rule, self.komi, self.result)

    def __str__(self):
        return self.__repr__()
