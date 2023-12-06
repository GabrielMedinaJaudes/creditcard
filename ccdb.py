import sqlite3


# macros differenciating tranactions/payments
TRANSACTION = 0
PAYMENT = 1

# macros differenciating transaction states
PENDING = 0
SETTLED = 1
CANCELED = 2

def connect_to_db():
    conn = sqlite3.connect('database.db')
    return conn

def create_db_tables():
    try:
        conn = connect_to_db()
        conn.execute('''
            CREATE TABLE IF NOT EXISTS actions (
                txn_id TEXT PRIMARY KEY NOT NULL,
                action_type INTEGER NOT NULL,
                init_time INTEGER NOT NULL,
                final_time INTEGER NOT NULL,
                amount INTEGER NOT NULL,
                state INTEGER NOT NULL
            );
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS creditcard (
                cc_id INT PRIMARY KEY NOT NULL,
                credit_limit INT NOT NULL,
                payable_balance INT NOT NULL
            );
        ''')
        conn.commit()
        print("Tables created successfully")
    except sqlite3.Error as error:
        print("Table creation failed", error)
    finally:
        conn.close()

def init_cc(credit_limit):
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO creditcard (cc_id, credit_limit, payable_balance) VALUES (?, ?, ?);", (0, credit_limit, 0)
        )
        conn.commit()
        print('Initialized creditcard')
    except sqlite3.Error as error:
        print("Credit card initialization failed", error)
    finally:
        conn.close()

def get_cc():
    cc = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM creditcard;"
        )
        row = cur.fetchone()
        cc["credit_limit"] = row[1]
        cc["payable_balance"] = row[2]
    except sqlite3.Error as error:
        print("Credit card get failed", error)
    finally:
        conn.close()
    return cc

def reset():
    try:
        conn = connect_to_db()
        conn.execute('''
            DROP TABLE IF EXISTS actions;
        ''')
        conn.execute('''
            DROP TABLE IF EXISTS creditcard;
        ''')
        conn.commit()
        print("Tables dropped successfully")
    except sqlite3.Error as error:
        print("Table dropping failed", error)
    finally:
        conn.close()

def get_action_by_id(txn_id):
    action = {}
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM actions WHERE txn_id = ?;", (txn_id,)
        )
        row = cur.fetchone()
        if row == None:
            return action
        action["txn_id"] = row["txn_id"]
        action["action_type"] = row["action_type"]
        action["init_time"] = row["init_time"]
        action["final_time"] = row["final_time"]
        action["amount"] = row["amount"]
        action["state"] = row["state"]
    except sqlite3.Error as error:
        print("Couldn't fetch action", error)
    finally:
        conn.close()
    return action

def get_actions():
    actions = []
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM actions"
        )
        rows = cur.fetchall()
        for row in rows:
            action = {}
            action["txn_id"] = row["txn_id"]
            action["action_type"] = row["action_type"]
            action["init_time"] = row["init_time"]
            action["final_time"] = row["final_time"]
            action["amount"] = row["amount"]
            action["state"] = row["state"]
            actions.append(action)
    except sqlite3.Error as error:
        print("Couldn't fetch actions", error)
    finally:
        conn.close()
    return actions

def get_settled_actions():
    actions = []
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM actions WHERE state = ? ORDER BY init_time  LIMIT 3", (SETTLED,)
        )
        rows = cur.fetchall()
        for row in rows:
            action = {}
            action["txn_id"] = row["txn_id"]
            action["action_type"] = row["action_type"]
            action["init_time"] = row["init_time"]
            action["final_time"] = row["final_time"]
            action["amount"] = row["amount"]
            action["state"] = row["state"]
            actions.append(action)
    except sqlite3.Error as error:
        print("Couldn't fetch transactions", error)
    finally:
        conn.close()
    return actions

def get_pending_actions():
    actions = []
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM actions WHERE state = ? ORDER BY init_time", (PENDING,)
        )
        rows = cur.fetchall()
        for row in rows:
            action = {}
            action["txn_id"] = row["txn_id"]
            action["action_type"] = row["action_type"]
            action["init_time"] = row["init_time"]
            action["final_time"] = row["final_time"]
            action["amount"] = row["amount"]
            action["state"] = row["state"]
            actions.append(action)
    except sqlite3.Error as error:
        print("Couldn't fetch payments", error)
    finally:
        conn.close()
    return actions

def get_credit_limit():
    limit = -1
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM creditcard"
        )
        row = cur.fetchone()
        if row == None:
            return limit
        limit = row["credit_limit"]
    except sqlite3.Error as error:
        print("Couldn't fetch credit limit", error)
    finally:
        conn.close()
    return limit

def set_credit_limit(new_limit):
    limit = -1
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            "UPDATE creditcard SET credit_limit = ?;", (new_limit,)
        )
        conn.commit()
        row = cur.fetchone()
        if row == None:
            return limit
        limit = row["credit_limit"]
    except sqlite3.Error as error:
        print("Couldn't update credit limit", error)
        conn.rollback()
    finally:
        conn.close()
    return limit

def get_payable_balance():
    balance = -1
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM creditcard"
        )
        row = cur.fetchone()
        if row == None:
            return balance
        balance = row["payable_balance"]
    except sqlite3.Error as error:
        print("Couldn't fetch balance", error)
    finally:
        conn.close()
    return balance

def set_payable_balance(new_balance):
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            "UPDATE creditcard SET payable_balance = ?", (new_balance,)
        )
        conn.commit()
        row = cur.fetchone()
        if row == None:
            return -1
        balance = row["payable_balance"]
    except sqlite3.Error as error:
        print("Couldn't set payable balance", error)
        conn.rollback()
    finally:
        conn.close()
    return balance

def insert_action(inputJSON): # will raise exeception if txn_id already exists
    inserted = {}
    conn = None
    try:
        event_type = inputJSON["eventType"]
        action_type = TRANSACTION if event_type == "TXN_AUTHED" else PAYMENT
        amount = inputJSON["amount"]
        credit_limit = 0
        payable_balance = 0
        if action_type == TRANSACTION:
            credit_limit = get_credit_limit()
            if amount > credit_limit:
                print("Not enough credit")
                return {}
        else:
            if amount > 0:
                print("invalid payment amount")
                return {}
            payable_balance = get_payable_balance()
            if payable_balance == 0:
                print('no balance to be paid')
                return {}
        conn = connect_to_db()
        cur = conn.cursor()
        txn_id = inputJSON["txnId"]
        init_time = inputJSON["eventTime"]
        final_time = 0
        state = PENDING
        action_type = TRANSACTION if event_type == "TXN_AUTHED" else PAYMENT
        cur.execute('''INSERT INTO actions (txn_id, action_type, init_time, final_time, amount, state)
                                    VALUES (?, ?, ?, ?, ?, ?)''', (txn_id, action_type, init_time, final_time, amount, state))
        conn.commit()
        if action_type == TRANSACTION:
            set_credit_limit(credit_limit - amount)
        else:
            set_payable_balance(payable_balance + amount)
        inserted = get_action_by_id(txn_id)
    except sqlite3.Error as error:
        print("Couldn't insert action", error)
        conn.rollback()
    finally:
        if conn:
            conn.close()
    return inserted

def cancel_action(txn_id):
    new_action = {}
    try:
        old_action = get_action_by_id(txn_id)
        if old_action == {}: # not found
            return {}
        if old_action["action_type"] == TRANSACTION:
            credit_limit = get_credit_limit()
            set_credit_limit(credit_limit + old_action["amount"])
        else:
            payable_balance = get_payable_balance()
            set_payable_balance(payable_balance - old_action["amount"])
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('''
            UPDATE actions SET state = ? WHERE txn_id = ?
        ''', (CANCELED, txn_id))
        conn.commit()
        new_action = get_action_by_id(txn_id)
    except sqlite3.Error as error:
        print("Couldn't cancel action", error)
        conn.rollback()
    finally:
        conn.close()
    return new_action

def update_action_amount(txn_id, final_amount):
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            "UPDATE actions SET amount = ? WHERE txn_id = ?;", (final_amount, txn_id)
        )
        conn.commit()
    except sqlite3.Error as error:
        print("Couldn't update action amount", error)
        conn.rollback()
    finally:
        conn.close()

def settle_action(txn_id, final_time, new_amount=None):
    new_action = {}
    try:
        old_action = get_action_by_id(txn_id)
        if old_action == {}: # not found
            return {}
        if old_action["action_type"] == TRANSACTION:
            if new_amount != None and old_action["amount"] != new_amount:
                credit_limit = get_credit_limit()
                final_amount = new_amount-old_action["amount"]
                set_credit_limit(credit_limit-final_amount)
                update_action_amount(txn_id, new_amount)
            else:
                new_amount = old_action["amount"]
            payable_balance = get_payable_balance()
            set_payable_balance(payable_balance+new_amount)
        else:
            credit_limit = get_credit_limit()
            set_credit_limit(credit_limit-old_action["amount"])
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('''
            UPDATE actions SET final_time = ?, state = ? WHERE txn_id = ?;
        ''', (final_time, SETTLED, txn_id))
        conn.commit()
        new_action = get_action_by_id(txn_id)
    except sqlite3.Error as error:
        print("Couldn't settle action", error)
        conn.rollback()
    finally:
        conn.close()
    return new_action