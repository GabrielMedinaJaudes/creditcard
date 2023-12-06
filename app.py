from flask import Flask, request, jsonify
import ccdb

app = Flask(__name__)

def formatAction(action, is_settled):
    out = f"{action['txn_id']}: {action['amount']} @ time {action['init_time']}"
    if is_settled:
        return out + "(finalized @ time {action['final_time']})\n"
    else:
        return out + '\n'

def formatOutput():
    pending = ccdb.get_pending_actions()
    settled = ccdb.get_settled_actions()
    cc = ccdb.get_cc()
    if cc == {}:
        return 'Nothing to summarize!\n'
    pendingStr = ""
    for action in pending:
        pendingStr = pendingStr + formatAction(action, False)
    settledStr = ""
    for action in settled:
        settledStr = settledStr + formatAction(action, True)
    
    return (f'''
SUMMARY OF TRANSACTIONS:
Available credit: ${cc["credit_limit"]}
Payable balance: ${cc["payable_balance"]}
Pending Transactions:
{pendingStr}
Settled Transactions:
{settledStr}
''')

@app.route("/reset", methods=['GET'])
def reset():
    ccdb.reset()
    return "resetted\n"

@app.route("/init/<credit_limit>", methods=['GET'])
def init(credit_limit):
    ccdb.create_db_tables()
    ccdb.init_cc(credit_limit)
    return "Successfully initiated database\n"

@app.route("/authorize", methods=['POST'])
def init_action():
    event = request.get_json()
    response = ccdb.insert_action(event)
    if not response:
        return "********** BAD REQUEST!\n", 400
    return formatAction(response, False)

@app.route("/cancel", methods=['POST'])
def cancel():
    event = request.get_json()
    response = ccdb.cancel_action(event['txnId'])
    if not response:
        return "********** BAD REQUEST!\n", 400
    return formatAction(response, False)

@app.route("/settle", methods=['POST'])
def settle():
    event = request.get_json()
    action = ccdb.get_action_by_id(event["txnId"])
    if action["action_type"] == ccdb.TRANSACTION:
        response = ccdb.settle_action(event['txnId'], event['eventTime'], new_amount=event['amount'])
    else:
        response = ccdb.settle_action(event['txnId'], event['eventTime'])
    if not response:
        return "********** BAD REQUEST!\n", 400
    return formatAction(response, True)

@app.route("/summarize", methods=['POST', 'GET'])
def summarize():
    if request.method == 'GET':
        return formatOutput()
    body = request.get_json()
    ccdb.create_db_tables()
    ccdb.init_cc(body["creditLimit"])
    for event in body["events"]:
        event_type = event["eventType"]
        response = {}
        if event_type == "TXN_AUTHED" or event_type == "PAYMENT_INITIATED":
            response = ccdb.insert_action(event)
        elif event_type == "TXN_AUTH_CLEARED" or event_type == "PAYMENT_CANCELED":
            response = ccdb.cancel_action(event['txnId'])
        elif event_type == "TXN_SETTLED":
            response = ccdb.settle_action(event['txnId'], event['eventTime'], new_amount=event['amount'])
        elif event_type == "PAYMENT_POSTED":
            response = ccdb.settle_action(event['txnId'], event['eventTime'])
        if not response:
            ccdb.reset()
            return "********** BAD REQUEST!\n", 400
    response = formatOutput()
    return response
