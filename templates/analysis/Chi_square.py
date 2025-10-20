#!/usr/bin/env python3
# vim: set ts=4 sts=0 sw=4 si fenc=utf-8 et:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# Maintainers: BP
# Copyright:   2025, HRDAG, GPL v2 or later
# =========================================

# ---- dependencies {{{
from scipy.stats import power_divergence
#}}}

DEFAULTS = {
    'SIG': 0.05,
    'DDOF': 0,
}

CENSUS_PARAMS = [
    'CENSUS_DICT',
    'OBSERVED_DICT',
    'NULL_PHRASE',
    'SIG',
    'DDOF',
]

EQUAL_PARAMS = [
    'OBSERVED_DICT',
    'NULL_PHRASE',
    'SIG',
    'DDOF',
]

# --- support methods --- {{{
def format_longfloat(num):
    return float(f'{num:.3f}')


def text_statistic(pcs, sig, n, df, null_phrase, exp=None):
    rounded_stat = format_longfloat(pcs.statistic)
    rounded_pval = format_longfloat(pcs.pvalue)
    if rounded_pval == 0: rounded_pval = "< 0.0001"
    if exp: newinfo = f"\n\tThis test results in a **p-value of {rounded_pval}**, "
    else: newinfo = f"\n\tThis test results in a **p-value of {rounded_pval}**, "
    if pcs.pvalue < sig:
        newinfo += f"which is a statistically significant difference and rejects the null hypothesis that {null_phrase}. "
    else: newinfo += f"which is not statistically significant and fails to reject the null hypothesis that {null_phrase}. "
    if n < 30: newinfo += f"However, the sample size of {n} is small."
    return newinfo


def add_chisquare_census(censusdict, obsdict, null_phrase, sig, ddof):
    if not sorted(obsdict.keys()) == sorted(censusdict.keys()):
        """This is intended to fill in 0 values for groups not represented in the summary counts."""
        for k in censusdict.keys():
            if k not in obsdict.keys(): obsdict[k] = 0
    assert sorted(obsdict.keys()) == sorted(censusdict.keys()), f"\
    Expected census count dictionary and observed count dictionary to have the same keys.\
    Found census with keys {sorted(censusdict.keys())} and observed with keys {sorted(obsdict.keys())}."
    cats = obsdict.keys()
    # delta degrees of freedom ('ddof') and degrees of freedom ('df')
    df = len(cats) - 1 - ddof
    obs_n = [v for v in obsdict.values()]
    totalobs = sum(obs_n)
    exp_n = [round(censusdict[group]['prop']*totalobs, 5) for group in cats]
    assert sum(obs_n) == sum(exp_n), f"\
    The sum of the observed frequencies must agree with \
    the sum of the expected frequencies, but {sum(obs_n)} != {sum(exp_n)}"
    pcs_county_n = power_divergence(f_obs=obs_n, f_exp=exp_n, ddof=ddof, lambda_ = "pearson")
    chi_info = f"""This test compares whether observed racial proportions \
    match the proportion of each racial group in the general population.\
    In interpreting the results, a p-value below {sig} will be considered statistically significant.\n"""
    chi_info += text_statistic(
        pcs=pcs_county_n,
        sig=sig,
        n=totalobs,
        df=df,
        null_phrase=null_phrase,
        exp=exp_n
    )
    return chi_info


def add_chisquare_equal(obsdict, null_phrase, sig, ddof):
    cats = obsdict.keys()
    # delta degrees of freedom ('ddof') and degrees of freedom ('df')
    df = len(cats) - 1 - ddof
    obs_n = [v for v in obsdict.values()]
    totalobs = sum(obs_n)
    pcs_obs_n = power_divergence(f_obs=obs_n, ddof=ddof, lambda_ = "pearson")
    chi_info = f"""This test compares whether observed racial proportions match the proportion of each racial group in the general population.\
    In interpreting the results, a p-value below {sig} will be considered statistically significant.\n"""
    chi_info += text_statistic(
        pcs=pcs_obs_n,
        sig=sig,
        n=totalobs,
        df=df,
        null_phrase=null_phrase,
    )
    return chi_info


class Census():
    """
    Calculation:
    - Table: 
    - Description: 
    Present:
    - Contingency table: 
    - Finding: 
    """

    def __init__(self, params):
        assert all([k in CENSUS_PARAMS for k in params.keys()]), f"\
        Expected only known parameters {CENSUS_PARAMS}, found {params.keys()}"
        self.params = params
        self.info = ""
        

    def __setinfo__(self):
        censusdict = self.params['CENSUS_DICT']
        obsdict = self.params['OBSERVED_DICT']
        null_phrase = self.params['NULL_PHRASE']
        if 'SIG' not in self.params.keys(): sig = DEFAULTS['SIG']
        else: sig = self.params['SIG']
        if 'DDOF' not in self.params.keys(): ddof = DEFAULTS['DDOF']
        else: ddof = self.params['DDOF']
        info = add_chisquare_census(
            censusdict=censusdict,
            obsdict=obsdict,
            null_phrase=null_phrase,
            sig=sig,
            ddof=ddof
        )
        self.info = info
        

    def getinfo(self):
        if self.info == "": self.__setinfo__()
        return self.info


    def __str__(self):
        return self.getinfo()


class Equal():
    """
    Calculation:
    - Table: 
    - Description: 
    Present:
    - Contingency table: 
    - Finding: 
    """

    def __init__(self, params):
        assert all([k in EQUAL_PARAMS for k in params.keys()]), f"\
        Expected only known parameters {EQUAL_PARAMS}, found {params.keys()}"
        self.params = params
        self.info = ""
        

    def __setinfo__(self):
        obsdict = self.params['OBSERVED_DICT']
        null_phrase = self.params['NULL_PHRASE']
        if 'SIG' not in self.params.keys(): sig = DEFAULTS['SIG']
        else: sig = self.params['SIG']
        if 'DDOF' not in self.params.keys(): ddof = DEFAULTS['DDOF']
        else: ddof = self.params['DDOF']
        info = add_chisquare_equal(
            obsdict=obsdict,
            null_phrase=null_phrase,
            sig=sig,
            ddof=ddof
        )
        self.info = info
        

    def getinfo(self):
        if self.info == "": self.__setinfo__()
        return self.info


    def __str__(self):
        return self.getinfo()
# }}}

# done.
