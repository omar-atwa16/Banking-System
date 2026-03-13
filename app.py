import streamlit as st
import pandas as pd
import os
import sys
import csv
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
os.makedirs("./Files", exist_ok=True)

st.set_page_config(page_title="Code Bank 🏦", layout="wide")

ACCOUNTS_CSV     = "./Files/accounts.csv"
TRANSACTIONS_CSV = "./Files/transactions.csv"
PINS_CSV         = "./Files/pins.csv"

def read_accounts() -> pd.DataFrame:
    if os.path.exists(ACCOUNTS_CSV):
        df = pd.read_csv(ACCOUNTS_CSV)
        if not df.empty:
            return df
    return pd.DataFrame(columns=["accID", "owner", "accType"])

def read_transactions() -> pd.DataFrame:
    if os.path.exists(TRANSACTIONS_CSV):
        df = pd.read_csv(TRANSACTIONS_CSV)
        if not df.empty:
            return df
    return pd.DataFrame(columns=["transID", "accID", "transType", "amount", "balanceAfter", "timestamp"])

def read_balance(acc_id: int) -> float:
    tx = read_transactions()
    acc_tx = tx[tx["accID"] == acc_id]
    if acc_tx.empty:
        return 0.0
    return float(acc_tx.iloc[-1]["balanceAfter"])

def get_pin(acc_id: int) -> str:
    if os.path.exists(PINS_CSV):
        with open(PINS_CSV, newline="") as f:
            for row in csv.DictReader(f):
                if int(row["accID"]) == acc_id:
                    return row["pin"]
    return "0000"

def save_pin(acc_id: int, pin: str):
    rows = []
    updated = False
    if os.path.exists(PINS_CSV):
        with open(PINS_CSV, newline="") as f:
            rows = list(csv.DictReader(f))
        for row in rows:
            if int(row["accID"]) == acc_id:
                row["pin"] = pin
                updated = True
    if not updated:
        rows.append({"accID": acc_id, "pin": pin})
    with open(PINS_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["accID", "pin"])
        writer.writeheader()
        writer.writerows(rows)

def next_acc_id() -> int:
    df = read_accounts()
    return 1 if df.empty else int(df["accID"].max()) + 1

def next_trans_id() -> int:
    df = read_transactions()
    return 1 if df.empty else int(df["transID"].max()) + 1

def append_account(acc_id: int, owner: str, acc_type: str):
    write_header = not os.path.exists(ACCOUNTS_CSV)
    with open(ACCOUNTS_CSV, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["accID", "owner", "accType"])
        if write_header:
            writer.writeheader()
        writer.writerow({"accID": acc_id, "owner": owner, "accType": acc_type})

def append_transaction(acc_id: int, trans_type: str, amount: float, balance_after: float):
    write_header = not os.path.exists(TRANSACTIONS_CSV)
    with open(TRANSACTIONS_CSV, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["transID", "accID", "transType", "amount", "balanceAfter", "timestamp"])
        if write_header:
            writer.writeheader()
        writer.writerow({
            "transID":      next_trans_id(),
            "accID":        acc_id,
            "transType":    trans_type,
            "amount":       round(amount, 4),
            "balanceAfter": round(balance_after, 4),
            "timestamp":    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

def create_account(owner: str, acc_type: str, init_balance: float, pin: str) -> int:
    pin = str(pin)
    if not pin.isdigit() or len(pin) != 4:
        raise ValueError("PIN must be exactly 4 digits")
    acc_id = next_acc_id()
    append_account(acc_id, owner, acc_type)
    save_pin(acc_id, pin)
    if init_balance > 0:
        append_transaction(acc_id, "Initial Deposit", init_balance, init_balance)
    return acc_id

def do_deposit(acc_id: int, amount: float) -> float:
    if amount <= 0:
        raise ValueError("Amount must be positive")
    balance = read_balance(acc_id)
    new_balance = balance + amount
    append_transaction(acc_id, "Deposit", amount, new_balance)
    return new_balance

def get_overdraft_limit(acc_id: int) -> float:
    tx = read_transactions()
    acc_tx = tx[tx["accID"] == acc_id]
    if acc_tx.empty:
        return 0.0
    first = acc_tx.iloc[0]
    if "Initial Deposit" in str(first["transType"]):
        return float(first["amount"]) * 2
    return 0.0

def do_withdraw(acc_id: int, amount: float, acc_type: str) -> float:
    if amount <= 0:
        raise ValueError("Amount must be positive")
    balance = read_balance(acc_id)
    if acc_type == "OverDraftAccount":
        od_limit = get_overdraft_limit(acc_id)
        if amount > balance + od_limit:
            raise ValueError(f"Exceeds overdraft limit. Max withdrawal: ${balance + od_limit:,.2f}")
    else:
        if amount > balance:
            raise ValueError(f"Insufficient funds. Balance: ${balance:,.2f}")
    new_balance = balance - amount
    append_transaction(acc_id, "Withdraw", amount, new_balance)
    return new_balance

def do_transfer(from_id: int, to_id: int, amount: float, from_type: str):
    if amount <= 0:
        raise ValueError("Amount must be positive")
    from_bal = read_balance(from_id)
    to_bal   = read_balance(to_id)
    if from_type == "OverDraftAccount":
        od_limit = get_overdraft_limit(from_id)
        if amount > from_bal + od_limit:
            raise ValueError("Exceeds overdraft limit.")
    else:
        if amount > from_bal:
            raise ValueError(f"Insufficient funds. Balance: ${from_bal:,.2f}")
    append_transaction(from_id, f"Transfer Out -> #{to_id}",  amount, from_bal - amount)
    append_transaction(to_id,   f"Transfer In <- #{from_id}", amount, to_bal + amount)

if "logged_in_id" not in st.session_state:
    st.session_state.logged_in_id = None

st.title("🏦 Code Bank")

tab1, tab2, tab3, tab4 = st.tabs(["📁 Accounts", "⚙️ Admin", "👤 My Account", "📋 Logs"])


# ══════════════════════════════════════════
# TAB 1 — Accounts
# ══════════════════════════════════════════
with tab1:
    st.subheader("Open a New Account")

    c1, c2 = st.columns(2)
    with c1:
        owner_name   = st.text_input("Owner Name")
        acc_type_sel = st.selectbox("Account Type", ["Account", "SavingAccount", "OverDraftAccount"])
    with c2:
        init_balance = st.number_input("Initial Balance ($)", min_value=0.0, value=0.0, step=100.0)
        pin_input    = st.text_input("4-Digit PIN", type="password", max_chars=4, placeholder="0000")

    if st.button("Open Account"):
        if not owner_name.strip():
            st.error("Please enter an owner name.")
        else:
            pin = pin_input if pin_input else "0000"
            try:
                acc_id = create_account(owner_name.strip(), acc_type_sel, init_balance, pin)
                st.success(f"✅ Account #{acc_id} opened for **{owner_name.strip()}** ({acc_type_sel})")
                st.rerun()
            except ValueError as e:
                st.error(str(e))

    st.divider()
    st.subheader("All Accounts")

    df = read_accounts()
    if df.empty:
        st.info("No accounts yet. Create one above.")
    else:
        df_display = df.copy()
        df_display["balance"] = df_display["accID"].apply(lambda i: f"${read_balance(int(i)):,.2f}")
        st.dataframe(df_display, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("🧪 Showcase")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Apply Monthly Interest** — all Saving Accounts (7% p.a.)")
        if st.button("📈 Apply Interest", use_container_width=True):
            df = read_accounts()
            saving_accs = df[df["accType"] == "SavingAccount"]
            if saving_accs.empty:
                st.warning("No Saving Accounts found.")
            else:
                for _, row in saving_accs.iterrows():
                    acc_id   = int(row["accID"])
                    balance  = read_balance(acc_id)
                    interest = round(balance * (0.07 / 12), 4)
                    append_transaction(acc_id, "Interest Applied", interest, round(balance + interest, 4))
                st.success(f"✅ Interest applied to {len(saving_accs)} Saving Account(s).")
                st.rerun()

    with col2:
        st.write("**Pay Annual Fees ($120)** — all OverDraft Accounts")
        if st.button("💳 Charge Annual Fees", use_container_width=True):
            df = read_accounts()
            od_accs = df[df["accType"] == "OverDraftAccount"]
            if od_accs.empty:
                st.warning("No OverDraft Accounts found.")
            else:
                for _, row in od_accs.iterrows():
                    acc_id  = int(row["accID"])
                    balance = read_balance(acc_id)
                    append_transaction(acc_id, "Annual Fee", 120, round(balance - 120, 4))
                st.success(f"✅ Annual fee charged to {len(od_accs)} OverDraft Account(s).")
                st.rerun()


# ══════════════════════════════════════════
# TAB 2 — Admin
# ══════════════════════════════════════════
with tab2:
    st.subheader("Admin Panel")

    df = read_accounts()
    if df.empty:
        st.info("No accounts yet.")
    else:
        acc_options = {
            f"#{int(row['accID'])} · {row['owner']} ({row['accType']})": int(row["accID"])
            for _, row in df.iterrows()
        }

        c1, c2 = st.columns(2)
        with c1:
            operation = st.selectbox("Operation", ["Deposit", "Withdraw", "Transfer", "Apply Interest", "View Info"])
        with c2:
            sel_label = st.selectbox("Account", list(acc_options.keys()))

        sel_id   = acc_options[sel_label]
        sel_row  = df[df["accID"] == sel_id].iloc[0]
        sel_type = sel_row["accType"]

        st.divider()

        if operation == "Deposit":
            amount = st.number_input("Amount ($)", min_value=0.01, value=100.0, step=50.0, key="adep")
            if st.button("Deposit", key="adep_btn"):
                try:
                    new_bal = do_deposit(sel_id, amount)
                    st.success(f"Deposited ${amount:,.2f} → New balance: ${new_bal:,.2f}")
                except ValueError as e:
                    st.error(str(e))

        elif operation == "Withdraw":
            amount = st.number_input("Amount ($)", min_value=0.01, value=100.0, step=50.0, key="awd")
            if st.button("Withdraw", key="awd_btn"):
                try:
                    new_bal = do_withdraw(sel_id, amount, sel_type)
                    st.success(f"Withdrew ${amount:,.2f} → New balance: ${new_bal:,.2f}")
                except ValueError as e:
                    st.error(str(e))

        elif operation == "Transfer":
            others = {
                f"#{int(row['accID'])} · {row['owner']}": int(row["accID"])
                for _, row in df.iterrows() if int(row["accID"]) != sel_id
            }
            if not others:
                st.info("Need at least 2 accounts for transfers.")
            else:
                recv_label = st.selectbox("Transfer To", list(others.keys()))
                recv_id    = others[recv_label]
                amount     = st.number_input("Amount ($)", min_value=0.01, value=100.0, step=50.0, key="atr")
                if st.button("Transfer", key="atr_btn"):
                    try:
                        do_transfer(sel_id, recv_id, amount, sel_type)
                        st.success(f"Transferred ${amount:,.2f} to #{recv_id}")
                    except ValueError as e:
                        st.error(str(e))

        elif operation == "Apply Interest":
            if sel_type != "SavingAccount":
                st.warning("Only Saving Accounts earn interest (7% p.a.).")
            else:
                balance = read_balance(sel_id)
                monthly_interest = balance * (0.07 / 12)
                st.info(f"Current balance: **${balance:,.2f}** · Monthly interest: **${monthly_interest:,.4f}**")
                if st.button("Apply Monthly Interest"):
                    new_bal = balance + monthly_interest
                    append_transaction(sel_id, "Interest Applied", round(monthly_interest, 4), new_bal)
                    st.success(f"Interest of ${monthly_interest:,.4f} applied → Balance: ${new_bal:,.2f}")

        elif operation == "View Info":
            balance = read_balance(sel_id)
            c1, c2, c3 = st.columns(3)
            c1.metric("Account ID", sel_id)
            c2.metric("Owner",      sel_row["owner"])
            c3.metric("Balance",    f"${balance:,.2f}")
            if sel_type == "SavingAccount":
                st.metric("Annual Interest Rate", "7%")
            if sel_type == "OverDraftAccount":
                st.metric("Overdraft Limit", f"${get_overdraft_limit(sel_id):,.2f}")
            st.write("**Transaction History**")
            tx = read_transactions()
            acc_tx = tx[tx["accID"] == sel_id].sort_values("transID", ascending=False)
            if acc_tx.empty:
                st.info("No transactions yet.")
            else:
                st.dataframe(acc_tx, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════
# TAB 3 — My Account
# ══════════════════════════════════════════
with tab3:
    if st.session_state.logged_in_id is None:
        st.subheader("Customer Sign In")

        c1, c2 = st.columns(2)
        with c1:
            login_id = st.number_input("Account ID", min_value=1, step=1, value=1)
        with c2:
            login_pin = st.text_input("PIN", type="password", max_chars=4)

        if st.button("Sign In"):
            df = read_accounts()
            if df.empty or login_id not in df["accID"].values:
                st.error("Account not found.")
            elif login_pin == get_pin(int(login_id)):
                st.session_state.logged_in_id = int(login_id)
                st.rerun()
            else:
                st.error("Incorrect PIN.")
    else:
        uid  = st.session_state.logged_in_id
        df   = read_accounts()

        if uid not in df["accID"].values:
            st.error("Account no longer exists.")
            st.session_state.logged_in_id = None
        else:
            urow  = df[df["accID"] == uid].iloc[0]
            ubal  = read_balance(uid)
            utype = urow["accType"]

            c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
            with c1:
                st.subheader(f"Welcome, {urow['owner']} 👋")
            with c4:
                if st.button("Sign Out"):
                    st.session_state.logged_in_id = None
                    st.rerun()

            m1, m2, m3 = st.columns(3)
            m1.metric("Account #",    uid)
            m2.metric("Account Type", utype)
            m3.metric("Balance",      f"${ubal:,.2f}")

            if utype == "OverDraftAccount":
                od = get_overdraft_limit(uid)
                st.caption(f"Overdraft limit: ${od:,.2f} · Available: ${ubal + od:,.2f}")
            if utype == "SavingAccount":
                st.caption(f"Annual interest: 7% · Monthly: ${ubal * (0.07/12):,.2f}")

            st.divider()

            op1, op2, op3, op4, op5 = st.tabs(["Deposit", "Withdraw", "Transfer", "History", "Change PIN"])

            with op1:
                dep_amt = st.number_input("Amount ($)", min_value=0.01, value=100.0, step=50.0, key="udep")
                if st.button("Deposit", key="udep_btn"):
                    try:
                        new_bal = do_deposit(uid, dep_amt)
                        st.success(f"Deposited ${dep_amt:,.2f} → Balance: ${new_bal:,.2f}")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))

            with op2:
                wd_amt = st.number_input("Amount ($)", min_value=0.01, value=100.0, step=50.0, key="uwd")
                if st.button("Withdraw", key="uwd_btn"):
                    try:
                        new_bal = do_withdraw(uid, wd_amt, utype)
                        st.success(f"Withdrew ${wd_amt:,.2f} → Balance: ${new_bal:,.2f}")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))

            with op3:
                other_accs = {
                    f"#{int(row['accID'])} · {row['owner']} ({row['accType']})": int(row["accID"])
                    for _, row in df.iterrows() if int(row["accID"]) != uid
                }
                if not other_accs:
                    st.info("No other accounts to transfer to.")
                else:
                    tr_target = st.selectbox("Send To", list(other_accs.keys()))
                    tr_amt    = st.number_input("Amount ($)", min_value=0.01, value=100.0, step=50.0, key="utr")
                    if st.button("Send Transfer", key="utr_btn"):
                        try:
                            do_transfer(uid, other_accs[tr_target], tr_amt, utype)
                            st.success(f"Sent ${tr_amt:,.2f} to {tr_target}")
                            st.rerun()
                        except ValueError as e:
                            st.error(str(e))

            with op4:
                tx = read_transactions()
                acc_tx = tx[tx["accID"] == uid].sort_values("transID", ascending=False)
                if acc_tx.empty:
                    st.info("No transactions yet.")
                else:
                    st.dataframe(acc_tx, use_container_width=True, hide_index=True)

            with op5:
                old_p  = st.text_input("Current PIN",    type="password", max_chars=4, key="op")
                new_p  = st.text_input("New PIN",        type="password", max_chars=4, key="np")
                new_p2 = st.text_input("Confirm New PIN",type="password", max_chars=4, key="np2")
                if st.button("Update PIN"):
                    if new_p != new_p2:
                        st.error("New PINs don't match.")
                    elif old_p != get_pin(uid):
                        st.error("Current PIN is incorrect.")
                    elif not new_p.isdigit() or len(new_p) != 4:
                        st.error("PIN must be exactly 4 digits.")
                    else:
                        save_pin(uid, new_p)
                        st.success("PIN updated successfully.")


# ══════════════════════════════════════════
# TAB 4 — Logs
# ══════════════════════════════════════════
with tab4:
    st.subheader("Transaction Logs")

    if st.button("🔄 Refresh"):
        st.rerun()

    tx_df = read_transactions()

    if tx_df.empty:
        st.info("No transactions recorded yet.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Transactions", len(tx_df))
        c2.metric("Total Deposited",  f"${tx_df[tx_df['transType']=='Deposit']['amount'].astype(float).sum():,.2f}")
        c3.metric("Total Withdrawn",  f"${tx_df[tx_df['transType']=='Withdraw']['amount'].astype(float).sum():,.2f}")
        c4.metric("Transfers Out",    tx_df[tx_df["transType"].str.contains("Transfer Out", na=False)].shape[0])

        st.divider()

        f1, f2 = st.columns(2)
        with f1:
            filter_type = st.selectbox("Filter by Type", ["All"] + sorted(tx_df["transType"].unique().tolist()))
        with f2:
            filter_acc = st.selectbox("Filter by Account ID", ["All"] + sorted(tx_df["accID"].astype(str).unique().tolist()))

        filtered = tx_df.copy()
        if filter_type != "All":
            filtered = filtered[filtered["transType"] == filter_type]
        if filter_acc != "All":
            filtered = filtered[filtered["accID"].astype(str) == filter_acc]

        st.dataframe(filtered.sort_values("transID", ascending=False), use_container_width=True, hide_index=True)