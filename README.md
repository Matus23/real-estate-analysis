# real-estate-analysis
This repository contains:
* `mortgage_calc.py` - a script which visualizes mortgage repayments and total repaid value. Takes the following parameters:
  * space-separated fixed interest rate(s) in % form 
  * duration of repayment of the mortgage when fixed interest rate applies (in years, usually 2 or 3 years)
  * total duration of the mortgage (in years)
  * initial size of the mortgage
  * initial one-off mortgage fee
  * central bank base interest rate
  * additional interest your bank charges after the fixed interest repayment period is over in % form (e.g. 4.49% at Barclays in May 2022)
* `zoopla_scraper.py` - a web scraper for Zoopla (a real estate website used widely in UK and Europe). Saves the scraped real estate data into a local database. Filters new entries based on listings' ids to avoid duplicate entries. Takes the following parameters: 
  * number of pages to scrape
  * mode: 'sale' (for scraping properties that are for sale) or 'rental' (for scraping properties that are for rent)


Example run of `mortgage_calc.py`:
```
python mortgage_calc.py

Enter space-separated fixed interest rate(s) in % form: 3
Enter duration(s) of fixed interest rate: 10
Enter total loan duration in years: 10
Enter loan principal (initial size of loan): 50000
Enter space-separated loan fee(s): 0
Enter your central bank base interest rate: 2
Enter interest rate your bank charges on top of the central bank base rate: 5
```

Example run of `zoopla_scraper.py`:
```
python zoopla_scraper.py

Enter number of pages to scrape: 2
Enter category ('sale' or 'rental'): sale
```


