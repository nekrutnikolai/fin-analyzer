import numpy as np
import pandas as pd
import locale

## --- USER-MODIFIABLE VALUES --- ##

# specify the exact pathname of the files
checking_loc = '/.../checking.csv' # MODIFY
savings_loc = '/.../savings.csv' # MODIFY
credit_card_loc = '/.../credit_card.csv' # MODIFY

# specify the location of the output file
output_loc = '/.../combined_data.csv' # MODIFY

# current balance of all accounts [modify], all positive numbers
# done because you can't actually download all of your financial data ever
checking_balance = 1000.00 # MODIFY
savings_balance = 1000.00 # MODIFY
credit_balance = 500.00 # MODIFY

# most recent transactions at top of spreadsheet (True)/oldest transactions at top of spreadsheet (False)
reverse_order = True # MODIFY

## --- END OF USER-MODIFIABLE VALUES --- ##

# since we are using USD
locale.setlocale(locale.LC_ALL, 'en_US')

# calculation of the adjusted balance from values specific above
adj_balance = checking_balance + savings_balance - credit_balance

# create the dataframes form the csv files
checking_df = pd.read_csv(checking_loc)
savings_df = pd.read_csv(savings_loc)
credit_card_df = pd.read_csv(credit_card_loc)

# Delete useless columns
del checking_df['Reference No.']
del checking_df['Credits']
del checking_df['Debits']
del checking_df['Transaction Type']
del savings_df['Reference No.']
del savings_df['Credits']
del savings_df['Debits']
del savings_df['Transaction Type']
del credit_card_df['Post Date']

# Rename columns for simplicity
credit_card_df.rename(columns={'Trans. Date': 'Date'}, inplace=True)
checking_df.rename(columns={'Account Type': 'Account'}, inplace=True)
savings_df.rename(columns={'Account Type': 'Account'}, inplace=True)

# Clean up extra spaces
checking_df['Description'] = checking_df['Description'].str.replace(r'\s{2,}', ' ', regex=True)
savings_df['Description'] = checking_df['Description'].str.replace(r'\s{2,}', ' ', regex=True)
#credit_card_df['Description'] = checking_df['Description'].str.replace(r'\s{2,}', ' ', regex=True)

# Keep consistency across columns
checking_df['Category'] = ''
savings_df['Category'] = ''
credit_card_df['Account'] = 'Credit Card'
credit_card_df = credit_card_df.reindex(columns = ['Date', 'Account', 'Description', 'Amount', 'Category'])

# Add dates to the values
checking_df['Date'] = pd.to_datetime(checking_df['Date'])
savings_df['Date'] = pd.to_datetime(savings_df['Date'])
credit_card_df['Date'] = pd.to_datetime(credit_card_df['Date'])

# Reverse the Credit Card values, since positive is spendings and vice-versa
credit_card_df['Amount'] = credit_card_df['Amount'] * -1

# Concatenate the dataframes vertically into a single dataframe
combined_df = pd.concat([checking_df, savings_df, credit_card_df], ignore_index=True)

# Sort the combined DataFrame by the 'Date' column
combined_df.sort_values(by='Date', ascending=True, inplace=True)

# Reset the index (optional)
combined_df.reset_index(drop=True, inplace=True)

# If user specifies most recent transactions at the top
if reverse_order:
    # Now, show the most recent transactions on top
    combined_df.sort_values(by='Date', ascending=False, inplace=True)

    # Calculate the total given the reverse order
    combined_df['Total'] = combined_df.loc[::-1, 'Amount'].cumsum()[::-1]

    # Factor in the adjustment values as the data can be behind & not super current
    combined_df['Total'] += (adj_balance - combined_df['Total'].iloc[0])

# If user wants most recent transactions at the bottom
else:
    # Add the total value column
    combined_df['Total'] = combined_df['Amount'].cumsum()

    # Factor in the adjustment values as the data can be behind & not super current
    combined_df['Total'] += (adj_balance - combined_df['Total'].iloc[-1])

# Convert to USD
combined_df['Amount'] = combined_df['Amount'].apply(lambda x: locale.currency(x, grouping=True))
combined_df['Total'] = combined_df['Total'].apply(lambda x: locale.currency(x, grouping=True))

# re-ordering the columns
combined_df = combined_df.reindex(columns = ['Date', 'Account', 'Category', 'Description', 'Amount', 'Total'])

# Export the combined and sorted DataFrame to a CSV file
# Then, this exported csv can be copied and pasted into a Google Sheet
combined_df.to_csv(output_loc, index=False)