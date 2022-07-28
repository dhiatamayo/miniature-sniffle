#!/usr/bin/python3
"""
Auto app icons and desc script. Automatically parsed app icons from playstore and appstore (web not supported yet).
Input is appmap/appid. Descriptions manually written as playstore/appstore description might be misleading and not neutral.
After running the script, please also check the changes using scripts in ~/nio-class-webassets/scripts/ (description_validator.py and check_image_format.py)
Pre-requisites: ImageMagick (brew install imagemagick), bs4 (pip install bs4), pillow (pip install pillow)
note: change where nio-signatures and nio-class-webassets repo located in your own device
"""

import json
import os
import requests
import time
from bs4 import BeautifulSoup
from PIL import Image

### define functions
def get_image_url_playstore (url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    images_src = []
    a = soup.findAll("img")
    for i in a:
        images_src.append(i.get("src"))
    app_icon_url = images_src[0]
    return app_icon_url
    
def get_image_url_appstore (url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    images_src = []
    a = soup.findAll("source")
    for i in a:
        img_url = (i.get("srcset").split(',')[0]).split(' ')[0]
        images_src.append(img_url)
    app_icon_url = images_src[1]
    return app_icon_url

def image_write_to_file (appid, app_icon_url):
    img_data = requests.get(app_icon_url).content
    icon_name = str(appid) + ".png"
    img_path = "../icons_appmap/%s" %icon_name
    with open(img_path, 'wb') as handler:
        handler.write(img_data)
    os.system("mogrify -trim -resize 100x100 -gravity center -background matte -extent 100x100 %s && mogrify -trim %s" %(img_path,img_path))

def remove_transparency(im, bg_colour=(255, 255, 255)):
    if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):
        alpha = im.convert('RGBA').split()[-1]
        bg = Image.new("RGBA", im.size, bg_colour + (255,))
        bg.paste(im, mask=alpha)
        return bg
    else:
        return im

def desc_compiler(appid, description, url):
    w = {}
    w = {"appmap": int(appid),
         "description": description,
         "url": url
        }
    return w

def write_json(new_desc, filename='../descriptions_appmap/descriptions.json'):
    with open(filename,'r+') as exst_desc:
        exst_desc_data = json.load(exst_desc)
        exst_desc_data.append(new_desc)
        exst_desc.seek(0)
        json.dump(exst_desc_data, exst_desc, indent = 4, ensure_ascii=False)


### load appmap as json from nio-signatures
appmap = json.load(open("../../nio-signatures/appmap/appmap.json"))

### input appmap
input_appid = []
appid = ''
while appid != 'N':
    appid = input("Input appmap/appid (type N if there are no more appmap/appid):" + "\n")
    if appid == 'N':
        break
    elif appid.isdigit() == False:
        print('Appmap/appid must be integer')
    else:
        input_appid.append(appid)

### find url in sig-category.conf file
app_dict = {}
for app in appmap:
    try:
        appmap_name = app["application_full_name"]
        appmap_id = app["application"]
        for appid in input_appid:
            if appmap_id == appid:
                category = appmap_name.split('/')[0]
                appname = appmap_name.split('/')[1]
                sig_path = "../../nio-signatures/sigs/sig-%s.conf" % category
                sig = open(sig_path ,"r")
                found = -1
                for line in sig:
                    if found >= 2 and line.startswith('url'):
                        line = (line.strip().lstrip('url={"').rstrip('"}')).split('","')
                        for url in line:
                            app_url = ''
                            if 'apps.apple.com' in url:
                                app_url = url
                                break  
                            elif 'play.google.com' in url:
                                app_url = url
                                break
                            else:
                                app_url = url
                                continue
                        app_dict[appid] = [appname, app_url]
                        break
                    elif found > 0:
                        found += 1
                    else:
                        searchphrase = appname
                        if searchphrase in line:
                            found = 1
    except KeyError:
        pass

### image process and write
for appid in app_dict.keys():
    app_url = app_dict[appid][1]
    if 'apps.apple.com' in app_url:
        app_icon_url = get_image_url_appstore(app_url)
        image_write_to_file(appid, app_icon_url)
        print('%s.png has been added to icons_appmap.' %appid)
    elif 'play.google.com' in app_url:
        app_icon_url = get_image_url_playstore(app_url)
        image_write_to_file(appid, app_icon_url)
        print('%s.png has been added to icons_appmap.' %appid)
    else:
        try:
            app_icon_url = get_image_url_appstore(app_url)
            image_write_to_file(appid, app_icon_url)
            print('%s.png has been added to icons_appmap.' %appid)
        except Exception:
            try:
                app_icon_url = get_image_url_playstore(app_url)
                image_write_to_file(appid, app_icon_url)
                print('%s.png has been added to icons_appmap.' %appid)
            except Exception:
                print('Cannot parse app icon for %s:%s from the url. Please find the icon manually.' %(appid,app_dict[appid][0]))

### manually write description
for appid in app_dict.keys():
    print()
    print('The app name is %s' %app_dict[appid][0])
    description = input("Write the description: " + "\n")
    if description.endswith('.') is False:
        description = '%s.' %description
    header = description.split()[0]
    description = description.replace(header,header.replace(header[0],header[0].capitalize()))
    url = app_dict[appid][1]
### add to description.json
    write_json(desc_compiler(appid,description,url))

print('Done!')
