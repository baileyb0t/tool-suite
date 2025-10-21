#!/usr/bin/env python3
# vim: set ts=4 sts=0 sw=4 si fenc=utf-8 et:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# Maintainers: BP
# Copyright:   2025, HRDAG, GPL v2 or later
# =========================================

# ---- dependencies {{{
import sys
import numpy as np
import pandas as pd

sys.path.append(".")
from build_html_table import get_table
#}}}

CONTINGENCY_PARAMS = [
    'COMPARISON_GROUP_COL',
    'OUTCOME_EVENT_COL',
    'GIVEN_EVENT_COL',
]

RATIO_PARAMS = [
    'TREAT_GROUP_COL',
    'CONTROL_GROUP_COL',
    'OUTCOME_EVENT_OP', # supplemental to LABELS dictionary
    'OUTCOME_EVENT_COL',
    'GIVEN_EVENT_COL',
]

# --- support methods --- {{{
def verifycols(df, cols):
    for col in cols:
        assert col in df.columns, f"\
        Expected `{col}` to be in DataFrame with columns:\n{df.columns}"
        #assert df[col].dtype == bool, f"\
        #Expecting column `{col}` to be a Boolean indicator, found datatype {df[col].dtype}"
    return 1


def rel_risk(treat_event, treat_noevent, control_event, control_noevent, control_group_desc, given_event_desc):
    if ((pd.isna(control_event)) | (control_event == 0)):
        if control_noevent > 0:
            # @TODO: Revise this message to be more robust to different contexts
            return f"no [records of the outcome for the control group] were available for the comparison\
            .\n\n\tIf the treatment were the same for both groups, we would expect to observe at least \
            {int((treat_event / (treat_event + treat_noevent))*control_noevent)} out of {control_noevent} \
            [control records] to [have True for the outcome event]. However, \
            none of the [control records] have [True for the outcome event]"
        else:
            return f"no records of {given_event_desc} against {control_group_desc} available for comparison"
    num = treat_event / (treat_event + treat_noevent)
    den = control_event / (control_event + control_noevent)
    out = num / den
    assert pd.notna(out), f"{treat_event, treat_noevent, control_event, control_noevent}"
    assert not np.isinf(out), f"{treat_event, treat_noevent, control_event, control_noevent}"
    return out


def supp_risk_line(treat_event, control_event, outcome_event, outcome_op, rat):
    if rat < 1: cat = "less than"
    elif rat == 1: cat = "the same as"
    else: cat = "greater than"
    if rat == 1:
        info = f"In other words, the relative risk that {
            treat_event} {outcome_op} {outcome_event} is **{
            cat}** {control_event}.\n\n"
    else:
        info = f"In other words, the relative risk that {
            treat_event} {outcome_op} {outcome_event} is **{
            abs(1-rat)*100:.1f}% {cat}** {control_event}.\n\n"
    return info


def add_relrisk_results(treat_event, control_event, outcome_event, outcome_op, rat):
    if type(rat) is str:
        relrisk_info = f"""The ratio of the probability that {
            treat_event} {outcome_op} {outcome_event} compared to the probability that {
            control_event} {outcome_op} {outcome_event
            } **could not be calculated** because there were {rat}.\n\n"""
    elif np.isinf(rat):
        print(treat_event, control_event, rat)
    else:
        relrisk_info = f"""The ratio of the probability that {
            treat_event} {outcome_op} {outcome_event} compared to the probability that {
            control_event} {outcome_op} {outcome_event} is {rat:.3f}.\n\n"""
        relrisk_info += supp_risk_line(
            treat_event=treat_event,
            control_event=control_event,
            outcome_event=outcome_event,
            outcome_op=outcome_op,
            rat=rat)
    return relrisk_info


class Contingency():
    """
    Calculation:
    - Table: 
    - Description: 
    Present:
    - Contingency table: 
    - Finding: 
    """

    def __init__(self, df, params, labels):
        self.df = df
        assert all([k in CONTINGENCY_PARAMS for k in params.keys()]), f"\
        Expected known parameters {CONTINGENCY_PARAMS}, \nfound {params.keys()}"
        assert verifycols(df, cols=[
            v for param, v in params.items() if '_COL' in param])
        self.params = params
        self.labels = labels # @TODO: Pull in labels to rename fields in table
        self.table = {}


    def __setfulltable__(self):
        """This is different than the other contingency table method.
        We want to have a version that presents all groups in the table,
        so this uses the original `race_ethnicity` column instead of the adhoc `comparison_group_{x}`.
        """
        df = self.df
        magic = self.params
        # do we need to filter for candidates here like we do in the Ratio class?
        OUTCOME_EVENT_COL, GIVEN_EVENT_COL = magic['OUTCOME_EVENT_COL'], magic['GIVEN_EVENT_COL']
        df = df.copy()
        table = pd.crosstab(
            index=df.loc[df[GIVEN_EVENT_COL], OUTCOME_EVENT_COL],
            columns=df['race_ethnicity'],
            margins=True, margins_name='Total'
            ).reindex([True, False, 'Total']).reset_index().rename(columns={
            OUTCOME_EVENT_COL: f'{self.labels[OUTCOME_EVENT_COL]} given {self.labels[GIVEN_EVENT_COL]}',})
        # this is where to swap in labels instead of T/F
        #table[OUTCOME_EVENT_COL] = table[OUTCOME_EVENT_COL].replace({True: 'Conviction', False: 'No conviction'})
        html = get_table(
            df=pd.DataFrame(table.to_dict()),
            color='grey_dark',
            font_size='12pt', font_family='Georgia', text_align='left',
            #width_dict=['20px', '2.5in', '1in', '1in', '1in',], doesn't seem to work..?
            padding='4px',
            index=True,
            font_color='black',
            even_bg_color='white')
        self.table = html


    def __settable__(self):
        """This is different than the methods to calculate the ratio,
        because the `pd.crosstab()` method used to get the contingency table with marginal totals
        works on categorical fields.
        Note: This is why the indicate task sets up the `outcome_*` and `comparison_group_*` columns.
        """
        df = self.df
        magic = self.params
        # do we need to filter for candidates here like we do in the Ratio class?
        COMPARISON_GROUP_COL, OUTCOME_EVENT_COL, GIVEN_EVENT_COL = magic[
            'COMPARISON_GROUP_COL'], magic['OUTCOME_EVENT_COL'], magic['GIVEN_EVENT_COL']
        df = df.loc[df[COMPARISON_GROUP_COL].notna()].copy()
        df[COMPARISON_GROUP_COL] = df[COMPARISON_GROUP_COL].str.title()
        table = pd.crosstab(
            index=df.loc[df[GIVEN_EVENT_COL], OUTCOME_EVENT_COL],
            columns=df[COMPARISON_GROUP_COL],
            margins=True, margins_name='Total'
            ).reindex([True, False, 'Total']).reset_index().rename(columns={
            OUTCOME_EVENT_COL: f'{self.labels[OUTCOME_EVENT_COL]} given {self.labels[GIVEN_EVENT_COL]}',})
        # this is where to swap in labels instead of T/F
        #table[OUTCOME_EVENT_COL] = table[OUTCOME_EVENT_COL].replace({True: 'Conviction', False: 'No conviction'})
        html = get_table(
            df=pd.DataFrame(table.to_dict()),
            color='grey_dark',
            font_size='12pt', font_family='Georgia', text_align='left',
            #width_dict=['20px', '2.5in', '1in', '1in', '1in',], doesn't seem to work..?
            padding='4px',
            index=True,
            font_color='black',
            even_bg_color='white')
        self.table = html


    def gettable(self):
        if 'COMPARISON_GROUP_COL' not in self.params.keys():
            if self.table == {}: self.__setfulltable__()
        else:
            if self.table == {}: self.__settable__()
        return self.table


    def __str__(self):
        return self.gettable()


class Ratio():
    """
    Calculation:
    - Table: 
    - Description: 
    Present:
    - Ratio: 
    - Finding: 
    """

    def __init__(self, df, params, labels):
        self.df = df
        assert sorted(params.keys()) == sorted(RATIO_PARAMS), f"\
        Expected known parameters {RATIO_PARAMS}, \nfound {params.keys()}"
        assert verifycols(df, cols=[
            v for param, v in params.items() if '_COL' in param])
        self.params = params
        self.labels = labels
        self.magic = {}
        self.info = """"""


    def __setmagic__(self):
        df = self.df
        magic = self.params.copy()
        TREAT_GROUP_COL, CONTROL_GROUP_COL = magic[
            'TREAT_GROUP_COL'], magic['CONTROL_GROUP_COL']
        OUTCOME_EVENT_COL, GIVEN_EVENT_COL = magic[
            'OUTCOME_EVENT_COL'], magic['GIVEN_EVENT_COL']
        df = df.loc[(
            df[GIVEN_EVENT_COL]) & ((
            df[TREAT_GROUP_COL]) | (df[CONTROL_GROUP_COL]))
        ]
        for param, col  in self.params.items():
            if '_COL' not in param: continue
            label = f"{param.replace('_COL', '_SUM')}"
            magic[label] = df[col].sum()
        for eventvar in ('OUTCOME', 'GIVEN'):
            for groupvar in ('TREAT', 'CONTROL'):
                label, nolabel = f"{groupvar}_{eventvar}_SUM", f"{groupvar}_NO{eventvar}_SUM"
                groupcol = magic[f"{groupvar}_GROUP_COL"]
                eventcol = magic[f"{eventvar}_EVENT_COL"]
                magic[label] = ((df[groupcol]) & (df[eventcol])).sum()
                if eventvar == 'OUTCOME':
                    magic[nolabel] = ((df[groupcol]) & (~df[eventcol])).sum()
        self.magic = magic


    def __setinfo__(self):
        ratio = rel_risk(
            treat_event=self.magic['TREAT_OUTCOME_SUM'],
            treat_noevent=self.magic['TREAT_NOOUTCOME_SUM'],
            control_event=self.magic['CONTROL_OUTCOME_SUM'],
            control_noevent=self.magic['CONTROL_NOOUTCOME_SUM'],
            control_group_desc=self.labels[self.magic['CONTROL_GROUP_COL']],
            given_event_desc=self.labels[self.magic['GIVEN_EVENT_COL']]
        )
        info = add_relrisk_results(
            treat_event=self.labels[self.magic['TREAT_GROUP_COL']],
            control_event=self.labels[self.magic['CONTROL_GROUP_COL']],
            outcome_event=self.labels[self.magic['OUTCOME_EVENT_COL']],
            outcome_op=self.magic['OUTCOME_EVENT_OP'],
            rat=ratio)
        self.info = info


    def getinfo(self):
        if self.magic == {}: self.__setmagic__()
        if self.info == '': self.__setinfo__()
        return self.info


    def getmagic(self):
        if self.magic == {}: self.__setmagic__()
        return self.magic


    def __str__(self):
        return self.info


    def __repr__(self):
        return str(self.magic)


    def __dict__(self):
        return self.magic
# }}}

# done.
