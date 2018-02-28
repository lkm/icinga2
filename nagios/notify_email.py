#!/usr/bin/python

import smtplib,sys,getopt,os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from string import Template

config={
    'smtp_host': ''
    'smtp_port': 25
    'smtp_username': ''
    'smtp_password': ''
    'use_tls' : True
}

def send_mail(sender, subject, to, body):
    global config

    msg = MIMEMultipart('alternative') 

    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to

    part1 = MIMEText('Please view in html capable email reader', 'plain')
    part2 = MIMEText(body, 'html')

    msg.attach(part1)
    msg.attach(part2)
    
    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP(config['smtp_host'], config['smtp_port'])
    s.ehlo()
    if config['use_tls']
        s.starttls()
    s.ehlo()
    s.esmtp_features['auth'] = 'LOGIN PLAIN'
    s.login(config['smtp_username'], config['smtp_password'])
    s.sendmail(sender, to, msg.as_string())

    s.quit()

def build_mail_service(notification_type, notification_author, notification_comment, long_date, host_name, host_ip, state, output, service_name):
    s = get_template()

    return s.substitute(
        type='Service', 
        headline='Service: ' + service_name + ' is ' + state, 
        state=state,
        host_name=host_name,
        host_ip=host_ip,
        time=long_date,
        service_name=service_name,
        output=output
    )

def build_mail_host(notification_type, notification_author, notification_comment, long_date, host_name, host_ip, state, output):
    s = get_template()
    
    return s.substitute(
        type='Host', 
        headline='Host: ' + host_name + ' is ' + state, 
        state=state, 
        host_name=host_name,
        host_ip=host_ip,
        time=long_date,
        service_name='',
        output=output
    )

def get_template():
    s = ''

    with open(os.path.dirname(os.path.realpath(__file__)) + '/alert.html', 'r') as myfile:
        data=myfile.read()
        s = Template(data) 
    
    return s

def main(argv):
    global config

    email = ''
    notification_object = ''
    body = ''
    subject = ''

    ip_address = ''
    notification_type=''
    notification_author=''
    notification_comment=''
    long_date=''
    host_name=''
    service_name=''
    state=''
    output=''

    try:
        opts, args = getopt.getopt(argv, "h:t:e:T:b:c:d:n:S:s:o:4:",
                                   ["email=", "type=", "notification-type=", "notification-author=", "notification-comment=", "date=", "host-name=", "service-name=", "state=", "output=", "ip-address=", "smtp-host=", "smtp-username=", "smtp-password=" ])
    except getopt.GetoptError, e:
        print 'notify_email.py: ' + str(e)
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'notify_email.py --to [-t] <email>'
            sys.exit()
        elif opt in ("-t", "--type"):
            notification_object = arg
        elif opt in ("-e", "--email"):
            email = arg
        elif opt in ("-T", "--notification-type"):
            notification_type = arg
        elif opt in ("-b", "--notification-author"):
            notification_author = arg
        elif opt in ("-c", "--notification-comment"):
            notification_comment = arg
        elif opt in ("-d", "--date"):
            long_date = arg
        elif opt in ("-n", "--host-name"):
            host_name = arg
        elif opt in ("-S", "--service-name"):
            service_name = arg
        elif opt in ("-s", "--state"):
            state = arg
        elif opt in ("-o", "--output"):
            output = arg
        elif opt in ("-4", "--ip-address"):
            ip_address = arg
        elif opt in ("--smtp-host")
            config['smtp_host'] = arg
        elif opt in ("--smtp-username")
            config['smtp_username'] = arg
        elif opt in ("--smtp-password")
            config['smtp_password'] = arg

    if notification_object == 'host':
        body = build_mail_host(notification_type, notification_author, notification_comment, long_date, host_name, ip_address, state, output)
        subject = 'Host: ' + host_name + ' is ' + state
    elif notification_object == 'service':
        body = build_mail_service(notification_type, notification_author, notification_comment, long_date, host_name, ip_address, state, output, service_name)
        subject = 'Service: ' + service_name + ' on ' + host_name + ' is ' + state
    else:
        print 'invalid type: ' + notification_object
        sys.exit(2)

    send_mail('icinga2@bookboon.com', subject, email, body)

if __name__ == "__main__":
    main(sys.argv[1:])
