To run this Flask Server, run the commands:

```
cd creditcard
python3 -m venv .venv
. .venv/bin/activate
flask run --debug
```

To run the summarizer, run the following curl command in another terminal:
`curl -X POST -H "Content-Type: application/json" -d <JSON> http://127.0.0.1:5000/summarize`
The database will NOT reset when you run the summarizer! 
To reset it, run:
`curl http://127.0.0.1:5000/reset`

To query the results of the last summary run:
`curl http://127.0.0.1:5000/summarize`

Example JSON:
```
{
    "creditLimit":1000,
    "events":
        [
            {"eventType":"TXN_AUTHED","eventTime":1,"txnId":"t1","amount":123},
            {"eventType":"TXN_SETTLED","eventTime":2,"txnId":"t1","amount":456},
            {"eventType":"TXN_AUTHED","eventTime":3,"txnId":"t2","amount":-456},
            {"eventType":"TXN_SETTLED","eventTime":4,"txnId":"t2","amount":-456}
        ]
}
```
Example commands:
### Refund
```
curl -X POST -H "Content-Type: application/json" -d '{"creditLimit":1000, "events": [{"eventType":"TXN_AUTHED","eventTime":1,"txnId":"t1","amount":123},{"eventType":"TXN_SETTLED","eventTime":2,"txnId":"t1","amount":456},{"eventType":"TXN_AUTHED","eventTime":3,"txnId":"t2","amount":-456},{"eventType":"TXN_SETTLED","eventTime":4,"txnId":"t2","amount":-456}]}' http://127.0.0.1:5000/summarize
```
### Start transaction then cancel it
```
curl -X POST -H "Content-Type: application/json" -d '{"creditLimit":1000, "events": [{"eventType":"TXN_AUTHED","eventTime":1,"txnId":"t1","amount":123},{"eventType":"TXN_AUTH_CLEARED","eventTime":2,"txnId":"t1","amount":456}]}' http://127.0.0.1:5000/summarize
```
### Start transaction then settle it (with tip)
```
curl -X POST -H "Content-Type: application/json" -d '{"creditLimit":1000, "events": [{"eventType":"TXN_AUTHED","eventTime":1,"txnId":"t1","amount":123},{"eventType":"TXN_SETTLED","eventTime":2,"txnId":"t1","amount":456}]}' http://127.0.0.1:5000/summarize
```

### Start transaction then settle it (with tip) and start to pay it
```
curl -X POST -H "Content-Type: application/json" -d '{"creditLimit":1000, "events": [{"eventType":"TXN_AUTHED","eventTime":1,"txnId":"t1","amount":123},{"eventType":"TXN_SETTLED","eventTime":2,"txnId":"t1","amount":456},{"eventType":"PAYMENT_INITIATED","eventTime":3,"txnId":"t2","amount":-456}]}' http://127.0.0.1:5000/summarize
```

### Start transaction then settle it (with tip) and start to pay it but cancel it
```
curl -X POST -H "Content-Type: application/json" -d '{"creditLimit":1000, "events": [{"eventType":"TXN_AUTHED","eventTime":1,"txnId":"t1","amount":123},{"eventType":"TXN_SETTLED","eventTime":2,"txnId":"t1","amount":456},{"eventType":"PAYMENT_INITIATED","eventTime":3,"txnId":"t2","amount":-456},{"eventType":"PAYMENT_CANCELED","eventTime":4,"txnId":"t2","amount":-456}]}' http://127.0.0.1:5000/summarize
```

## Start transaction then settle it (with tip) and pay it off!
```
curl -X POST -H "Content-Type: application/json" -d '{"creditLimit":1000, "events": [{"eventType":"TXN_AUTHED","eventTime":1,"txnId":"t1","amount":123},{"eventType":"TXN_SETTLED","eventTime":2,"txnId":"t1","amount":456},{"eventType":"PAYMENT_INITIATED","eventTime":3,"txnId":"t2","amount":-456},{"eventType":"PAYMENT_POSTED","eventTime":4,"txnId":"t2","amount":-456}]}' http://127.0.0.1:5000/summarize
```
