from datetime import datetime as date
from colorama import Fore, Back, Style, init

init()

def error(msg):
    print(f'{Fore.LIGHTRED_EX}[{Back.BLUE}{date.now()}{Style.RESET_ALL} {Back.RED} ERROR {Style.RESET_ALL}{Fore.RED}]{Style.RESET_ALL}{msg}')

def info(msg):
    print(f'[{Fore.LIGHTBLUE_EX}{date.now()}{Style.RESET_ALL} {Fore.GREEN}INFO{Style.RESET_ALL}]{Style.RESET_ALL}{msg}')

def log(msg,code=1):
    if code==1:
        info(msg)
    
    else:
        error(msg)

if __name__=='__main__':#测试
    log('test info')
    log('test error',0)