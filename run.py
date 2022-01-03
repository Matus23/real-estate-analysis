import numpy as np
import numpy_financial as npf
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import rep_utils


def get_validated_fxd_irs():
    fxd_irs = input("Enter space-separated fixed interest rate(s) in % form: ")

    #Check fixed interest rates
    try:
        fxd_irs = fxd_irs.split(" ")
        fxd_irs = [float(ir)/100 for ir in fxd_irs]
    except:
        raise TypeError("Enter numerical value(s) in % form for interest rate(s)")

    return fxd_irs


def get_validated_fxd_durs():
    fxd_durs = input("Enter duration(s) of fixed interest rate: ")

    try:
        fxd_durs = fxd_durs.split(" ")
        fxd_durs = [int(dur)+0 for dur in fxd_durs]
    except:
        raise TypeError("Enter integer value(s) for duration(s) of fixed interest rate")

    return fxd_durs
    

def get_validated_loan_duration():
    ln_dur = input("Enter total loan duration in years: ")
    
    try:
        ln_dur = int(ln_dur) + 0
    except:
        raise TypeError("Enter integer value for loan duration")

    return ln_dur


def get_validated_principal():
    principal = input("Enter loan principal (initial size of loan): ")
    
    try:
        principal = int(principal) + 0
    except:
        raise TypeError("Enter numerical value for loan principal")

    return principal


def get_validated_fees():
    fees = input("Enter space-separated loan fee(s): ")
    
    try:
        fees = fees.split(" ")
        fees = [int(fee)+0 for fee in fees]
    except:
        raise TypeError("Enter integer value(s) for loan fees")

    return fees

def get_validated_interest_rate():
    base_rate     = input("Enter your central bank base interest rate: ")
    additional_ir = input("Enter interest rate your bank charges on top of the central bank base rate: ")

    try:
        base_rate     = float(base_rate) / 100
        additional_ir = float(additional_ir) / 100
    except:
        raise TypeError("Enter numerical values for base rate and additional bank rate")

    return base_rate, additional_ir


def get_inputs():
    fxd_irs = get_validated_fxd_irs()
    fxd_durs = get_validated_fxd_durs()
    ln_dur = get_validated_loan_duration()
    principal = get_validated_principal()
    fees = get_validated_fees()
    base_rate, additional_ir = get_validated_interest_rate()
    
    return fxd_irs, fxd_durs, ln_dur, principal, fees, base_rate, additional_ir


def main():
    descriptions = []
    # fxd_irs = [2.00, 2.18, 1.90, 2.75] 
    # fxd_durs = [2, 5, 5, 10]
    # ln_dur = 15
    # principal = [60000] * len(fxd_irs)
    # fees = [0, 0, 1295, 1795]
    # BBER = 0.1
    # additional_ir = 4.49
 
    fxd_irs, fxd_durs, ln_dur, principal, fees, base_rate, additional_ir = get_inputs()

    var_ir = rep_utils.calculate_variable_interest_rate(base_rate, additional_ir)
    ipmts, ppmts, pmts, pers, lns = rep_utils.compare_mortgages(principal, ln_dur, fxd_irs, fxd_durs, fees, var_ir)

    for ind in range(len(fxd_irs)):
        descr = "Initial interest rate: {},  Fixed period: {} years".format(fxd_irs[ind], fxd_durs[ind])
        descriptions.append(descr)

    rep_utils.visualize_mortgage_repayments(pmts, pers, descriptions)
    rep_utils.visualize_total_repayments(lns, descriptions)

main()