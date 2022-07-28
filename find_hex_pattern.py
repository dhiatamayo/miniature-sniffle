import os
import subprocess as sp

def find_pattern(s1,s2):
    l = [int(not(a == b)) for a,b in zip(s1,s2)]
    s = ""
    for i in l:
        s += str(i)
    return s

def find_overall_pattern(s1,s2):
    s = ""
    l = []
    x = zip(s1,s2)
    for (a,b) in x:
        a = int(a)
        b = int(b)
        if a == 0:
            if a == b:
                l.append('0')
            else:
                l.append('1')
        else:
            l.append('1')
        continue
    for i in l:
        s += str(i)
    return s
    #l = [int(not(a == b)) for a,b in zip(s1,s2)]
    #s = ""
    #for i in l:
     #   if i == 0:
      #      s += str(i)
       # else:
        #    s += 'F'
    #return s

def convert(s):
    new = ""

    # traverse in the string 
    for x in s:
        new += x 
  
    # return string 
    return new

path = input('input flows directory: ')
list_file = []

for r, d, f in os.walk(path):
    for file in f:
        list_file.append(os.path.join(r, file))

list_file.sort()
dict_hex = {}

prot = input('input protocol: ')
for i in list_file:
    try:
        output_tshark = sp.getoutput("tshark -r %s -T fields -e %s.payload | head -n 1" %(i, prot))
        #output_tshark = sp.getoutput("tshark -r %s -T fields -e tcp.payload | head -n 4" %i)
        #print(i)
        dict_hex[i.split('/')[-1]] = output_tshark
    except:
        continue

#print (dict_hex)
list_of_dict = []

for i in dict_hex:
    list_of_dict.append({i : dict_hex[i]})
#print(list_of_dict)

pattern_list = []
print ('### 0 means same value, 1 means different value ###\n')
for i in range(len(list_of_dict)-1):
    for j in list_of_dict[0]:
        key0 = j
    for k in list_of_dict[i+1]:
        key = k
    print(key0 + ' and ' + key + ':')
    hex_overlap = find_pattern(list_of_dict[0][key0],list_of_dict[i+1][key])
    print(hex_overlap + '\n')
    pattern_list.append(hex_overlap)

#print(pattern_list)
overall_pattern = find_overall_pattern(pattern_list[0],pattern_list[1])
#print(overall_pattern + '\n')
for i in range(len(pattern_list)-2):
    overall_pattern = find_overall_pattern(overall_pattern,pattern_list[i+2])
print("### This is the pattern for all flows ###")
print("re. 0 means it has the same value for all of the flows")
print(overall_pattern)

list_of_char = list(overall_pattern)
list_of_char_hex = list(list_of_dict[0][key0])
overall_hex = []
for i in range(len(list_of_char)):
    if list_of_char[i] != "0":
        overall_hex.append('F')
    else:
        overall_hex.append(list_of_char_hex[i])
print("\n### This should be the hex for all flows ###")
print(convert(overall_hex))
