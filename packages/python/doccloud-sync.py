#!/usr/bin/env python3
# vim: set ts=4 sts=0 sw=4 si fenc=utf-8 et:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# Maintainers: BP
# Copyright:   2025, HRDAG, GPL v2 or later
# =========================================

# ---- dependencies {{{
from pathlib import Path
from sys import stdout
import argparse
from loguru import logger
import re
import pandas as pd
from documentcloud import DocumentCloud
#}}}

# --- support methods --- {{{
def getargs():
    parser = argparse.ArgumentParser()
    parser.add_argument("--projectid", default="219560-human-trafficking-cpd")
    parser.add_argument("--outdir", default=None)
    parser.add_argument("--outpdfs", default=None)
    parser.add_argument("--outannots", default=None)
    args = parser.parse_args()
    assert Path(args.outdir).exists()
    return args


def setuplogging(logfile):
    logger.add(logfile,
               colorize=True,
               format="<green>{time:YYYY-MM-DD⋅at⋅HH:mm:ss}</green>⋅<level>{message}</level>",
               level="INFO")
    return 1


def writepdf(fname, pdfbyts):
    with open(fname, 'wb') as f:
        f.write(pdfbyts)
        f.close()
    return True


def getcreds():
    with open("creds/doccloud") as f:
        line = f.readline()
    found = line.split("|")
    assert len(found) == 2
    return found[0], found[1]


def getclient():
    user, pwd = getcreds()
    client = DocumentCloud(username=user, password=pwd)
    return client


def getdoc(doc):
    info = {
        'pdfurl': doc.get_pdf_url(),
        'filehash': doc.file_hash,
        'filename': doc.title,
        'fileid': doc.id,
        'created_at': doc.created_at,
        'last_update': doc.updated_at,
        'n_pages': doc.page_count,
        'doc': doc,
    }
    return info


def build_docdf(docs):
    data = []
    for doc in docs:
        info = getdoc(doc=doc)
        data.append(info)
    assert any(data)
    out = pd.DataFrame(data)
    assert out.shape[0] == len(data) == len(docs)
    assert not out.pdfurl.isna().any()
    assert not out.fileid.isna().any()
    return out


def findrd(fname):
    assert not pd.isna(fname)
    found = re.findall(pattern="[A-Z]{1,2}[0-9]{5,7}", string=fname)
    if not len(found) == 1: return None
    return found[0]


def addrd(df):
    copy = df.copy()
    copy['rd'] = copy.filename.apply(findrd)
    assert copy.rd.notna().sum() == 163
    assert copy.rd.isna().sum() == 1
    assert (copy.loc[copy.rd.isna(), 'fileid'] == 25211366).all()
    copy.loc[(copy.rd.isna()) & (copy.fileid == 25211366), 'rd'] = "JG271294"
    return copy


def getannot(annotation):
    info = {
        'created_at': annotation.created_at,
        'annotid': annotation.id,
        'pageno': annotation.page_number,
        'title': annotation.title,
        'content': annotation.content,
        'loc_x12_y12': (annotation.x1, annotation.x2, annotation.y1, annotation.y1),
        'loc_btlr': (annotation.location.top, annotation.location.bottom, annotation.location.left, annotation.location.right),
        'annotation': annotation,
    }
    return info


def formatannots(doc):
    annots = doc.annotations.list()
    if not any(annots): return pd.DataFrame()
    data = []
    for ea in annots:
        info = getannot(annotation=ea)
        data.append(info)
    assert any(data)
    out = pd.DataFrame(data)
    assert out.shape[0] == len(data)
    assert not out.loc[:, out.columns != 'annotation'].duplicated().any()
    assert not out.annotid.isna().any()
    assert not out.loc_x12_y12.isna().any()
    return out


def build_annotdf(df):
    data = []
    for tup in df[['fileid', 'doc']].itertuples():
        annots = formatannots(doc=tup.doc)
        if annots.shape[0] == 0: continue
        annots['fileid'] = tup.fileid
        data.append(annots)
    assert len(data) >= 1
    out = pd.concat(data)
    assert out.shape[0] >= len(data)
    return out
# }}}

# --- main --- {{{
if __name__ == '__main__':
    args = getargs()
    setuplogging("output/sync.log")

    logger.info('(1/5) setting up Document Cloud API client')
    client = getclient()

    logger.info('(2/5) collecting project documents')
    project = client.projects.get_by_id(args.projectid)
    docs = project.document_list
    docsdf = build_docdf(docs=docs)
    docsdf = addrd(df=docsdf)

    logger.info('(3/5) pulling annotations')
    annotsdf = build_annotdf(df=docsdf)

    logger.info(f'(4/5) writing pdf data locally in {args.outdir}')
    docsdf['localcopy'] = docsdf[['rd', 'doc']].apply(
        lambda row: writepdf(
            fname=f"{args.outdir}/{row.rd}.pdf",
            pdfbyts=row.doc.pdf),
        axis=1)

    logger.info('(5/5) writing reference tables')
    docsdf.loc[:, docsdf.columns != 'doc'].to_parquet(args.outpdfs)
    annotsdf.loc[:, annotsdf.columns != 'annotation'].to_parquet(args.outannots)

    logger.info('done')
# }}}

# done
