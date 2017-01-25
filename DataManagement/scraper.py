# To use this function
# Make sure you are under Linux environment with 7-zip, unzip, unrar installed

from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import os
from config import DOWNLOAD_PATH, RAW_DATA_PATH, ROOT_PATH


def scrap(url):
    out_path = DOWNLOAD_PATH
    raw_path = RAW_DATA_PATH
    root = ROOT_PATH

    if not raw_path.endswith(os.sep):
        raw_path = raw_path + os.sep

    if not root.endswith(os.sep):
        root = root + os.sep

    if not out_path.endswith(os.sep):
        out_path = out_path + os.sep

    if not os.path.exists(out_path):
        print('Download path is not existed')
        return False

    # Send request
    req = Request(url=url)
    try:
        html = urlopen(req)
    except:
        print('Something wrong with network or website')
        return False

    bsobj = BeautifulSoup(html, 'html.parser')
    links = bsobj.findAll('a')

    # Get download links
    for link in links:
        try:
            dl_url = link.attrs['href']
        except KeyError:
            continue

        if dl_url.startswith('./'):
            base = url.split('/')
            dl_url = dl_url.replace('./', '')
            base[-1] = dl_url
            dl_url = ''.join(base)

        # Support zip rar 7z and tar
        if dl_url.lower().endswith('.zip') or dl_url.lower().endswith('.rar') or dl_url.lower().endswith('.7z')\
                or dl_url.lower().endswith('.tar.gz'):
            os.chdir(out_path)
            os.system(' '.join(['wget', dl_url]))
            file_name = dl_url.split('/')[-1]  # No /
            os.chdir(root)  # Change back

            if file_name.lower().endswith('.zip'):  # unzip file_name -d ./sub/
                os.system(' '.join(['unzip', out_path + file_name, '-d', raw_path + file_name.replace('.zip', '')]))
            elif file_name.lower().endswith('.rar'):  # unrar x file_name ./sub/
                os.system(' '.join(['unrar', 'x', out_path + file_name, raw_path + file_name.replace('.rar', '')]))
            elif file_name.lower().endswith('.7z'):  # 7z x -o./sub/ file_name
                os.system(' '.join(['7z', 'x', '-d' + raw_path + file_name.replace('.7z', ''), out_path + file_name]))
            elif file_name.lower().endswith('.tar.gz'):  # tar -xvzf file_name -C ./sub/
                os.system(' '.join(['tar', '-xvzf', out_path + file_name,
                                    '-C', raw_path + file_name.replace('.tar.gz', '')]))
            else:
                continue