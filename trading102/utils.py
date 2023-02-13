import json
from clint.textui import colored

def readConfig(config):
        with open(config,encoding='utf-8') as f:
            lines = f.readlines()

            C = {}
            listObj = []
            i = 0

            while True:
                try:
                    if lines[i].split()[0] != '':
                        C.update({lines[i].split()[0]:lines[i].split()[1]})
                        i +=1
                except:
                    listObj.append(C)
                    with open(r'BinanceAPIs.json','w',encoding='utf-8') as f:
                        json.dump(listObj,f,indent=4,ensure_ascii=False)

                    i+=1
                    C = {}

                    try:
                        lines[i].split()[0]
                    except:
                        break
            return  listObj[0]

def green(msg=""):
    print(colored.green(msg))

def red(msg=""):
    print(colored.red(msg))