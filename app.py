from flask import Flask, request, jsonify
import ccdb

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/reset", methods=['GET'])
def reset():
    ccdb.reset()
    return "resetted\n"

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
            return "********** BAD REQUEST!\n", 404
    response = formatOutput()
    return response

def formatOutput():
    pending = ccdb.get_pending_actions()
    settled = ccdb.get_settled_actions()
    cc = ccdb.get_cc()
    if cc == {}:
        return 'Nothing to summarize!\n'
    pendingStr = ""
    for action in pending:
        pendingStr = pendingStr + f"{action['txn_id']}: {action['amount']} @ time {action['init_time']}\n"
    settledStr = ""
    for action in settled:
        settledStr = settledStr + f"{action['txn_id']}: {action['amount']} @ time {action['init_time']} (finalized @ time {action['final_time']})\n"
    
    return (f'''
SUMMARY OF TRANSACTIONS:
Available credit: ${cc["credit_limit"]}
Payable balance: ${cc["payable_balance"]}
Pending Transactions:
{pendingStr}
Settled Transactions:
{settledStr}
''')
