"""Streamlit ATM app. Run with: streamlit run app.py"""

import streamlit as st
import bank

st.set_page_config(page_title="Python ATM", page_icon="🏧")

if "acc_no" not in st.session_state:
    st.session_state.acc_no = None
if "failed" not in st.session_state:
    st.session_state.failed = 0

users = bank.load_users()


def logout():
    st.session_state.acc_no = None
    st.session_state.failed = 0
    st.rerun()


# ---------- Not logged in ----------
if st.session_state.acc_no is None or st.session_state.acc_no not in users:
    st.title("🏧 Python ATM")
    tab_login, tab_new = st.tabs(["Login", "Create Account"])

    with tab_login:
        with st.form("login_form"):
            acc = st.text_input("Account number")
            pin = st.text_input("PIN", type="password", max_chars=4)
            go = st.form_submit_button("Login")
        if go:
            ok, msg, _ = bank.login(users, acc.strip(), pin, st.session_state.failed)
            if ok:
                st.session_state.acc_no = acc.strip()
                st.session_state.failed = 0
                st.rerun()
            else:
                st.session_state.failed += 1
                st.error(msg)

    with tab_new:
        with st.form("new_form"):
            name = st.text_input("Name")
            new_pin = st.text_input("Set 4-digit PIN", type="password", max_chars=4)
            confirm = st.text_input("Confirm PIN", type="password", max_chars=4)
            opening = st.number_input("Opening deposit (Rs.)", min_value=0.0, step=100.0)
            create = st.form_submit_button("Create account")
        if create:
            if new_pin != confirm:
                st.error("PINs do not match.")
            else:
                ok, result = bank.create_account(users, name, new_pin, opening)
                if ok:
                    st.success(f"Account created! Your account number is {result}. "
                               "Remember it - you need it to log in.")
                else:
                    st.error(result)
    st.stop()

# ---------- Logged in ----------
acc_no = st.session_state.acc_no
user = users[acc_no]

st.sidebar.write(f"**{user['name']}**")
st.sidebar.caption(f"Account: {acc_no}")
page = st.sidebar.radio("Menu", ["Dashboard", "Deposit", "Withdraw",
                                 "Transaction History", "Change PIN", "Delete Account"])
if st.sidebar.button("Logout"):
    logout()

if page == "Dashboard":
    st.title("Dashboard")
    st.metric("Current balance", f"Rs. {user['balance']:,.2f}")
    st.subheader("Mini statement (last 5)")
    last = list(reversed(user["transactions"][-5:]))
    if last:
        st.table(last)
    else:
        st.info("No transactions yet.")

elif page == "Deposit":
    st.title("Deposit")
    with st.form("dep"):
        amt = st.number_input("Amount (Rs.)", min_value=0.0, step=100.0)
        go = st.form_submit_button("Deposit")
    if go:
        ok, msg = bank.deposit(users, user, amt)
        (st.success if ok else st.error)(msg)

elif page == "Withdraw":
    st.title("Withdraw")
    st.caption(f"Available balance: Rs. {user['balance']:,.2f}")
    with st.form("wd"):
        amt = st.number_input("Amount (Rs., multiples of 100)", min_value=0.0, step=100.0)
        go = st.form_submit_button("Withdraw")
    if go:
        ok, msg = bank.withdraw(users, user, amt)
        (st.success if ok else st.error)(msg)

elif page == "Transaction History":
    st.title("Transaction History")
    if user["transactions"]:
        st.dataframe(list(reversed(user["transactions"])), use_container_width=True)
    else:
        st.info("No transactions yet.")

elif page == "Change PIN":
    st.title("Change PIN")
    with st.form("pin"):
        cur = st.text_input("Current PIN", type="password", max_chars=4)
        new = st.text_input("New 4-digit PIN", type="password", max_chars=4)
        go = st.form_submit_button("Change PIN")
    if go:
        ok, msg = bank.change_pin(users, user, cur, new)
        (st.success if ok else st.error)(msg)

elif page == "Delete Account":
    st.title("Delete Account")
    st.warning(f"This permanently deletes your account. Balance Rs. {user['balance']:,.2f} "
               "will be paid out as cash.")
    with st.form("del"):
        pin = st.text_input("Enter PIN to confirm", type="password", max_chars=4)
        sure = st.checkbox("I understand this cannot be undone")
        go = st.form_submit_button("Delete my account")
    if go:
        if not sure:
            st.error("Tick the confirmation box first.")
        else:
            ok, msg = bank.delete_account(users, acc_no, pin)
            if ok:
                st.session_state.acc_no = None
                st.success(msg + " Collect your cash.")
                st.stop()
            else:
                st.error(msg)
