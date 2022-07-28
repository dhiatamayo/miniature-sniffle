#!/usr/bin/python3
'''
tshark pcap extractor script
made to simplify the sampling process for multiple apps and bulk the processes together.
first developed to sample a lot of web apps cust reqs (http/tcp hosts, user-agents, quic hosts as possible new sigs).
for more complicated apps (uri, udp preambles, pretaints, and quic components as possible new sigs), 
this script can still be used for finding obvious new sigs (obvious SNIs, hosts, user-agents), pcap naming, and scp purposes.
pre-requisites: 'tshark' command executable on terminal
'''

import os
import argparse

# checker function for file directly in given path
def dir_to_file_checker(path):
    pathname_list = []
    for file in os.listdir(path):
        if file.endswith('.pcap'):
            pathname_list.append(path + '/' + file)
    return pathname_list
 
# checker function for file not directly in given path
def dir_to_dir_checker(path):
    pathname_list = []
    for dir in os.listdir(path):
        if not dir.startswith('.'):
            pathdir = path + '/' + dir
            for file in os.listdir(pathdir):
                if file.endswith('.pcap'):
                    pathname_list.append(pathdir + '/' + file)
    return pathname_list

# scp to picobeast function
def scp_files_to_picobeast(pathname, path, dir_scp_fullsamples, dir_scp_incoming, identifier):
    if identifier == 3:
        dir_fullsamples = '{}/*/*.pcap'.format(path)
        dir_incoming = '{}/*/incoming/*.pcap'.format(path)
    elif identifier == 2:
        dir_fullsamples = '{}/*.pcap'.format(path)
        dir_incoming = '{}/incoming/*.pcap'.format(path)  
    if dir_scp_fullsamples.lower() == 'd':
        dir_scp_fullsamples = '192.168.2.70:/home/traces/fullsamples/'
    if dir_scp_incoming.lower() == 'd':
        dir_scp_incoming = '192.168.2.70:/home/traces/incoming/'
    print("scp-ing fullsample pcaps...")
    print('scp {} {}'.format(dir_fullsamples, dir_scp_fullsamples))
    print("scp-ing incoming pcaps...")
    print('scp {} {}'.format(dir_incoming, dir_scp_incoming))
    
# define class for pcap file for neat object processing
class PcapFile():
    
    def __init__(self, filename_path):
        self.pathname = filename_path
        self.filename = filename_path.split('/')[-1]
        self.path = filename_path.split(self.filename)[0]
        try:
            os.mkdir(self.path + 'incoming')
        except OSError:
            pass
        self.incoming_path = self.path + 'incoming/'
        
    def tshark_server_name(self):
        print("Server Name tshark result from " + self.pathname + ':')
        os.system("tshark -2 -r %s -T fields -e tls.handshake.extensions_server_name -R tls.handshake.extensions_server_name -e tcp.stream | sort | uniq -c | sort -nr" %self.pathname)
        
    def tshark_quic_server_name(self):   
        print("QUIC Server Name tshark result from " + self.pathname + ':')
        os.system("tshark -2 -r %s -T fields -e tls.handshake.extensions_server_name -R tls.handshake.extensions_server_name -e udp.stream | sort | uniq -c | sort -nr" %self.pathname)
    
    def tshark_http_host(self):
        print("HTTP host tshark result from " + self.pathname + ':')
        os.system("tshark -2 -r %s -T fields -e http.host -R http.host -e tcp.stream | sort | uniq -c | sort -nr" %self.pathname)
    
    def tshark_http_user_agent(self):
        print("HTTP User-Agent tshark result from " + self.pathname + ':')
        os.system("tshark -2 -r %s -T fields -e http.user_agent -R http.user_agent -e tcp.stream | sort | uniq -c | sort -nr" %self.pathname)
    
    # for further development, new tshark function can be added for other tshark filter (ex: http x-req, uri, ssl cert, etc) 
    
    def tshark_incoming_extractor(self):
        count = 0
        stream_input = "0"
        while stream_input.isdigit():
            stream_input = str(input("Stream number for extracting pcap? (N to stop pcap extracting) "))
            if not stream_input.isdigit():
                print("### Pcap extracting for " + self.filename + " is done ###")
                break
            else:
                protocol_input = input("What is the protocol (tcp/udp)? ")
                count += 1
            try:
                incoming_pathname = self.incoming_path + self.filename.replace('.pcap','') + str(count) + '.pcap'
                os.system("tshark -2 -R {}.stream=={} -r {} -w {}".format(protocol_input, stream_input, self.pathname, incoming_pathname))
                print("Pcap dumped in {}".format(incoming_pathname))
                print()
            except OSError:
                continue
        print()

    def fullsample_rename(self):
        print("Pcap file is " + self.filename)
        print("The name format example: flowsample.acctid=Paper.ipproto=tcp.source=fadhlika.time=1597153231.appver=web.attempt=1.sig-51435.anon.pcap")
        appname_input = input("Input acctid or appname if it's a new app:" + "\n")
        source_input = input("Input source:" + "\n")
        time_input = os.popen('date +%s').read().replace('\n','')
        appver_input = input("Input appver (e.g Android_1_1_1, iOS_1_1_1, web):" + "\n")
        sig_input = input("Input ticket number:" + "\n")
        print()
        new_fullsample_pathname = self.path + "flowsample.acctid=%s.ipproto=tcp.source=%s.time=%s.appver=%s.attempt=1.sig-%s.anon.pcap" %(appname_input, source_input, time_input, appver_input, sig_input)
        os.rename(self.path + self.filename, new_fullsample_pathname)
        return new_fullsample_pathname
    
    def incoming_rename(self, new_fullsample_pathname):
        new_fullsample_filename = new_fullsample_pathname.split('/')[-1]
        old_time_fullsample = int(new_fullsample_pathname.split('.')[4].replace('time=',''))
        count = 0
        for j in os.listdir(self.incoming_path):
            if j.startswith(self.filename.replace('.pcap','')):
                count += 1
                new_time_incoming = old_time_fullsample + count
                old_incoming_pathname = self.incoming_path + j
                new_incoming_pathname = self.incoming_path + new_fullsample_filename.replace(str(old_time_fullsample),str(new_time_incoming))
                os.rename(old_incoming_pathname, new_incoming_pathname)
       

parser = argparse.ArgumentParser()
parser.add_argument('-d')
args = parser.parse_args()
path = args.d
path = "/Users/fadhlika/Downloads/eatmarnanugi" 
# important to make sure the path doesn't end with '/' 
if path.endswith('/'):
    path = path[:-1]


# finding pcap file(s) from directory given
while True:
    pcapdirif = input("Is " + path + " where the pcaps stored?" + " (Y/N)" + "\n")
    try:
        if pcapdirif == "Y":
            pathname_list = dir_to_file_checker(path)
            if len(pathname_list) == 0:
                print('### There are no pcap files stored in this dir, proceeding to find pcap files further inside the dir ###')
                pathname_list = dir_to_dir_checker(path)
            break
        else:
            pathname_list = dir_to_dir_checker(path)
            break
    except NotADirectoryError:
        print('### The pcap files already stored in this dir, proceeding to list the pcap files ###')
        pathname_list = dir_to_file_checker(path)
        break
print()

# processing the pcap files
for pathname in pathname_list:
    pcap = PcapFile(pathname)
    print('### Processing {} ###\n'.format(pcap.filename))
    # printing tshark results
    pcap.tshark_server_name()
    pcap.tshark_quic_server_name()
    pcap.tshark_http_host()
    pcap.tshark_http_user_agent()
    pcap.tshark_incoming_extractor()
    output_filename = pcap.fullsample_rename()
    pcap.incoming_rename(output_filename)
    print('### Pcap renaming for {} is done ###'.format(pcap.filename))
    print()

# scp files to picobeast
scp_if = input('Do you want to scp your pcaps to picobeast? (Y/N) ')
if scp_if.lower() == 'y':
    dir_scp_fullsamples = input('Input fullsamples scp path: (D for default scp path (192.168.2.70:/home/traces/fullsamples/)) ')
    dir_scp_incoming = input('Input incoming scp path: (D for default scp path (192.168.2.70:/home/traces/incoming/)) ')
    path_note = list(pathname.replace(path,'').split('/'))
    scp_files_to_picobeast(pathname, path, dir_scp_fullsamples, dir_scp_incoming, len(path_note))
        
print('### All done! ###')