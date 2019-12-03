#!/usr/bin/env python3
'''
 Basic script to gather data from BRE sites. Script will be ran via cron on a 5 minute interval. once the BGY shows unreachable HCM, A battery of commands will be gathered.

'''
__author__ = "Aruba&ATT"
__version__ = "2.3"
__status__ = "Prod"

##########
#V2.0: Added store id to config file and email; Adjusted commands triggered for failed HCM: Jay McNealy
#V2.1: Added Log file as a config file variable: Jay McNealy
#V2.2: modified; if len(sys.argv) < 1: to if len(sys.argv) < 2:also
#      sendMail(from_addr, to_addrs,"HCM is unreachable from McD Store-(%s),contact Engineering team for further debugging.." % store_name,smpt_server) --> sendMail(ip, from_addr, to_addrs,"HCM is unreachable from McD Store-(%s),contact Engineering team for further debugging.." % store_name,smpt_server)
#                                                                              : Cesar Saucedo
#V2.3: Added cmds for reachable HMC: Jay McNealy
#V2.4:
##########

import sys
sys.path.append('/usr/local/lib/python3.4/site-packages/')
import paramiko
import time
import os
import pdb
import re
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import getpass
import logging
import configparser
import logging.handlers


def sendMail(ip, from_addr, to_addrs, body, smtp_server='localhost'):
    """
    sample call:
    sendMail("satish.pathak@hpe.com","satish.pathak@hpe.com", "HCM is unreachable",'localhost')
    """
    if not (from_addr and to_addrs and body and smtp_server):
        #print("Required email details not provided please pass from_addr,to_addrs,smtp_server and mail body")
        my_logger.info("Required email details not provided please pass from_addr,to_addrs,smtp_server and mail body")
        return 0
    to_addr = []
    for email in to_addrs:
        email = str(email).lstrip()
        email = str(email).rstrip()
        to_addr.append(email)
    try:
        #print("Sending mail to %s"%str(to_addrs))
        my_logger.info("Sending mail to %s"%str(to_addrs))
        msg = MIMEMultipart()
        message = """\
        <html>
            <head></head>
            <body>
            <p><b>Hi! TAC Team,</b><br>
            <br>
            %s<br>
            <br>
            <b>Thanks,</b><br>
            <b>Aruba Team</b>
            </p>
            </body>
        </html>
        """%(str(body))
        msg.attach(MIMEText(message, 'html'))
        msg['Subject'] = ("%s HCM is unreachable" % ip)
        msg['To'] = str(to_addr)
        msg['From'] = str(from_addr)
        server = smtplib.SMTP(str(smtp_server))
        server.sendmail(str(from_addr), to_addr, msg.as_string())
    except Exception as e:
        #print("Error, Unable to send mail for error %s"%str(e))
        my_logger.info("Error, Unable to send mail for error %s"%str(e))
        return 0
    #print("Mail sent successfully to email %s"%(str(to_addrs)))
    my_logger.info("Mail sent successfully to email %s"%(str(to_addrs)))
    return 1


if __name__ == '__main__':

    test = 'show ip health-check 216.12.248.116 4081\n'
    cmd1 = 'show ip health-check 216.12.248.116 4094\n'
    cmd2 = 'show clock\n'
    cmd3 = 'show port stats\n'
    cmd4 = 'show uplink\n'
    cmd5 = 'show uplink load-balance\n'
    cmd6 = 'show ip health-check\n'
    cmd7 = 'show crypto isakmp stats\n'
    cmd8 = 'show ipc statistics app-name ike\n'
    cmd9 = 'show datapath frame\n'
    cmd10 = 'show datapath frame counters\n'
    cmd11 = 'show datapath application counters\n'
    cmd12 = 'show datapath message-queue counters\n'
    cmd13 = 'show datapath session verbose | include 216.12.248.116,P\n'
    cmd14 = 'show interface gigabitethernet 0/0/3\n'
    cmd15 = 'show ip health-check verbose\n'
    cmd101 = 'no paging\n'

    # Config Parse Start ####
    #Pull variables from config
    if len(sys.argv) < 2:
        print("Not enough arguments provided, please provide file name for config file")
        sys.exit(1)
    CONFIG_FILE = sys.argv[1]
    #CONFIG_FILE = '/var/home/cs485b/config.ini'
    # Initialize Config file and get config
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    ip = str(config['main']['bgw-ip'])
    username =  str(config['main']['username'])
    password = str(config['main']['password'])
    to_addrs = (config['main']['to_addrs'])
    to_addrs = to_addrs.split()
    from_addr =  str(config['main']['from_addr'])
    smpt_server =  str(config['main']['smpt_server'])
    store_name = str(config['main']['store_name'])
    logfile = str(config['main']['logfile'])

    # Set up logging
    my_logger = logging.getLogger('MyLogger')
    my_logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    handler = logging.handlers.RotatingFileHandler(logfile, maxBytes=10485760, backupCount=3)
    handler.setFormatter(formatter)
    my_logger.addHandler(handler)

    #print ('connecting to {}, as user {}'.format (ip,username))
    my_logger.info('connecting to {}, as user {}'.format (ip,username))
    try:
       remote_conn_pre = paramiko.SSHClient()
       # Automatically add untrusted hosts (make sure okay for security policy in your environment)
       remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
       # initiate SSH connection
       remote_conn_pre.connect(ip, username=username, password=password, look_for_keys=False, allow_agent=False, timeout=30)
       #remote_conn_pre.connect("10.8.244.145", username="admin", password="admins", look_for_keys=False, allow_agent=False, timeout=30)
       # Use invoke_shell to establish an 'interactive session'
       remote_conn = remote_conn_pre.invoke_shell()
    except paramiko.SSHException as sshException:
       #print("Unable to establish SSH connection: %s" % sshException)
       my_logger.info("%s Unable to establish SSH connection: %s" %(ip, sshException))
       sendMail(ip, from_addr, to_addrs,"Gateway is down/unreachable from McD site, please contact CSM immediately!",smpt_server)
       sys.exit(1)

    #print("\n\nSet no paging")
    remote_conn.send(cmd101)
   ###  Sleep for 3 minutes and check the status again (i.e 180 seconds)
    #print("\n\n%s Intial health check" %ip)
    remote_conn.send(cmd1)
    time.sleep(2)
    status_report = remote_conn.recv(5000)
    #print(status_report)
    #my_logger.info(status_report)
    #added decode('utf-8' to convert from bytes to str
    #if not 'unreachable' in status_report.decode('utf-8'):
    if not 'unreachable' in status_report.decode('utf-8'):
        #print("%s HCM is reachable" % ip)
        my_logger.info("%s Store %s, HCM is reachable" % (ip,store_name))
        
        ##  Execute command: show ip health-check vlan ###
        remote_conn.send(cmd1)
        time.sleep(2)
        status_report = remote_conn.recv(5000)
        my_logger.info(status_report)

        ###  Execute command: show clock  ###
        remote_conn.send(cmd2)
        time.sleep(1)
        unreachable_time = remote_conn.recv(10000)
        my_logger.info("unreachable time :: %s" %unreachable_time)

        ###  Execute command: show port stats  ###
        remote_conn.send(cmd3)
        time.sleep(1)
        port_stats = remote_conn.recv(10000)
        my_logger.info("\n*******Port Stats*******")
        my_logger.infot(port_stats)
        sys.exit(0)
    else:
        #print("%s HCM is unreachable falling to BackupLink" %ip)
        sendMail(ip, from_addr, to_addrs,"HCM is unreachable from McD Store-(%s),contact Engineering team for further debugging.." % store_name,smpt_server)

   ###  Execute command: show clock  ###
    remote_conn.send(cmd2)
    time.sleep(1)
    unreachable_time = remote_conn.recv(10000)
    my_logger.info("unreachable time :: %s" %unreachable_time)
    ###  Execute command: show uplink  ###
    remote_conn.send(cmd4)
    time.sleep(1)
    port_stats = remote_conn.recv(10000)
    my_logger.info("\n*******Port Stats*******")
    my_logger.info(port_stats.decode('utf-8'))
    ### Execute command: show uplink load-balance" ###
    remote_conn.send(cmd5)
    time.sleep(1)
    load_balance = remote_conn.recv(10000)
    my_logger.info("\n******** Load Balance *******")
    my_logger.info(load_balance.decode('utf-8'))
    ### Execute command: show ip health-check" ###
    remote_conn.send(cmd6)
    time.sleep(1)
    ip_health_check = remote_conn.recv(10000)
    my_logger.info("\n********  IP Health Check *******")
    my_logger.info(ip_health_check.decode('utf-8'))
   ### Following commands are captured 3 times with an interval of 15 seconds each.

    for x in range(3):
        #import pdb; pdb.set_trace()
        remote_conn.send(cmd7)
        time.sleep(1)
        ip_health_check = remote_conn.recv(10000)
        my_logger.info("\n********  Debug: Data collection, iteration:")
        my_logger.info(ip_health_check.decode('utf-8'))
        time.sleep(1)
        remote_conn.send(cmd8)
        time.sleep(1)
        ip_health_check = remote_conn.recv(10000)
        my_logger.info("\n********  Debug: Data collection, iteration:")
        my_logger.info(ip_health_check.decode('utf-8'))
        my_logger.info("\n********  Debug: Data collection, iteration:")
        my_logger.info(ip_health_check.decode('utf-8'))
        remote_conn.send(cmd9)
        time.sleep(1)
        ip_health_check = remote_conn.recv(10000)
        my_logger.info("\n********  Debug: Data collection, iteration:")
        my_logger.info(ip_health_check.decode('utf-8'))
        remote_conn.send(cmd10)
        time.sleep(1)
        ip_health_check = remote_conn.recv(10000)
        my_logger.info("\n********  Debug: Data collection, iteration:")
        my_logger.info(ip_health_check.decode('utf-8'))
        remote_conn.send(cmd11)
        time.sleep(1)
        ip_health_check = remote_conn.recv(10000)
        my_logger.info("\n********  Debug: Data collection, iteration:")
        my_logger.info(ip_health_check.decode('utf-8'))
        time.sleep(3)
        remote_conn.send(cmd12)
        time.sleep(1)
        ip_health_check = remote_conn.recv(10000)
        my_logger.info("\n********  Debug: Data collection, iteration:")
        my_logger.info(ip_health_check.decode('utf-8'))
        remote_conn.send(cmd13)
        time.sleep(1)
        ip_health_check = remote_conn.recv(10000)
        my_logger.info("\n********  Debug: Data collection, iteration:")
        my_logger.info(ip_health_check.decode('utf-8'))
        remote_conn.send(cmd14)
        time.sleep(1)
        ip_health_check = remote_conn.recv(10000)
        my_logger.info("\n********  Debug: Data collection, iteration:")
        my_logger.info(ip_health_check.decode('utf-8'))
        remote_conn.send(cmd15)
        time.sleep(1)
        ip_health_check = remote_conn.recv(10000)
        my_logger.info("\n********  Debug: Data collection, iteration:")
        my_logger.info(ip_health_check.decode('utf-8'))
        time.sleep(15)
    remote_conn.close()
