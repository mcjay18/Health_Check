# healthcheck_ATTMCD


## Current Version 2.3

Change Log 

* V2.0: Added store id to config file and email; Adjusted commands triggered for failed HCM: Jay McNealy
* V2.1: Added Log file as a config file variable: Jay McNealy
* V2.2: modified; if len(sys.argv) < 1: to if len(sys.argv) < 2:also
      sendMail(from_addr, to_addrs,"HCM is unreachable from McD Store-(%s),contact Engineering team for further debugging.." % store_name,smpt_server) --> sendMail(ip, from_addr, to_addrs,"HCM is unreachable from McD Store-(%s),contact Engineering team for further debugging.." % store_name,smpt_server)
                                                                             : Cesar Saucedo
* V2.3: Added cmds for reachable HMC: Jay McNealy
