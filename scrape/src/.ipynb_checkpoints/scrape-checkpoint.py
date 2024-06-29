# vim: set ts=4 sts=0 sw=4 si fenc=utf-8 et:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# Maintainers: BP
# Copyright:   2023, HRDAG, GPL v2 or later
# =========================================
# SFO-pubdef-documents/individual/DPA/scrape/src/scrape.py

# ---- dependencies {{{
import os
from pathlib import Path
from sys import stdout
import argparse
import logging
import yaml
import time
import random
import hashlib
from functools import partial
import requests
from bs4 import BeautifulSoup
import pandas as pd
#}}}

# ---- support methods {{{
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=None)
    parser.add_argument("--domain", default=None)
    parser.add_argument("--agents", default=None)
    parser.add_argument("--names", default=None)
    parser.add_argument("--outdir", default=None)
    parser.add_argument("--ref_out", default=None)
    parser.add_argument("--rev_out", default=None)
    args = parser.parse_args()
    assert Path(args.agents)
    assert Path(args.names)
    assert Path(args.outdir)
    return args


def get_logger(sname, file_name=None):
    logger = logging.getLogger(sname)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s " +
                                  "- %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
    stream_handler = logging.StreamHandler(stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    if file_name:
        file_handler = logging.FileHandler(file_name)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    return logger


def readyaml(fname):
    with open(fname, 'r') as f:
        data = yaml.safe_load(f)
    return data


def readfile(fname):
    with open(fname, 'rb') as f:
        data = f.read()
    return data


def writefile(fname, data):
    with open(fname, 'wb') as f:
        f.write(data)
    return 1


def get_user_agent():
    idx = random.randint(0, len(users)-1)
    return users[idx]


def parse_link(url, agent):
    res = requests.get(url, headers={"User-Agent" : agent})
    html = res.content
    parsed = BeautifulSoup(html, "html.parser")
    return parsed


def try_parse(url, users):
    print(f'parsing:\t{url}')
    random.shuffle(users)
    soup = None
    for user in users:
        try:
            soup = parse_link(url=url, agent=user)
            break
        except:
            time.sleep(.2)
            continue
    if pd.isna(soup):
        print(f'unable to parse URL')
        exit(1)
    return soup


def extract_revocations(html, keyphrase):
    revocations = [ea for li in html.find_all('li') for ea in li.find_all('a')
                   if keyphrase in str(ea)]
    assert len(revocations) >= 18
    return revocations


def unpack_revocations(domain, revocations):
    data = []
    for li in revocations:
        info = {'officer_name': li.contents[0],
                'href': li['href']}
        info['given_hash'] = info['href'][info['href'].find('hash='):]
        info['pdfurl'] = domain + info['href']
        data.append(info)
    assert len(data) > 10
    out = pd.DataFrame(data)
    return out


def get_file(fileurl, user):
    response = requests.get(fileurl, headers={"User-Agent" : user})
    return response.content


def try_download(outdir, url, users, fext):
    print(f'attempting to download:\t{url}')
    random.shuffle(users)
    found, have = None, None
    filename = url[url.rfind('/')+1:url.rfind(fext)+len(fext)]
    filename = f'{outdir}/{filename}'
    if os.path.exists(filename): have = readfile(fname=filename)
    for i in range(20):
        user =  get_user_agent()
        try:
            found = get_file(fileurl=url, user=user)
            if pd.isna(found): continue
            if pd.notna(have):
                if have == found:
                    print(f'a file with the same name and contents already exists in {outdir}.')
                else:
                    print(f'a file with the same name already exists in {outdir} but the contents do not match. \
                    Writing found data with the name filename as the root and todays date as suffix')
                    filename = filename[-len(fext):] + time.strftime('%Y-%m-%d') + fext
                    assert writefile(fname=filename, data=found)
            else:
                assert writefile(fname=filename, data=found)
                print(f"download successful")
            break
        except:
            time.sleep(.2)
            continue
    if all([pd.isna(v) for v in (have, found)]):
        print(f'unable to parse URL')
        return None
    return filename


def hashrecord(rec, dataset=None):
    '''given a pandas record and a string dataset name,
       hash the dataset name and the record's fields w sha1,
       return the hexdigest.
    '''
    hasher = hashlib.sha1()
    hasher.update(bytearray(str(dataset), encoding='utf-8'))
    for f in rec:
        hasher.update(bytearray(str(f), encoding='utf-8'))
    return hasher.hexdigest()[:8]


def hashfile(fname):
    if pd.isna(fname): return None
    with open(fname, 'rb') as f:
        digest = hashlib.file_digest(f, "sha1")
    return digest.hexdigest()[:8]
#}}}

# ---- main {{{
if __name__ == '__main__':
    # setup logging
    logger = get_logger(__name__, "output/scrape.log")

    # arg handling
    args = get_args()
    users = readyaml(args.agents)
    sitenames = readyaml(args.names)
    sitenames = pd.DataFrame(sitenames).T.reset_index(names='caseno')
    soup = try_parse(url=args.url, users=users)
    title = soup.title.string
    if title: print(f"page title:\t{title}")
    revocations = extract_revocations(html=soup, keyphrase='Commission-Information/Revocations')
    data = unpack_revocations(domain=args.domain, revocations=revocations)
    data['filename'] = data.pdfurl.apply(
        lambda x: try_download(outdir=args.outdir, url=x, users=users, fext='.pdf'))
    assert data.filename.notna().all()
    data['fileid'] = data.filename.apply(hashfile)
    assert sitenames.shape[0] == data.shape[0]
    sitenames['last_name'] = sitenames.officer_name.apply(lambda x: x.split()[-1])
    data['last_name'] = data.officer_name.apply(lambda x: x.split()[-1])
    assert not sitenames.last_name.duplicated().any()
    both = pd.merge(sitenames, data[['last_name', 'pdfurl', 'fileid']],
                    on='last_name')
    hash_recs = partial(hashrecord, dataset=both)
    both['revocation_id'] = both.apply(hash_recs, axis=1)
    data.to_csv(args.ref_out, index=False)
    both.to_csv(args.rev_out, index=False)

    logger.info("done.")
#}}}
# done.