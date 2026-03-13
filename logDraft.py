# Basic libraries
import csv
import os
from datetime import datetime

class CSVHandler:
    transCounter = 1
    def __init__(self):
        self.accountsCSV = "accounts.csv"
        self.transactionsCSV = "transactions.csv"
        self.accountsFields = ['accID', 'owner', 'accType', 'balance']
        self.transactionsFields = ['transID', 'accID', 'transType', 'amount', 'balanceAfter', 'timestamp']
        self.transID = CSVHandler.transCounter
        CSVHandler.transCounter += 1

    def saveAccount(self, account):
        rows = []
        if os.path.exists(self.accountsCSV):
            with open(self.accountsCSV, newline="") as f:
                rows = list(csv.DictReader(f))
        
        updated = False
        for row in rows:
            if int(row['accID']) == account.getID():
                row['balance'] = account.getBalance()
                updated = True
                break
        
        if not updated:
            rows.append({
                'accID': account.getID(),
                'owner': account.getOwner(),
                'accType': account.__class__.__name__,
                'balance': account.getBalance()
            })

        with open(self.accountsCSV, mode="w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.accountsFields)
            writer.writeheader()
            writer.writerows(rows)

    def log(self, accID, transType, amount, balance):
        rows = []
        if os.path.exists(self.transactionsCSV):
            with open(self.transactionsCSV, newline="") as f:
                rows = list(csv.DictReader(f))

        # FIX 1: append was inside the if block, so it only ran when the file
        # already existed. Moved it outside so it always appends.
        rows.append({
            'transID' : self.transID,
            'accID' : accID,
            'transType' : transType,
            'amount' : amount,
            'balanceAfter' : balance,
            'timestamp' : datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # FIX 2: timestamp field was missing entirely
        })

        # FIX 3: write-back was missing — rows were never saved to the file
        with open(self.transactionsCSV, mode="w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.transactionsFields)
            writer.writeheader()
            writer.writerows(rows)

        # FIX 4: transID never incremented after logging, so every transaction
        # got the same ID
        CSVHandler.transCounter += 1
        self.transID = CSVHandler.transCounter