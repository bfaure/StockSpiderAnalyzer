from os import system,remove
from paramiko import SSHClient
from scp import SCPClient
from datetime import datetime,timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from time import time

def fetch_remote_data(ticker='AAPL'): # loads in all historical data for provided ticker
    print("Loading price data for %s..."%ticker)
    server_ip='192.168.1.17' # ip where StockSpider is currently running 
    server_user='pi' # username of device running StockSpider 
    server_path='/home/pi/Desktop/StockSpider' # path where StockSpider is installed on server
    scp=None # client interface to remote server
    server_password=input("Enter server password: ")
    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.connect(server_ip,port=22,username=server_user,password=server_password)
    scp = SCPClient(ssh.get_transport())
    t0=time()
    scp.get('%s/data/%s.tsv'%(server_path,ticker),'%s.tsv'%ticker)
    print("Took %d seconds to fetch %s.tsv"%(time()-t0,ticker))
    return '%s.tsv'%ticker

class Stock:
    def __init__(self,ticker,name=None):
        self.name=name 
        self.ticker=ticker
        self.prices,self.dates=[],[]
        self.SMA={}
    def append(self,price,date):
        self.prices.append(float(price))
        self.dates.append(datetime.utcfromtimestamp(int(date))-timedelta(hours=5,minutes=0))
    def __repr__(self):
        retstr='Date\t\t\t%s Price\n'%self.ticker
        retstr+=('_'*30)+"\n"
        for price,date in zip(self.prices,self.dates):
            retstr+='%s\t$%0.2f\n'%(date.strftime('%Y-%m-%d %H:%M:%S'),price) 
        return retstr
    def get_formatted_dates(self,format='%Y-%m-%d %H:%M:%S'):
        dates=[]
        for date in self.dates:
            dates.append(date.strftime(format))
        return dates
    def strip_off_hours(self): # remove all data not within extended trading hours (8AM-6PM)
        new_prices,new_dates=[],[]
        for price,date in zip(self.prices,self.dates):
            if date.weekday()<5 and date.hour>=7 and date.hour<=18:
                new_dates.append(date)
                new_prices.append(price)
        self.prices,self.dates=new_prices,new_dates
    
def parse_data(fname):
    stock=Stock(fname.split("/")[-1].split(".")[0])
    with open(fname,'r') as f:
        lines=f.read().split('\n')
        for line in lines:
            items=line.split("\t")
            if len(items)==2 and items[0]!='Datetime':
                stock.append(items[1].strip(),items[0])
    stock.strip_off_hours()
    return stock

def plot_price(stock):
    fig, ax = plt.subplots(1)
    # fig.autofmt_xdate()
    # xfmt = mdates.DateFormatter('%d-%m-%y %H:%M:%S')
    # ax.xaxis.set_major_formatter(xfmt)
    #plt.plot(stock.dates,stock.prices)
    plt.plot(stock.prices)
    plt.ylabel('%s Price ($)'%stock.ticker)
    plt.show()

def plot_SMA(stock):
    fig, ax = plt.subplots(nrows=2,ncols=1)
    fig.autofmt_xdate()
    xfmt = mdates.DateFormatter('%d-%m-%y %H:%M:%S')
    for i,row in enumerate(ax):
        if i==0:
            row.xaxis.set_major_formatter(xfmt)
            row.plot(stock.dates,stock.prices)
            plt.ylabel('%s Price ($)'%stock.ticker)
        if i==1:
            row.plot(stock.dates,stock.SMA[10])
    plt.show()

def SMA(stock,n_days=5):
    moving_average=[]
    buffer=[]
    for price in stock.prices:
        buffer.append(price)
        if len(buffer)==n_days:
            moving_average.append(sum(buffer))
            buffer=buffer[1:]
        else:
            moving_average.append(None)
    stock.SMA[n_days]=moving_average
    return stock

#fetch_remote_data()
stock=parse_data('AAPL.tsv')
plot_price(stock)
# stock=SMA(stock,10)
# plot_SMA(stock)


