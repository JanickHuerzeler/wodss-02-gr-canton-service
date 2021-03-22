import requests
import os


def download_regionalportraets_excel():

    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname,'data','regionalportraets.xls')
    
    regionalporträts_2020_kennzahlen_aller_gemeinden = r'https://www.bfs.admin.ch/bfsstatic/dam/assets/11587763/master'
    resp = requests.get(regionalporträts_2020_kennzahlen_aller_gemeinden)
    with open(filename, 'wb') as output:
        output.write(resp.content)

if __name__ == '__main__':
    download_regionalportraets_excel()