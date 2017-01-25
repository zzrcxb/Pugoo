import os
import re
from converter import SGF2Json
import datetime


class Filter:
    def __init__(self, inpath, outpath):
        self.inpath = inpath
        self.outpath = outpath
        self.pattern_re = re.compile(r'(RE)+([^\]]+|\])')
        self.pattern_ru = re.compile(r'(RU)+([^\]]+|\])')
        self.pattern_sz = re.compile(r'(SZ)+([^\]]+|\])')
        self.pattern_ko = re.compile(r'(KO)+([^\]]+|\])')
        self.pattern_sgf = re.compile('[^.sgf]+.sgf')
        self.pattern_SGF = re.compile('[^.SGF]+.SGF')
        self.jp = 0
        self.ch = 0
        self.kr = 0
        self.ot = 0
        self.szerr = 0
        self.fm_err = 0
        self.ctent = 0
        self.total = 0
        self.dec = 0
        self.dec_files = []

    def check_file(self, filepath):
        with open(filepath, 'rb') as infile:
            try:
                sgf = infile.read().decode('utf-8')
            except UnicodeDecodeError:
                with open(filepath, 'rb') as infile:
                    try:
                        sgf = infile.read().decode('gb2312')  # Angry about people who don't use Unicode!!!
                    except:
                        self.dec += 1
                        self.dec_files.append(filepath)
                        return False

        # Komi
        res_ko = self.pattern_sz.findall(sgf)
        if len(res_ko) != 1:
            self.fm_err += 1
            return False
        else:
            res_ko = res_ko[0][1].replace('[', '')
            try:
                komi = float(res_ko)
            except ValueError:
                self.ctent += 1
                return False
        # Check size
        res_sz = self.pattern_sz.findall(sgf)
        if len(res_sz) != 1:
            self.fm_err += 1
            return False
        else:
            res_sz = res_sz[0][1].replace('[', '')
            try:
                linenum = int(res_sz)
                if linenum != 19:
                    self.szerr += 1
                    return False
            except ValueError:
                self.ctent += 1
                return False

        # Check Result
        res_re = self.pattern_re.findall(sgf)
        if len(res_re) != 1:
            self.fm_err += 1
            return False
        else:
            res_re = res_re[0][1].replace('[', '').split('+')
            if len(res_re) != 2:
                self.fm_err += 1
                return False
            elif res_re[0] != 'B' and res_re[0] != 'b' and res_re[0] != 'w' and res_re[0] != 'W':
                self.ctent += 1
                return False
            else:
                try:
                    res_val = float(res_re[1])
                    if res_re[0] == 'W' or res_re[0] == 'w':
                        res_val = -res_val
                except ValueError:
                    self.ctent += 1
                    return False
        # Get rule
        res_ru = self.pattern_ru.findall(sgf)
        # print(res_ru)
        if len(res_ru) != 1:
            self.ot += 1
            return ('Other', res_val, komi)
        else:
            ru = res_ru[0][1].replace('[', '')
            ru = ru.title()
            if ru == 'Chinese':
                self.ch +=1
                return ('Chinese', res_val, komi)
            elif ru == 'Japanese':
                self.jp += 1
                return ('Japanese', res_val, komi)
            elif ru == 'Korean':
                self.kr += 1
                return ('Korean', res_val, komi)
            else:
                self.ot += 1
                return ('Other', res_val, komi)


    def get_files(self):
        os.chdir(self.outpath)
        if not os.path.exists('Chinese'):
            os.makedirs('Chinese')
        if not os.path.exists('Japanese'):
            os.makedirs('Japanese')
        if not os.path.exists('Korean'):
            os.makedirs('Korean')
        if not os.path.exists('Other'):
            os.makedirs('Other')
        os.chdir(self.inpath)
        for root, dirs, files in os.walk(self.inpath):
            for file in files:
                self.total += 1
                if self.pattern_sgf.match(file) or self.pattern_SGF.match(file):
                    # Check
                    res = self.check_file(root + os.sep + file)
                    if res != False:
                        name = file.split('.sgf')[0]
                        SGF2Json(root + os.sep + file, self.outpath + os.sep + res[0] + os.sep + name + '.bg', res[0], res[1], res[2])
        with open(self.outpath + os.sep + 'log-' + str(datetime.datetime.now()) + '.txt', 'w') as out_log:
            out_log.write('Total: %d file(s)\n' % self.total)
            out_log.write('Chinese rule: %d file(s)\n' % self.ch)
            out_log.write('Japanese rule: %d file(s)\n' % self.jp)
            out_log.write('Korean rule: %d file(s)\n' % self.kr)
            out_log.write('Other rule: %d file(s)\n' % self.ot)
            out_log.write('From: ' + self.inpath)
            out_log.write('To: ' + self.outpath)
            out_log.write('==========Error(s)=========\n')
            out_log.write('Line number error: %d file(s)\n' % self.szerr)
            out_log.write('Format error: %d file(s)\n' % self.fm_err)
            out_log.write('Content error: %d file(s)\n' % self.ctent)
            out_log.write('\n' + str(datetime.datetime.now()))

