import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time
import os
import sys
from selenium import webdriver
plt.style.use('fivethirtyeight')

num = 1000
while num > 6:
    print('1: SMT\n2: AAPL\n3: IBM\n4: ARVL\n5: Type Stock Symbol\n6: Exit Program\nStock type: ')
    num = int(input())
    if num == 1:
        stock = "SMT.L"
    elif num == 2:
        stock = "AAPL"
    elif num == 3:
        stock = "IBM"
    elif num == 4:
        stock = 'ARVL'
    elif num == 5:
        print('Stock symbol: ')
        stock = str(input())
    elif num == 6:
        sys.exit()

file = stock + '.csv'
location = 'C:\\Users\\glens\\Downloads\\'
path = os.path.join(location, file)

#Delete current downloaded market data if present
if os.path.isfile(path) == 1:
    os.remove(path)

PATH = "C:\Program Files (x86)\chromedriver.exe"
driver = webdriver.Chrome(PATH)

#Minimise window
driver.minimize_window()

#Open website
site = "https://uk.finance.yahoo.com/quote/" + stock + "/history/?guce_referrer=aHR0cHM6Ly93d3cuZ29vZ2xlLmNvb/S8&guce_/" \
                                                       "refer/rer_sig=AQAAAJ9_y5cVU7UWPU6_x27JjeyjEndyvBOpnW-ty58zVeMyZ/" \
                                                       "DAY2b1fjfsxWMX6N71H35221sfGtXQIBa9dc/lmiZI2XBFrkdw//" \
                                                       "OCbhkrcriXYTk1nW4ZrlQzAMau8qdBJZmt-Cdb2-v1Fv0fn7eR7H_L-8-FagPvs/" \
                                                       "Ds-SvE4EQCBGHOl&guccounter=2"
driver.get(site)
#Select scale
driver.find_element_by_xpath("//*[@id='Col1-1-HistoricalDataTable-Proxy']/section/div[1]/div[1]/div[1]/div").click()
#Click button to display 5 years of data
driver.find_element_by_xpath("//*[@id='dropdown-menu']/div/ul[2]/li[3]/button").click()
#Click download
driver.find_element_by_xpath("//*[@id='Col1-1-HistoricalDataTable-Proxy']/section/div[1]/div[2]/span[2]/a").click()
#If file has downloaded, close window
while os.path.isfile(path) == 0:
    time.sleep(1)
print(stock, 'Data Successfully Downloaded')
driver.close()

#Import data
data = pd.read_csv(path)

#Create data frames for 30-day rolling average and standard deviation
Av = pd.DataFrame()
Av['50 Day'] = data['Adj Close'].rolling(window=50).mean()
Av['200 Day'] = data['Adj Close'].rolling(window=200).mean()
Av['Grad'] = np.gradient(Av['50 Day'])

#Create function to signal buy or sell
def buy_sell(data):
    sigPriceBuy = []
    sigPriceSell = []
    flag = -1

    for i in range(len(data)):
        if Av['50 Day'][i] < Av['200 Day'][i] or Av['Grad'][i] > 4:
        #if ((data['Adj Close'][i] - Av['50 Day'][i])/data['Adj Close'][i] < -0.04 and Av['Grad'][i] > 0) or Av['Grad'][i] > 4:
            if flag != 1:
                sigPriceBuy.append(data['Adj Close'][i])
                buy_price = data['Adj Close'][i]
                sigPriceSell.append(np.nan)
                flag = 1
            else:
                sigPriceBuy.append(np.nan)
                sigPriceSell.append(np.nan)
        elif (Av['50 Day'][i] - Av['200 Day'][i] > 0) and (Av['50 Day'][i] - Av['200 Day'][i] < 10):
            if flag == 1:
                sigPriceBuy.append(np.nan)
                sigPriceSell.append(data['Adj Close'][i])
                flag = 0
            else:
                sigPriceBuy.append(np.nan)
                sigPriceSell.append(np.nan)
        else:
            sigPriceBuy.append(np.nan)
            sigPriceSell.append(np.nan)
    if flag == 1:
        sigPriceSell[i - 1] = data['Adj Close'][i - 1]
    return sigPriceBuy, sigPriceSell

#Create function to calculate return
buy_sell = buy_sell(data)
def algo_rtn(buy_sell):
    buy = 0
    sell = 0
    for i in range(len(buy_sell[0])):
        # print(i,' ',buy_sell[0][i])
        if type(buy_sell[0][i]) == np.float64:
            buy = buy + buy_sell[0][i]
        elif type(buy_sell[1][i]) == np.float64:
            sell = sell + buy_sell[1][i]
    Rtn = round(((sell - buy) * 100 / buy), 2)
    return (Rtn)

#Print return
print('Return =',algo_rtn(buy_sell),'%')

#Visualise data from buy_sell function
plt.scatter(data.index, buy_sell[0], label='buy', marker='^', color='green')
plt.scatter(data.index, buy_sell[1], label='sell', marker='v', color='red')
#Plot graphs
plt.plot(data['Adj Close'], label=stock, linewidth=1)
plt.plot(Av['50 Day'], label='50 Day Mean', linewidth=1)
plt.plot(Av['200 Day'], label='200 Day Mean', linewidth=1)
plt.legend(loc='upper left', prop={'size': 10})
plt.show()