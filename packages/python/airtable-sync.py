#!/usr/bin/env python3
# vim: set ts=4 sts=0 sw=4 si fenc=utf-8 et:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# Maintainers: BP
# Copyright:   2024, HRDAG, GPL v2 or later
# =========================================

# ---- dependencies {{{
from pathlib import Path
from sys import stdout
import argparse
from loguru import logger
import pyairtable as at
import pandas as pd
#}}}

LINKS = {
    'hotline_database': 'https://airtable.com/appz4hOaz40iNCQ54/tblLAbHMaYwKLSUHu/viwlL6VElJO7lnnkp',
    'cw_hearings': 'https://airtable.com/appLCRgBv3MljqZpH/tbluVSpnXTq9WxrrA/viwQ4Jbge0vPW5mqV?blocks=hide',
}

# --- support methods --- {{{
def getargs():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hotline", default=None)
    parser.add_argument("--hearings", default=None)
    args = parser.parse_args()
    return args


def setuplogging(logfile):
    logger.add(logfile,
               colorize=True,
               format="<green>{time:YYYY-MM-DD⋅at⋅HH:mm:ss}</green>⋅<level>{message}</level>",
               level="INFO")
    return 1


def getcreds():
    with open("/Users/home/git/dotfiles/creds/ds_airtable", "r") as f:
        out = f.readline()
    return out


def processlink(url):
    if not url: return None
    pieces = url.split('/')
    baseid, tableid = None, None
    for piece in pieces:
        if 'app' == piece[:3]: baseid = piece
        elif 'tbl' == piece[:3]: tableid = piece
    if not baseid: print(f'could not extract base_id from URL: {url}')
    if not tableid: print(f'could not extract table_id from URL: {url}')
    return {'base_id': baseid, 'table_id': tableid}


def getformatrows(api, baseid, tableid):
    if (baseid is None) | (tableid is None): return None
    rows = api.table(baseid, tableid).all()
    df = pd.DataFrame(rows)
    return df


def formatfields(ref, x):
    copy = ref.copy()
    copy.update(x)
    return copy


def formattable(table):
    assert table.shape[0] == table.id.nunique(), f"\
    Expecting data to have 1 `record_id` per row, but nrows {
    table.shape[0]} != nunique id {table.id.nunique()}"

    logger.info('collecting every field reported at least once')
    allfields = set()
    for fieldset in table.fields.values:
        for k in fieldset.keys(): allfields.add(k)
    template = {field: None for field in allfields}

    logger.info('use collected as template to standardize all reported data')
    table.fields = table.fields.apply(
        lambda x: formatfields(ref=template, x=x))

    logger.info('format meta + report data as one table')
    dfs = []
    for row in table.itertuples():
        df = pd.DataFrame([row.fields])
        df['recordid'] = row.id
        df['date_created'] = row.createdTime
        dfs.append(df)
    df = pd.concat(dfs).reset_index(drop=True)
    return df
# }}}

# --- main --- {{{
if __name__ == '__main__':
    args = getargs()
    setuplogging("output/sync.log")
    api = at.Api(api_key=getcreds())
    tableinfo = {
        label: processlink(url=link)
        for label, link in LINKS.items()
    }

    logger.info('accessing & formatting table data as table')
    tables = {
        label: getformatrows(
            api=api,
            baseid=info['base_id'],
            tableid=info['table_id'])
        for label, info in tableinfo.items()
    }

    logger.info('unpacking data in each table')
    hotline = formattable(table=tables['hotline_database'])
    hearings = formattable(table=tables['cw_hearings'])

    logger.info('writing accessed and formatted datasets')
    hotline.to_parquet(args.hotline)
    hearings.to_parquet(args.hearings)

    logger.info('done')
# }}}

# done.
