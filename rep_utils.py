import numpy as np
import numpy_financial as npf
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def calculate_variable_interest_rate(BBER, additional_ir):
    """
        Calculates interest rate that will be applied after the fixed period
    """
    return BBER + additional_ir


def calculate_total_loan_repayment(pmt_fxd, per_fxd, pmt_var, per_var):
    """
        Calculates total amount of money needed to repay the mortgage
        Returns: 
            total value needed to repay the mortgage
    """
    return pmt_fxd * len(per_fxd) + pmt_var * len(per_var)


def get_payment_period(fut_duration, paid_off_duration=0):
    """
        Args:
            fut_duration: # years the loan will be paid off for
            paid_off_duration: # years the loan has been paid off for
        Returns:
            payment period in months in a list form
    """
    return np.arange(fut_duration * 12) + 1 + paid_off_duration * 12


def get_num_compunding_periods(loan_duration_in_years):
    """
        Converts loan duration from years to months
    """
    return loan_duration_in_years * 12


def get_monthly_interest_rate(annual_interest_rate):
    """
        Converts annual interest rate into monthly rate
    """
    return annual_interest_rate / 12


def put_payments_in_absolute_value(ipmt, ppmt, pmt=0):
    """
        Puts payments into absolute value
    """
    return [abs(num) for num in ipmt], [abs(num) for num in ppmt], abs(pmt)


def concatenate_repayments(ipmt_fxd, ppmt_fxd, pmt_fxd, per_fxd, ipmt_var, 
                            ppmt_var, pmt_var, per_var):
    ipmt_fxd = ipmt_fxd[:len(per_fxd)]
    ppmt_fxd = ppmt_fxd[:len(per_fxd)]
    
    pmt_fxd = [pmt_fxd] * len(per_fxd)
    pmt_var = [pmt_var] * len(per_var)
    
    ipmt = ipmt_fxd + ipmt_var
    ppmt = ppmt_fxd + ppmt_var
    pmt  = pmt_fxd + pmt_var
    
    return ipmt, ppmt, pmt


def update_principal(principal, ppmt, duration):
    """
        Subtracts the amount of balance that has been paid off during the 
        fixed interest-rate period
        Args:
            principal - initial value of the loan
            ppmt - monthly repayments that go towards paying off the principal
            duration - # years how long the principal has been paid off for 
        Returns:
            principal - update value of the principal
    """
    duration_in_months  = duration * 12

    # The loan duration cannot be longer than # monthly payments
    # It can be shorter because the interest rate might change over time
    if  duration_in_months > len(ppmt):
        return -1

    for ind in range(duration_in_months):
        principal -= ppmt[ind]
        
    return principal


def get_repayments(principal, ir, loan_dur):
    """
        Args:
            principal - (initial) size of the loan
            ir - annual interest rate in percentage form 
            loan_dur - duration of the loan in years
        Returns
            ipmt - list of monthly interest repayments
            ppmt - list of monthly principal repayments
            pmt - list total monthly repayments (ipmt + ppmt for a given month)
    """
    monthly_ir = get_monthly_interest_rate(ir)

    per  = get_payment_period(loan_dur)
    nper = get_num_compunding_periods(loan_dur)
    ipmt = npf.ipmt(monthly_ir, per, nper, principal)
    ppmt = npf.ppmt(monthly_ir, per, nper, principal)
    pmt  = npf.pmt(monthly_ir, nper, principal)
    ipmt, ppmt, pmt = put_payments_in_absolute_value(ipmt, ppmt, pmt)

    return ipmt, ppmt, pmt


def calculate_mortgage_repayment(principal, fxd_ir, loan_dur, var_ir, fxd_dur):
    """
    Calculates mortgage repayment schedule
        Args:
            principal - (initial) size of the loan
            fxd_ir - annual interest rate in percentage form 
            loan_dur - duration of the loan in years
            var_ir - (expected) future/variable annual interest rate 
            fxd_dur - # years of fixed interest rate
        Returns
            ipmt - list of monthly interest repayments
            ppmt - list of monthly principal repayments
            pmt - list total monthly repayments (ipmt + ppmt for a given month)
            per - list of months during which the loan is paid off
            loan_total - total amount of money to repay the loan
    """
    # get full payment period
    per = get_payment_period(loan_dur)
    
    # Fixed ir repayment
    fxd_per = get_payment_period(fxd_dur)
    ipmt_fxd, ppmt_fxd, pmt_fxd = get_repayments(principal, fxd_ir, loan_dur)
    
    # Variable ir repayment
    # decrease loan duration by period that has been paid off (fixed ir payment period)
    loan_dur -= fxd_dur
    # update principal with the part that was paid off during the fixed interest period
    principal = update_principal(principal, ppmt_fxd, fxd_dur)
    ipmt_var, ppmt_var, pmt_var = get_repayments(principal, var_ir, loan_dur)

    # get total loan repayment value
    var_per    = get_payment_period(loan_dur, fxd_dur)
    loan_total = calculate_total_loan_repayment(pmt_fxd, fxd_per, pmt_var, var_per)

    # concatenate the periods and payments
    ipmt, ppmt, pmt = concatenate_repayments(ipmt_fxd, ppmt_fxd, pmt_fxd, 
                                fxd_per, ipmt_var, ppmt_var, pmt_var, var_per)
    
    return ipmt, ppmt, pmt, per, loan_total


def compare_mortgages(principal, loan_dur, fxd_irs, fxd_durs, fees, var_ir):  
    """
        Compares repayments of mortgages specified in the input
        Args:
            principal - (initial) size of the loan
            loan_dur - duration of the loan in years
            fxd_irs - annual interest rate(s) in percentage form 
            fxd_durs - duration(s) of fixed interest rate repayment period(s)
            fees - additional loan fees charged by the bank or 3rd party
            var_ir - (expected) future/variable annual interest rate 
        Returns
            ipmts - list of lists of monthly interest repayments
            ppmts - list of lists of monthly principal repayments
            pmts - list of total monthly repayments (ipmt + ppmt for a given month)
            pers - list of lists of months during which the loan is paid off
            loan_totals - list of total amounts of money to repay the loans
    """  
    ipmts, ppmts, pmts, pers, loan_totals = [], [], [], [], []
    
    for ind in range(len(fxd_irs)):        
        fxd_ir  = fxd_irs[ind]
        fxd_dur = fxd_durs[ind]

        ipmt, ppmt, pmt, per, ln_total = calculate_mortgage_repayment(
            principal, fxd_ir, loan_dur, var_ir, fxd_dur)
        ln_total += fees[ind]
        
        ipmts.append(ipmt)
        ppmts.append(ppmt)
        pmts.append(pmt)
        pers.append(per)
        loan_totals.append(ln_total)

    return ipmts, ppmts, pmts, pers, loan_totals


def visualize_mortgage_repayment(ipmt, ppmt, pmt, per):
    plt.rcParams["figure.figsize"] = [16,9]
    plt.plot(per, ipmt, label = "Interest payment")
    plt.plot(per, ppmt, label = "Mortgage balance repayment")
    plt.plot(per, pmt, label = "Total repayment")
    plt.xlabel('Months')
    plt.ylabel('Payment ($)')
    plt.title('Mortgage repayment')
    plt.legend()
    plt.show()    


def visualize_mortgage_repayments(pmts, pers, descriptions):
    plt.rcParams["figure.figsize"] = [16,9]
    
    for ind in range(len(pmts)):
        plt.plot(pers[ind], pmts[ind], label=descriptions[ind])
        
    plt.xlabel('Months')
    plt.ylabel('Payment ($)')
    plt.title('Mortgage repayment')
    plt.legend()
    plt.show()  


def visualize_total_repayments(lns, descriptions):
    plt.rcParams["figure.figsize"] = [16,9]
    
    for ind in range(len(lns)):
        plt.plot(ind+1, lns[ind], label=descriptions[ind], markersize=12, marker='o')
        
    plt.xlabel('Loan #')
    plt.ylabel('Total repayment ($)')
    plt.title('Total amount repaid')
    plt.ylim([min(lns) - max(lns)*0.1, max(lns) + max(lns)*0.1])
    plt.legend()
    plt.show()  