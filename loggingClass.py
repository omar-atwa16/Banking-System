# Basic libraries
import csv
import os
from datetime import datetime

class CSVHandler:
    transCounter = 1
    def __init__(self):
        self.accountsCSV = "./Files/accounts.csv"
        self.transactionsCSV = "./Files/transactions.csv"
        self.accountsFields = ['accID', 'owner', 'accType', 'balance']
        self.transactionsFields = ['transID', 'accID', 'transType', 'amount', 'balanceAfter', 'timestamp']

        #  Creating the CSV files and writing the headers
        for file, fields in [
            (self.accountsCSV, self.accountsFields),
            (self.transactionsCSV, self.transactionsFields)
        ]:
            if not os.path.exists(file):
                with open(file, mode="w", newline="") as f:
                    csv.DictWriter(f, fieldnames=fields).writeheader()

    # Appending accounts into the accounts CSV
    def saveAccount(self, account):
        with open(self.accountsCSV, mode="a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.accountsFields)
            writer.writerow({
                'accID': account.getID(),
                'owner': account.getOwner(),
                'accType': account.__class__.__name__,
                'balance': account.getBalance() 
            })

    #  Logging transactions
    def log(self, accID, transType, amount, balance):
        with open(self.transactionsCSV, mode="a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.transactionsFields)
            writer.writerow({
                'transID': CSVHandler.transCounter,
                'accID': accID,
                'transType': transType,
                'amount': amount,
                'balanceAfter': balance,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        CSVHandler.transCounter += 1