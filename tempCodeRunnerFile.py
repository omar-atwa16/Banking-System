import os
import csv

# Clean CSV files BEFORE importing Account (which triggers CSVHandler init)
for _f in ["accounts.csv", "transactions.csv"]:
    if os.path.exists(_f):
        os.remove(_f)

from AccountClass import Account
from AccountTypesClass import SavingAccount, OverDraftAccount
from BankClass import Bank

# ─────────────────────────────────────────────
#  Terminal Colors & Helpers
# ─────────────────────────────────────────────

PASS    = "\033[92m[PASS]\033[0m"
FAIL    = "\033[91m[FAIL]\033[0m"
SECTION = "\033[94m"
YELLOW  = "\033[93m"
RESET   = "\033[0m"

results = []

def section(title):
    print(f"\n{SECTION}{'═'*60}")
    print(f"  {title}")
    print(f"{'═'*60}{RESET}")

def expect_pass(label, fn):
    try:
        fn()
        print(f"  {PASS}  {label}")
        results.append((True, label))
    except Exception as e:
        print(f"  {FAIL}  {label}")
        print(f"         ↳ Unexpected exception: {e}")
        results.append((False, label))

def expect_fail(label, fn, exc_type=Exception):
    try:
        fn()
        print(f"  {FAIL}  {label}")
        print(f"         ↳ Expected {exc_type.__name__} but nothing was raised")
        results.append((False, label))
    except exc_type as e:
        print(f"  {PASS}  {label}")
        print(f"         ↳ Caught expected {exc_type.__name__}: {e}")
        results.append((True, label))
    except Exception as e:
        print(f"  {FAIL}  {label}")
        print(f"         ↳ Wrong exception type: {type(e).__name__}: {e}")
        results.append((False, label))

def assert_equal(label, got, expected):
    if got == expected:
        print(f"  {PASS}  {label}  (got: {got})")
        results.append((True, label))
    else:
        print(f"  {FAIL}  {label}")
        print(f"         ↳ Expected {expected!r}, got {got!r}")
        results.append((False, label))

def assert_true(label, condition, detail=""):
    if condition:
        print(f"  {PASS}  {label}")
        results.append((True, label))
    else:
        print(f"  {FAIL}  {label}" + (f"\n         ↳ {detail}" if detail else ""))
        results.append((False, label))

# ─────────────────────────────────────────────
#  Reset state for deterministic IDs
# ─────────────────────────────────────────────
Account.idCounter = 1




# ════════════════════════════════════════════════════════════
#  1. ACCOUNT — Construction & Getters
# ════════════════════════════════════════════════════════════
section("1. Account — Construction & Getters")

a1 = Account("Omar", 1000)
a2 = Account("Ahmed")

assert_equal("getOwner() returns correct name",       a1.getOwner(),   "Omar")
assert_equal("getBalance() returns initial balance",  a1.getBalance(), 1000)
assert_equal("getID() starts at 1",                   a1.getID(),      1)
assert_equal("Second account ID is 2",                a2.getID(),      2)
assert_equal("Default balance is 0",                  a2.getBalance(), 0)
assert_equal("accType reflects class name",           a1.accType,      "Account")


# ════════════════════════════════════════════════════════════
#  2. ACCOUNT — setBalance
# ════════════════════════════════════════════════════════════
section("2. Account — setBalance")

expect_pass("setBalance(500) works",          lambda: a1.setBalance(500))
assert_equal("Balance updated to 500",         a1.getBalance(), 500)
expect_pass("setBalance(0) allowed",          lambda: a1.setBalance(0))
assert_equal("Balance updated to 0",           a1.getBalance(), 0)
expect_fail("setBalance(-1) raises ValueError", lambda: a1.setBalance(-1), ValueError)
a1.setBalance(1000)  # restore


# ════════════════════════════════════════════════════════════
#  3. ACCOUNT — PIN Validation
# ════════════════════════════════════════════════════════════
section("3. Account — PIN Validation")

expect_pass("Account created with valid PIN '1234'",
    lambda: Account("PinUser", 0, "1234"))

expect_fail("PIN with letters raises ValueError",
    lambda: Account("Bad", 0, "abcd"), ValueError)

expect_fail("PIN shorter than 4 digits raises ValueError",
    lambda: Account("Bad", 0, "123"), ValueError)

expect_fail("PIN longer than 4 digits raises ValueError",
    lambda: Account("Bad", 0, "12345"), ValueError)

expect_fail("Empty PIN raises ValueError",
    lambda: Account("Bad", 0, ""), ValueError)

pin_acc = Account("PinChanger", 100, "1111")
expect_pass("setPin with correct old PIN works",
    lambda: pin_acc.setPin("1111", "2222"))
assert_equal("PIN updated correctly", pin_acc.getPin(), "2222")

expect_fail("setPin with wrong old PIN raises ValueError",
    lambda: pin_acc.setPin("0000", "3333"), ValueError)


# ════════════════════════════════════════════════════════════
#  4. ACCOUNT — Deposit
# ════════════════════════════════════════════════════════════
section("4. Account — Deposit")

a1.setBalance(1000)

expect_pass("Deposit 200 succeeds",              lambda: a1.deposit(200))
assert_equal("Balance is 1200 after deposit",     a1.getBalance(), 1200)
expect_pass("Deposit float amount (0.99)",        lambda: a1.deposit(0.99))
assert_equal("Balance after float deposit",       a1.getBalance(), 1200.99)
expect_fail("Deposit 0 raises ValueError",        lambda: a1.deposit(0),   ValueError)
expect_fail("Deposit negative raises ValueError", lambda: a1.deposit(-50), ValueError)

a1.setBalance(1000)  # restore


# ════════════════════════════════════════════════════════════
#  5. ACCOUNT — Withdraw
# ════════════════════════════════════════════════════════════
section("5. Account — Withdraw")

a1.setBalance(1000)

expect_pass("Withdraw 300 succeeds",                      lambda: a1.withdraw(300))
assert_equal("Balance is 700 after withdrawal",            a1.getBalance(), 700)
expect_pass("Withdraw float amount (0.50)",                lambda: a1.withdraw(0.50))
expect_fail("Withdraw more than balance raises ValueError", lambda: a1.withdraw(9999),  ValueError)
expect_fail("Withdraw 0 raises ValueError",                lambda: a1.withdraw(0),      ValueError)
expect_fail("Withdraw negative raises ValueError",         lambda: a1.withdraw(-100),   ValueError)

# Exact balance withdrawal
exact = Account("Exact", 250)
expect_pass("Withdraw exactly full balance",  lambda: exact.withdraw(250))
assert_equal("Balance is 0 after exact withdrawal", exact.getBalance(), 0)

a1.setBalance(1000)  # restore


# ════════════════════════════════════════════════════════════
#  6. ACCOUNT — Transfer
# ════════════════════════════════════════════════════════════
section("6. Account — Transfer")

a1.setBalance(500)
a2.setBalance(200)

expect_pass("Transfer 100 from a1 to a2 succeeds", lambda: a1.transfer(a2, 100))
assert_equal("Sender balance reduced by 100",       a1.getBalance(), 400)
assert_equal("Receiver balance increased by 100",   a2.getBalance(), 300)

expect_fail("Transfer more than balance raises ValueError", lambda: a1.transfer(a2, 9999), ValueError)
expect_fail("Transfer 0 raises ValueError",                 lambda: a1.transfer(a2, 0),    ValueError)
expect_fail("Transfer negative raises ValueError",          lambda: a1.transfer(a2, -10),  ValueError)

# Large transfer
big1 = Account("Rich", 1_000_000)
big2 = Account("Receiver", 0)
expect_pass("Transfer large amount works",        lambda: big1.transfer(big2, 999_999))
assert_equal("Large transfer sender balance",      big1.getBalance(), 1)
assert_equal("Large transfer receiver balance",    big2.getBalance(), 999_999)

# Transfer to self
self_acc = Account("SelfUser", 300)
expect_pass("Transfer to self doesn't crash",     lambda: self_acc.transfer(self_acc, 100))

a1.setBalance(500)  # restore


# ════════════════════════════════════════════════════════════
#  7. ACCOUNT — Transaction History
# ════════════════════════════════════════════════════════════
section("7. Account — Transaction History")

fresh = Account("Fresh", 0)
expect_pass("TransactionHistory on new account (no transactions)",
    lambda: fresh.TransactionHistory())

fresh.deposit(100)
fresh.withdraw(50)
fresh.transfer(a2, 25)
expect_pass("TransactionHistory after deposit/withdraw/transfer",
    lambda: fresh.TransactionHistory())


# ════════════════════════════════════════════════════════════
#  8. ACCOUNT — displayAccInfo
# ════════════════════════════════════════════════════════════
section("8. Account — displayAccInfo")

expect_pass("displayAccInfo runs without error", lambda: a1.displayAccInfo())


# ════════════════════════════════════════════════════════════
#  9. SAVING ACCOUNT — Construction & Interest
# ════════════════════════════════════════════════════════════
section("9. SavingAccount — Construction & Interest")

s1 = SavingAccount("Sara", 1200)
assert_equal("accType is SavingAccount",      s1.accType,      "SavingAccount")
assert_equal("Annual interest rate is 0.07",  s1.interestRate, 0.07)
assert_equal("Initial balance is 1200",       s1.getBalance(), 1200)

expected_interest = 1200 * (0.07 / 12)
before = s1.getBalance()
expect_pass("applyInterest() executes without error", lambda: s1.applyInterest())
assert_equal("Balance after interest is correct",
    round(s1.getBalance(), 10), round(before + expected_interest, 10))

expect_pass("SavingAccount displayAccInfo runs", lambda: s1.displayAccInfo())

s1.setBalance(500)
expect_pass("SavingAccount deposit works",  lambda: s1.deposit(100))
expect_pass("SavingAccount withdraw works", lambda: s1.withdraw(50))
expect_fail("SavingAccount overdraft raises ValueError",
    lambda: s1.withdraw(999999), ValueError)


# ════════════════════════════════════════════════════════════
#  10. SAVING ACCOUNT — Compounding (3 months)
# ════════════════════════════════════════════════════════════
section("10. SavingAccount — 3-Month Compounding Interest")

comp = SavingAccount("Comp", 10_000)
for month in range(1, 4):
    comp.applyInterest()
    print(f"         Month {month} balance: ${comp.getBalance():.4f}")

expected_after_3 = 10_000 * ((1 + 0.07/12) ** 3)
assert_equal("3-month compounded balance correct",
    round(comp.getBalance(), 4), round(expected_after_3, 4))


# ════════════════════════════════════════════════════════════
#  11. OVERDRAFT ACCOUNT — Construction & Withdraw
# ════════════════════════════════════════════════════════════
section("11. OverDraftAccount — Construction & Overdraft Withdraw")

od1 = OverDraftAccount("Ali", 500)
assert_equal("accType is OverDraftAccount",  od1.accType,      "OverDraftAccount")
assert_equal("Overdraft limit = balance * 2", od1.overdraftLimit, 1000)

# Withdraw within balance
od1._Account__balance = 500
expect_pass("Withdraw within balance works",       lambda: od1.withdraw(300))
assert_equal("Balance after normal withdrawal",     od1.getBalance(), 200)

# Withdraw into overdraft
od1._Account__balance = 500
od1.overdraftLimit    = 1000
expect_pass("Withdraw into overdraft (within limit) works", lambda: od1.withdraw(1200))
assert_equal("Balance goes negative (overdraft used)",       od1.getBalance(), -700)

# Exceed overdraft limit
od1._Account__balance = 500
od1.overdraftLimit    = 1000
expect_fail("Withdraw exceeding overdraft limit raises ValueError",
    lambda: od1.withdraw(9999), ValueError)

expect_fail("Withdraw 0 raises ValueError",
    lambda: od1.withdraw(0), ValueError)

expect_fail("Withdraw negative raises ValueError",
    lambda: od1.withdraw(-100), ValueError)

expect_pass("OverDraftAccount displayAccInfo runs", lambda: od1.displayAccInfo())


# ════════════════════════════════════════════════════════════
#  12. BANK CLASS
# ════════════════════════════════════════════════════════════
section("12. Bank — openAccount / getAccount / displayAllAccounts")

bank = Bank()
b1   = Account("Layla", 800)
b2   = SavingAccount("Nour", 3000)
b3   = OverDraftAccount("Ziad", 600)

expect_pass("openAccount(regular) works",   lambda: bank.openAccount(b1))
expect_pass("openAccount(saving) works",    lambda: bank.openAccount(b2))
expect_pass("openAccount(overdraft) works", lambda: bank.openAccount(b3))

assert_equal("Bank holds 3 accounts",       len(bank.accounts), 3)
assert_equal("Bank name is always 'Code Bank'", bank.name, "Code Bank")

found = bank.getAccount(b1.getID())
assert_equal("getAccount returns correct owner", found.getOwner(), "Layla")

expect_fail("getAccount with invalid ID raises KeyError",
    lambda: bank.getAccount(9999), KeyError)

expect_pass("displayAllAccounts runs without error",
    lambda: bank.displayAllAccounts())


# ════════════════════════════════════════════════════════════
#  13. CSV LOGGING — accounts.csv
# ════════════════════════════════════════════════════════════
section("13. CSV Logging — accounts.csv")

assert_true("accounts.csv file exists", os.path.exists("./Files/accounts.csv"))

with open("./Files/accounts.csv", newline="") as f:
    rows = list(csv.DictReader(f))

assert_true("accounts.csv has rows saved", len(rows) > 0,
    f"Expected rows, got {len(rows)}")

ids_in_csv = [int(r["accID"]) for r in rows]
assert_true("a1 (Account) saved to CSV",          a1.getID() in ids_in_csv)
assert_true("s1 (SavingAccount) saved to CSV",     s1.getID() in ids_in_csv)
assert_true("od1 (OverDraftAccount) saved to CSV", od1.getID() in ids_in_csv)

types_in_csv = {r["accID"]: r["accType"] for r in rows}
assert_equal("SavingAccount type logged correctly",
    types_in_csv.get(str(s1.getID())), "SavingAccount")
assert_equal("OverDraftAccount type logged correctly",
    types_in_csv.get(str(od1.getID())), "OverDraftAccount")


# ════════════════════════════════════════════════════════════
#  14. CSV LOGGING — transactions.csv
# ════════════════════════════════════════════════════════════
section("14. CSV Logging — transactions.csv")

assert_true("transactions.csv file exists", os.path.exists("./Files/transactions.csv"))

with open("./Files/transactions.csv", newline="") as f:
    trans_rows = list(csv.DictReader(f))

assert_true("transactions.csv has entries", len(trans_rows) > 0,
    f"Expected transaction rows, got {len(trans_rows)}")

trans_types = [r["transType"] for r in trans_rows]
assert_true("Deposit transactions logged",  any("Deposit"  in t for t in trans_types))
assert_true("Withdraw transactions logged", any("Withdraw" in t for t in trans_types))
assert_true("Transfer transactions logged", any("Transfer" in t for t in trans_types))

# Verify required fields are present and non-empty
required_fields = ["transID", "accID", "transType", "amount", "balanceAfter", "timestamp"]
for field in required_fields:
    assert_true(f"Field '{field}' present and non-empty in all rows",
        all(r.get(field, "").strip() != "" for r in trans_rows),
        f"Some rows missing '{field}'")

# Verify transIDs are unique
trans_ids = [r["transID"] for r in trans_rows]
assert_true("All transIDs are unique", len(trans_ids) == len(set(trans_ids)))


# ════════════════════════════════════════════════════════════
#  15. EDGE CASES
# ════════════════════════════════════════════════════════════
section("15. Edge Cases & Boundary Conditions")

# Zero-balance account
z = Account("Zero", 0)
expect_fail("Withdraw from zero-balance account raises ValueError",
    lambda: z.withdraw(0.01), ValueError)

# Overdraft with zero balance
oz = OverDraftAccount("OZero", 0)
assert_equal("OverDraft limit on zero-balance account is 0", oz.overdraftLimit, 0)
expect_fail("OverDraft account with 0 limit cannot withdraw anything",
    lambda: oz.withdraw(1), ValueError)

# Multiple deposits then full withdrawal
multi = Account("Multi", 0)
multi.deposit(100)
multi.deposit(200)
multi.deposit(300)
assert_equal("Balance after 3 deposits is 600", multi.getBalance(), 600)
expect_pass("Withdraw full balance after multiple deposits",
    lambda: multi.withdraw(600))
assert_equal("Balance is 0 after full withdrawal", multi.getBalance(), 0)

# Chained transfers A -> B -> C
ca = Account("ChainA", 300)
cb = Account("ChainB", 0)
cc = Account("ChainC", 0)
ca.transfer(cb, 300)
cb.transfer(cc, 300)
assert_equal("Chain transfer: A balance", ca.getBalance(), 0)
assert_equal("Chain transfer: B balance", cb.getBalance(), 0)
assert_equal("Chain transfer: C balance", cc.getBalance(), 300)

# ID auto-increment never resets mid-run
id_before = Account.idCounter
_ = Account("TempA", 0)
_ = Account("TempB", 0)
assert_equal("ID increments correctly after two more accounts",
    Account.idCounter, id_before + 2)


# ════════════════════════════════════════════════════════════
#  SUMMARY
# ════════════════════════════════════════════════════════════
section("TEST SUMMARY")

passed = sum(1 for ok, _ in results if ok)
failed = sum(1 for ok, _ in results if not ok)
total  = len(results)

print(f"\n  Total  : {total}")
print(f"  {PASS} Passed : {passed}")
print(f"  {FAIL} Failed : {failed}")

if failed:
    print(f"\n  {YELLOW}Failed tests:{RESET}")
    for ok, label in results:
        if not ok:
            print(f"    ✗ {label}")

print()

if __name__ == "__main__":
    pass