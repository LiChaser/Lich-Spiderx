from ast import main
from mimetypes import init
import requests
import warnings
warnings.filterwarnings("ignore")

def Whether_Login(url):
    try:
        text=requests.get(url=url,timeout=0.1,verify=False)
        list=['passwd','user','login','register']
        for str in list :
            if text.status_code==200 and str in text:
                try:
                    print(f'存在{str}',str="")
                except:
                    pass    
    except requests.exceptions.RequestException as e:
        # 使用 pass 语句，当发生异常时，什么也不做，直接跳过
        pass


def main():
    URL=open('listdir/url.txt','r')
    for url in URL:
        Whether_Login(url)
if __name__ == '__main__':
    main()
