#!/usr/local/bin/python3

import sys,getopt,os
from twilio.rest import Client

TWILIO_SID= ''
TWILIO_TOKEN=''

def send_sms(to, body):
    global TWILIO_TOKEN
    global TWILIO_SID

    client = Client(TWILIO_SID, TWILIO_TOKEN)

    message = client.api.account.messages.create(to=to,
                                        from_="Bookboon Alerts",
                                        body=body)

def main(argv):
    global TWILIO_SID
    global TWILIO_TOKEN

    address = ''
    message= ''

    try:
        opts, args = getopt.getopt(argv, "h:a:m:",
                                   ["message=", "address=", "twilio-sid=", "twilio-token="])
    except getopt.GetoptError as e:
        print ('notify_sms.py: ' + str(e))
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print ('notify_sms.py --address [-a] <number> --message [-m] <message>')
            sys.exit()
        elif opt in ("-a", "--address"):
            address = arg
        elif opt in ("-m", "--message"):
            message = arg
        elif opt in ["--twilio-sid"]:
            TWILIO_SID = arg
        elif opt in ["--twilio-token"]:
            TWILIO_TOKEN = arg

    # send_sms(address, message)

if __name__ == "__main__":
    main(sys.argv[1:])
