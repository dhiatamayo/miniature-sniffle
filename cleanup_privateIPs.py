# workaround
# get into domains folder
# open each one of the domains file
# check every category if theres any private IPs. store the private IPs to other dict:key:privateIPs, value:category
# store every domains (private IPs excluded) inside every category, store it as a list
# remove old domains file, create a new domains file using all domains list from above
# do for all the categories

import os
from collections import defaultdict

domaindict = {}
with open ('listdomains', 'r') as listdomain:
    for j in listdomain:
        (key,val) = j.replace(' ','').split(':')
        domaindict[int(key)] = val.replace('\n','')

localdomain = defaultdict(list)
for key in range(0, len(domaindict)):
    categorypath = '../../categories/%s/domains' % (domaindict[int(key)])
    categorydomains = []
    with open (categorypath, "r") as domainsfile:
        for domain in domainsfile:
            if domain.startswith('10.') == True:
                if domain.split('.')[1].isnumeric() is True:
                    localdomain[categorypath].append(domain)
            else:
                if domain.startswith('192.168.') == True:
                    localdomain[categorypath].append(domain)
                else:
                    for j in range(16,32):
                        filter2 = '172.%s.' % j
                        if domain.startswith(filter2) == True:
                            localdomain[categorypath].append(domain)
                        else:
                            continue
                    else:
                        categorydomains.append(domain)
    print("processed " + categorypath)
    #print(localdomain)
    #print("---------------------------------")
    os.system("rm %s" %categorypath)
    with open (categorypath, 'a') as writedomainsfile:
        for i in categorydomains:
            writedomainsfile.write(i)

with open ('privateIPs_dict', 'a') as g:
    g.write('category,private_IP\n')
    for i in localdomain.keys():
        for j in localdomain[i]:
            g.write(i.split('/categories/')[1].replace('/domains','') + ',' + j)
