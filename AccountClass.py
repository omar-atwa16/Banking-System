# Importing the Logging class
from loggingClass import CSVHandler

class Account:
    idCounter = 1
    logger = CSVHandler()

    def __init__(self, owner, balance=0, pin="0000"):
        self.__id = Account.idCounter
        Account.idCounter += 1
        self.__owner = owner
        self.__balance = balance
        self.__pin = self.validatePin(pin)
        self.__transactions = []
        self.accType = self.__class__.__name__
        Account.logger.saveAccount(self)

    # Getters and Setters
    def getID(self):
        return self.__id

    def getOwner(self):
        return self.__owner

    def getBalance(self):
        return self.__balance

    #  Negatives attribute for Overdraft Accounts
    def setBalance(self, amount, negatives=False):
        if not negatives and amount < 0:
            raise ValueError("Balance must be positive")
        self.__balance = amount

    # Making sure pins are consistent
    def validatePin(self, pin):
        pin = str(pin)
        if not pin.isdigit() or len(pin) != 4:
            raise ValueError("PIN must be exactly 4 numbers")
        return pin
    
    def getPin(self):
        return self.__pin
    
    def setPin(self, oldPin, newPin):
        if oldPin != self.__pin:
            raise ValueError("Current PIN is incorrect")
        self.__pin = self.validatePin(newPin)
        print(f"PIN updated for #{self.getID()}")

    #####Separator#####

    # Transactions Functions
    def deposit(self, amount: float):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.setBalance(self.getBalance() + amount)
        self.__transactions.append(f"Deposit: +${amount}    Balance: {self.getBalance()}")
        Account.logger.log(self.getID(), "Deposit", amount, self.getBalance())        
        print(f"Deposited ${amount} into #{self.getID()}")
        print(f"Balance Available: {self.getBalance()}")

    def withdraw(self, amount: float):
        if amount <= 0:
            raise ValueError("Withdraw amount must be positive")
        if amount > self.getBalance():
            raise ValueError(f"Insufficient funds.\nBalance Available: {self.getBalance()}")
        self.setBalance(self.getBalance() - amount)
        self.__transactions.append(f"Withdrew: -${amount}   Balance: {self.getBalance()}")
        Account.logger.log(self.getID(), "Withdraw", amount, self.getBalance())
        print(f"Withdrew ${amount} from #{self.getID()}")
        print(f"Balance Available: {self.getBalance()}")

    def transfer(self, receiver: "Account", amount: float):
        if amount <= 0:
            raise ValueError("Transfer amount must be positive")
        if amount > self.getBalance():
            raise ValueError(f"Insufficient funds.\nBalance Available: {self.getBalance()}")
        self.setBalance(self.getBalance() - amount)
        receiver.setBalance(receiver.getBalance() + amount)
        self.__transactions.append(f"Transferred ${amount} to {receiver.getID()}    Balance: {self.getBalance()}")
        receiver.__transactions.append(f"Received: ${amount} from {self.getID()}    Balance: {receiver.getBalance()}")
        Account.logger.log(self.getID(), f"Transfer Out -> #{receiver.getID()}", amount, self.getBalance())
        Account.logger.log(receiver.getID(), f"Transfer In <- #{self.getID()}", amount, receiver.getBalance())
        print(f"Transferred ${amount} from #{self.getID()} to #{receiver.getID()}")

    # Loooop over the transactions list for an Account
    def TransactionHistory(self):
        print("=" * 7, f"Transaction History for #{self.getID()}:", "=" * 7)

        if not self.__transactions:
            print("No transactions yet.")
        else:
            for transaction in self.__transactions:
                print(transaction)

    def displayAccInfo(self):
        print("=" * 7, f"Account #{self.getID()} Info:", "=" * 7)
        print(f"Owner: {self.getOwner()}")
        print(f"Account Type: {self.accType}")
        print(f"Balance: {self.getBalance()}")