#!/usr/bin/python

import sys, getopt
import MySQLdb as mdb
from subprocess import Popen, PIPE

tables_to_check = ['Advert', 'Author', 'Answer', 'Application', 'Book', 'Exam', 'Branding', 'Category', 'Document', 'Language',
                   'Question', 'Review', 'Rotation', 'RotationVariant', 'Segment']

master_connection = None
slave_connection = None


def initiate_connection(hostname, database, user, password):
    try:
        return mdb.connect(hostname, user, password, database)
    except mdb.Error, e:
        print "CRITICAL - Connection error %d: %s" % (e.args[0], e.args[1])
        sys.exit(2)


def check_table(table):
    global master_connection
    global slave_connection

    output = ""

    cur = master_connection.cursor()
    cur.execute("SELECT HEX(Id), Version from " + table)
    mrows = cur.fetchall()
    mcount = cur.rowcount

    assoc = {}
    scur = slave_connection.cursor()
    scur.execute("SELECT HEX(Id), Version from " + table)
    srows = scur.fetchall()
    scount = scur.rowcount

    if scount != mcount:
        output += table + ": has " + str(scount) + " rows while master has " + str(
            mcount) + " on slave " + '\n'

    for row in srows:
        assoc[row[0]] = row[1]

    for m in mrows:
        if m[0] in assoc:
            if m[1] != assoc[m[0]]:
                output += table + ": Row with id 0x" + m[0] + " has different version on slave " + '\n'
        else:
            output += table + ": Row with id 0x" + m[0] + " is missing on slave " + '\n'
    scur.close()

    return output

def get_rancher_ip(host_id, access_key, secret_key):
    command_execute = 'rancher --access-key={0} --secret-key={1} --url https://rancher.bookbooncloud.com ps -c | grep api-database | grep {2}| awk \'{{print $6}}\''.format(access_key, secret_key, host_id)

    pipe = Popen(command_execute, shell=True, stdout=PIPE)
    slaveHost = pipe.stdout.readline();

    if not slaveHost:
        print "CRITICAL - Could not resolve database container on %s" % (host_id)
        sys.exit(2)
    return slaveHost

def main(argv):
    global master_connection
    global slave_connection

    database = ''

    master_host = ''
    master_user = ''
    master_password = ''

    slave_host = ''
    slave_user = ''
    slave_password = ''

    rancher_key = ''
    rancher_secret = ''

    output = ""

    try:
        opts, args = getopt.getopt(argv, "hd:m:u:p:s:U:P:r:R:",
                                   ["database=", "master-host=", "master-user=", "master-password=", "slave-host=", "slave-user=",
                                    "slave-password=","rancher-key=","rancher-secret="])
    except getopt.GetoptError, e:
        print 'check_db_sync.py: ' + str(e)
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'check_db_sync.py --database [-d] <database> --master-host [-m] <hostname> --master-user [-u] <user> --master-password [-p] <password> --slave-host [-s] <hostname> --slave-user [-U] <user> --slave-password [-P] <password> '
            sys.exit()
        elif opt in ("-d", "--database"):
            database = arg
        elif opt in ("-m", "--master-host"):
            master_host = arg
        elif opt in ("-u", "--master-user"):
            master_user = arg
        elif opt in ("-p", "--master-password"):
            master_password = arg
        elif opt in ("-s", "--slave-host"):
            slave_host = arg
        elif opt in ("-U", "--slave-user"):
            slave_user = arg
        elif opt in ("-P", "--slave-password"):
            slave_password = arg
        elif opt in ("-r", "--rancher-key"):
            rancher_key = arg
        elif opt in ("-R", "--rancher-secret"):
            rancher_secret = arg
    
    slaveHost = get_rancher_ip(slave_host, rancher_key, rancher_secret);
    master_connection = initiate_connection(master_host, database, master_user, master_password)
    slave_connection = initiate_connection(slaveHost, database, slave_user, slave_password)

    for table in tables_to_check:
        output += check_table(table)

    if output:
        print "CRITICAL - Not properly synchronized %s" % output
    else:
        print "OK - tables %s are synchronized" % tables_to_check

    master_connection.close()
    slave_connection.close()


if __name__ == "__main__":
    main(sys.argv[1:])
