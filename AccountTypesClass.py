# Importing the Account class
from AccountClass import Account

# Inheriting from the Account class with additional attribute
class SavingAccount(Account):
    annualInterest = 0.07

    def __init__(self, owner, balance=0, pin="0000"):
        super().__init__(owner, balance, pin)
        self.interestRate = SavingAccount.annualInterest

    # Calculating interest and adding it to the balance
    def applyInterest(self):
        monthlyInterest = self.interestRate / 12
        interest = self.getBalance() * monthlyInterest
        oldBalance = self.getBalance()
        self.setBalance(self.getBalance() + interest)
        print(
            f"Interest of ${interest:.2f} applied to #{self.getID()}"
            f"\nOld Balance: {oldBalance}\nNew Balance: {self.getBalance():.2f}"
        )

    # Overriding the function just to show the interest
    def displayAccInfo(self):
        print("=" * 7, f"Account #{self.getID()} Info:", "=" * 7)
        print(f"Owner: {self.getOwner()}")
        print(f"Account Type: {self.accType}")
        print(f"Annual Interest Rate: {self.interestRate}")
        print(f"Annual Interest Amount: {self.getBalance() * self.annualInterest}")
        print(f"Balance: {self.getBalance()}")


# Inheriting from the Account class with additional attribute
class OverDraftAccount(Account):
    annualFees = 120

    def __init__(self, owner, balance=0, pin="0000"):
        super().__init__(owner, balance, pin)
        self.overdraftLimit = self.getBalance() * 2

    def payAnnualFees(self):
        self.setBalance(self.getBalance() - OverDraftAccount.annualFees)

    # Overriding the function to allow negatives, and the withdraw amount check is considering the overdraft limit
    def withdraw(self, amount: float):
        if amount <= 0:
            raise ValueError("Withdraw amount must be positive")
        if amount > self.getBalance() + self.overdraftLimit:
            raise ValueError(
                f"Exceeds overdraft limit. Max withdrawal: "
                f"${self.getBalance() + self.overdraftLimit:,.2f}"
            )
        self.setBalance(self.getBalance() - amount, negatives=True)
        self._Account__transactions.append(f"Withdrew: -${amount}   Balance: {self.getBalance()}")
        Account.logger.log(self.getID(), "Withdraw", amount, self.getBalance())
        print(f"Withdrew ${amount} from #{self.getID()}")
        print(f"Balance Available: {self.getBalance()}")

    # Overriding the function to show the overdraft limit
    def displayAccInfo(self):
        print("=" * 7, f"Account #{self.getID()} Info:", "=" * 7)
        print(f"Owner: {self.getOwner()}")
        print(f"Account Type: {self.accType}")
        print(f"Balance: {self.getBalance()}")
        print(f"Over Draft Limit: {self.overdraftLimit}")