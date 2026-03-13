# Importing the Account class
from AccountClass import Account

# Class to handle all the accounts
class Bank:
    bankName = "Code Bank"

    def __init__(self):
        self.name = Bank.bankName
        self.accounts: dict[int, Account] = {}

    # Adding the account to the bank system
    def openAccount(self, account: Account):
        self.accounts[account.getID()] = account
        print(f"{account.getOwner()} opened {account.accType} #{account.getID()} in {self.name}")

    def getAccount(self, accID):
        if accID not in self.accounts:
            raise KeyError(f"Account #{accID} not found")
        return self.accounts[accID]

    # Looping over the accounts to display info
    def displayAllAccounts(self):
        for acc in self.accounts.values():
            acc.displayAccInfo()
            print("=" * 50)