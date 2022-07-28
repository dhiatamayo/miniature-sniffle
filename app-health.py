#app health script
import json
import csv

#mapping Games app from appmap
filename = 'appmap.json'
appmap = open(filename,'r+')
appmap_data = json.load(appmap)
games_appmap = []
for i in appmap_data:
    try:
        if "Games" in i['application_full_name']:
            games_appmap.append(i)
    except KeyError:
        continue
appmap.close()

#sum the volume
#filename_2 = 'sum_app_health_202205_simpl.csv'
#apphealth = open(filename_2, 'r')
#sum_volume = {}
#for i in apphealth:
 #   app = i.split(',')[0]
  #  volume = i.split(',')[2].replace('\n','')
   # if str(app) != sum_volume.keys():
    #    sum_volume[app] = volume
    #else:
     #   volume = int(volume) + int(sum_volume[app])
      #  sum_volume[app] = volume
#apphealth.close()

#recursive search from app health for list of games appmap
filename_2 = 'sum_app_health_202205_simpled.csv'
apphealth = open(filename_2, 'r')
top_games = []
for k in apphealth:
    for l in games_appmap:
        if l['application'] == str(k.split(',')[0]):
            top_games.append(l['application_full_name'] + "," + str(k.split(',')[1]))
        else:
            continue
apphealth.close()

#sum the volume
#filename_2 = 'sum_app_health_202205_simpl.csv'
#apphealth = open(filename_2, 'r')
sum_volume = {}
for i in top_games:
    app = i.split(',')[0]
    volume = i.split(',')[1].replace('\n','')
    if app not in sum_volume.keys():
        sum_volume[app] = volume
    else:
        volume = int(volume) + int(sum_volume[app])
        sum_volume[app] = volume
#apphealth.close()

#printout all result
for i in sum_volume.keys():
    with open ('top_games_sum_202205.csv', 'a') as output:
        output.write(str(i) + ',' + str(sum_volume[i]) + '\n')
