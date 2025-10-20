#!/usr/bin/env python3
# vim: set ts=4 sts=0 sw=4 si fenc=utf-8 et:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# Maintainers: BP
# Copyright:   2025, HRDAG, GPL v2 or later
# =========================================

# ---- dependencies {{{
import sys
import pandas as pd

sys.path.append(".")
from build_html_table import get_table
#}}}

PARAMS = [
    'INDICATOR_COL',
    'INDICATOR_OP',
    'GROUP_COL',
    'RENAMER',
]


# --- support methods --- {{{
def format_countperc(num, den):
    prop = num / den
    return f"{int(num)} ({prop*100:.1f}%)"


def byeach_group(df, groupcol, eventcol, renamer):
    #@TODO: update this method to use the `format_countperc` method
    if df.shape[0] == df[eventcol].sum():
        print(f"Expected at least one record with negative indicator, but \
        all {df.shape[0]} records have positive {eventcol} value.")
        return None
    nobs = df.shape[0]
    table = pd.crosstab(
        index=df[groupcol],
        columns=df[eventcol].rename(''),
        margins=True, margins_name='Total').reset_index().rename(columns=renamer)
    table['true_prop'] = table[renamer[True]]/table.Total
    table['false_prop'] = table[renamer[False]]/table.Total
    #table['total_prop'] = table['Total']/nobs # @TODO: revisit how to best represent prop group total over all
    table[renamer[True]] = table[[renamer[True], 'true_prop']].apply(
        lambda row: f"{int(row[renamer[True]])} ({row.true_prop*100:.1f}%)", axis=1)
    table[renamer[False]] = table[[renamer[False], 'false_prop']].apply(
        lambda row: f"{int(row[renamer[False]])} ({row.false_prop*100:.1f}%)", axis=1)
    #table['Total'] = table[['Total', 'total_prop']].apply(
    #    lambda row: f"{int(row['Total'])} ({row.total_prop*100:.1f}%)", axis=1)
    table = table[[c for c in table.columns if 'prop' not in c]]
    html = get_table(
        df=pd.DataFrame(table.to_dict()),
        font_size='11pt', font_family='Georgia', text_align='left',
        width='auto',
        index=True,
        font_color='black',
        color='grey_dark',
        padding='4px',
        #even_bg_color='white'
    )
    return html


def byeach_event(df, groupcol, eventcol, renamer):
    if df.shape[0] == df[eventcol].sum():
        print(f"Expected at least one record with negative indicator, but \
        all {df.shape[0]} records have positive {eventcol} value.")
        return None
    # setup the core counts
    if eventcol in renamer.keys(): label = renamer[eventcol]
    else: label = ''
    nobs = df.shape[0]
    table = pd.crosstab(
        index=df[groupcol],
        columns=df[eventcol].rename(label),
        margins=True, margins_name='Total').reset_index().rename(columns=renamer)
    # format counts as f'{COUNT} ({PERC}%)'
    tablet = table.set_index(renamer[groupcol]).T
    dencol = tablet['Total']
    tableindex = tablet.index
    tofix = [c for c in tablet.columns if c != 'Total']
    data = []
    for col in tofix:
        numcol = tablet[col]
        countperc = [
            format_countperc(num=numcol.values[rowi], den=dencol.values[rowi])
            for rowi in range(3)]
        info = pd.DataFrame(index=tableindex, columns=[col], data=countperc)
        data.append(info.T)
    data.append(pd.DataFrame(dencol).T)
    table = pd.concat(data).T.reset_index()
    # format as html
    html = get_table(
        df=pd.DataFrame(table.to_dict()),
        font_size='11pt', font_family='Georgia', text_align='left',
        width='auto',
        index=True,
        font_color='black',
        color='grey_dark',
        padding='4px',
        #even_bg_color='white'
    )
    return html


def by_conviction(df, givencol, groupcol, eventcol):
    #@TODO: work in `format_countperc`
    #@TODO: can this be another call to `byeach_group` instead?
    table = pd.crosstab(
        index=df.loc[df[givencol], groupcol],
        columns=df[eventcol].rename(''),
        margins=True, margins_name='Total').reset_index().rename(columns={
        False: 'No conviction', True: 'Any conviction', 'race_ethnicity': 'Recorded Race/Ethnicity',})
    table['true_prop'] = table['Any conviction']/table.Total
    table['false_prop'] = table['No conviction']/table.Total
    table['Any conviction'] = table[['Any conviction', 'true_prop']].apply(
        lambda row: f"{int(row['Any conviction'])} ({row.true_prop*100:.1f}%)", axis=1)
    table['No conviction'] = table[['No conviction', 'false_prop']].apply(
        lambda row: f"{int(row['No conviction'])} ({row.false_prop*100:.1f}%)", axis=1)
    table = table[[c for c in table.columns if 'prop' not in c]]
    html = get_table(
        df=pd.DataFrame(table.to_dict()),
        color='grey_dark',
        font_size='11pt', font_family='Georgia', text_align='left',
        width='auto', padding='4px',
        index=True,
        font_color='black',
        even_bg_color='white')
    return html


def report_outcome(item_i, magic, df, givencol, groupcol, eventcol):
    magic['table'] = {}
    label = f"outcome_{givencol}"
    magic['table'][label] = {
        'html': by_conviction(df=df, givencol=givencol, groupcol=groupcol, eventcol=eventcol)}
    info = f"{item_i}.\tThe following is the distribution of outcomes across racial categories for all cases in which {statute} was alleged/filed. Each row refers to one racial category, with a column for conviction of {statute} and no conviction of {statute}. Margin columns for the Total by row and/or column are also included.\n\n\t"
    mdFile.new_paragraph(info)
    mdFile.new_paragraph(magic['table'][label]['html'])
    mdFile.new_paragraph()
    return item_i + 1, magic



def verifycols(df, cols):
    for col in cols:
        assert col in df.columns, f"\
        Expected `{col}` to be in DataFrame with columns:\n{df.columns}"
        #assert df[col].isin((True, False)).all(), f"\
        #Expecting column `{col}` to be a Boolean indicator, found datatype {df[col].dtype}"
        #assert df[col].dtype == bool, f"\
        #Expecting column `{col}` to be a Boolean indicator, found datatype {df[col].dtype}"
    return 1


class Summary():
    """
    Calculation:
    - Table: df[[INDICATOR_COL, GROUP_COL]].groupby(GROUP_COL)[INDICATOR_COL].sum()
    - Description: Summarize by {GROUP_COL} all records where {INDICATOR_COL} is True
    Present:
    - Count/Percent: '{GROUP_COL.sum()/INDICATOR_COL.sum()*100}% ({GROUP_COL.sum()} of {INDICATOR_COL.sum()})'
    - Finding:
        - Of the {INDICATOR_COL.sum()},
            - {magic['GROUP_COUNTS'][GROUP_LABEL]} were for {GROUP_LABEL}
            - (repeated for each group appearing in GROUP_COL)
    """

    def __init__(self, df, params, labels):
        self.df = df
        assert all([k in PARAMS] for k in params.keys()), f"\
        Expected  only known parameters {PARAMS}, found {params.keys()}"
        assert verifycols(df, cols=[
            v for param, v in params.items() if '_COL' in param])
        self.params = params
        self.labels = labels
        self.magic = {}
        self.info = """"""
        self.label = """"""
        self.table_wingroup = None
        self.table_winevent = None


    def __setmagic__(self):
        df = self.df
        magic = self.params
        if 'RENAMER' not in magic.keys(): magic['RENAMER'] = {True: 'True', False: 'False'}
        INDICATOR_COL, INDICATOR_OP, GROUP_COL = magic[
            'INDICATOR_COL'], magic['INDICATOR_OP'], magic['GROUP_COL']
        magic['INDICATOR_COUNT'] = df[INDICATOR_COL].sum()
        magic['GROUP_COUNTS'] = df[[INDICATOR_COL, GROUP_COL]
            ].groupby(GROUP_COL)[INDICATOR_COL].sum().to_dict()
        magic['GROUP_PERCENTS'] = (df[[INDICATOR_COL, GROUP_COL]
            ].groupby(GROUP_COL)[INDICATOR_COL].sum(
            )/magic['INDICATOR_COUNT']*100).to_dict()
        assert magic['INDICATOR_COUNT'] == sum(magic['GROUP_COUNTS'].values()), f"\
        Missing group placeholder value for some indicated records."
        self.magic = magic


    def __setinfo__(self):
        info = f"""Of the {self.magic['INDICATOR_COUNT']} {
            self.labels[self.magic['INDICATOR_COL']]},"""
        for GROUP_LABEL, GROUP_IND_SUM in self.magic['GROUP_COUNTS'].items():
            info += f"\n-  {GROUP_IND_SUM} or {self.magic['GROUP_PERCENTS'][GROUP_LABEL]:.1f}% {
                self.magic['INDICATOR_OP']} {self.labels[self.magic['GROUP_COL']]} {GROUP_LABEL}."
        self.info = info


    def __settables__(self):
        label = f"""Of the {self.df.shape[0]:,} cases considered, there are {
            self.magic['INDICATOR_COUNT']} {
            self.labels[self.magic['INDICATOR_COL']]
            }, with the following distribution:\n"""
        self.label = label
        if '_wconv' in self.magic['INDICATOR_COL']:
            html_wingroup = by_conviction(
                df=self.df, # should there be a given col here, or should we expect the user to pass filtered data?
                givencol=self.magic['INDICATOR_COL'].replace('_wconv', ''),
                groupcol=self.magic['GROUP_COL'],
                eventcol=self.magic['INDICATOR_COL'])
            self.table_wingroup = html_wingroup
        else:
            html_wingroup = byeach_group(
                df=self.df,
                groupcol=self.magic['GROUP_COL'],
                eventcol=self.magic['INDICATOR_COL'],
                renamer=self.magic['RENAMER'])
            html_winevent = byeach_event(
                df=self.df,
                groupcol=self.magic['GROUP_COL'],
                eventcol=self.magic['INDICATOR_COL'],
                renamer=self.magic['RENAMER'])
            self.table_wingroup = html_wingroup
            self.table_winevent = html_winevent


    def getmagic(self):
        if self.magic == {}: self.__setmagic__()
        return self.magic


    def getinfo(self):
        if self.magic == {}: self.__setmagic__()
        if self.info == '': self.__setinfo__()
        return self.info


    def gettable_wingroup(self):
        if self.magic == {}: self.__setmagic__()
        if not self.table_wingroup: self.__settables__()
        return self.label, self.table_wingroup


    def gettable_winevent(self):
        if self.magic == {}: self.__setmagic__()
        if not self.table_winevent: self.__settables__()
        return self.label, self.table_winevent


    def __str__(self):
        return self.info


    def __repr__(self):
        return str(self.magic)


    def __dict__(self):
        return self.magic
# }}}

# done.
