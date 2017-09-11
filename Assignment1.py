# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import bs4
import urllib.request 
import pandas as pd
import datetime as dt
import locale
locale.setlocale(locale.LC_ALL,'English')

# Get trading price using beautiful soup
def get_price(Ticker):
    url = "https://finance.yahoo.com/quote/"+Ticker +"?p="+Ticker
    page=urllib.request.urlopen(url)
    soup = bs4.BeautifulSoup(page,'html.parser')
    span = soup.find_all("span",{"class" : "Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"})
    market_price = span[0].text
    return market_price

'''
Convert dictionary to data frame 
Convert Maket,WAP,UPL,RPL column to currency type
Convert Position column to string type 
'''
def convert_dic_to_table(dic):
    table = pd.DataFrame(dic,columns=dic.keys())
    table['Market'] =pd.Series(map(lambda x: locale.currency(x,grouping = True),table['Market']))
    table['WAP']  = pd.Series(map(lambda x: locale.currency(x,grouping = True), table['WAP']))
    table['UPL']  = pd.Series(map(lambda x: locale.currency(x,grouping = True), table['UPL']))
    table['RPL']  = pd.Series(map(lambda x: locale.currency(x,grouping = True), table['RPL']))
    table['Position']  = pd.Series(map(lambda x: str(int(x)), table['Position']))
    table.iloc[5,3:6] = ''
    table.iloc[5,1] = table.iloc[5,2]
    return table

'''
Initialize PnL by creating a PnL dictionary with initial value
and convert it into data frame
'''
def init_PnL_table():
    dic = {'Ticker':[],'Position':[],'Market':[],'WAP':[],'UPL':[],'RPL':[]}
    Ticker = ['AAPL','AMZN','INTC','MSFT','SNAP']
    for t in Ticker:  
        dic['Ticker'].append(t)
        dic['Position'].append(int(0))
        dic['Market'].append(float(get_price(t)))
        dic['WAP'].append(float(0))
        dic['UPL'].append(float(0))
        dic['RPL'].append(float(0))
    dic['Ticker'].append('Cash')
    dic['Position'].append(int(10000000))
    dic['Market'].append(float(10000000))
    dic['WAP'].append(float(0))
    dic['UPL'].append(float(0))
    dic['RPL'].append(float(0))
    table =convert_dic_to_table(dic) 
    return table,dic

'''
Start a new trading by ask console input about the order information
and store all inputs into a list
'''
def trade():
    while(True):
        Ticker_list = ['AAPL','AMZN','INTC','MSFT','SNAP']
        print('1 AAPL\n2 AMZN\n3 INTC\n4 MSFT\n5 SNAP') 
        ticker = input('Enter the corresponding number for the stock from the list to trade\n')
        quantity = int(input('Enter quantity (e.g 1000)\n') )
        side = input('Buy/Sell (e.g Buy)\n') 
        confirm = input('Confirm ?(Y/N)\n') 
        if confirm == 'Y':
            executed_price = float(get_price(Ticker_list[int(ticker)-1]))
            return [side,Ticker_list[int(ticker)-1],quantity,executed_price,str(dt.datetime.now())]
        else:
            continue


#Create the menu list and ask console input for item to choose
def menu():
    print('1 Trade\n2 Show Blotter\n3 Show P/L\n4 Quit\n')
    action = input('pelease enter the corresponding number to proceed\n')
    return action

'''
Take a new trade and covert Executed Price into currency type
and convert Quantity into string type
Add the new trade into blotter dataframe and sort it
'''
def add_trade_to_blotter(blotter_table,trade):
    trade[2] = str(trade[2])
    trade[3] = locale.currency(trade[3],grouping = True)
    blotter_table.loc[-1] = trade
    blotter_table.index = blotter_table.index + 1  
    blotter_table=blotter_table.sort_index()
    return(blotter_table)

#Update WAP,Cash Balance and Position after most recent trade
def update_wap_cash_postion_rpl(PnL_dic,ticker,trade_price,trade_quantity,side):
    stock_to_update=PnL_dic['Ticker'].index(ticker)
    trade_cost = trade_price*trade_quantity
    if side =='Buy':
        prev_position=PnL_dic['Position'][stock_to_update]
        prev_wap = PnL_dic['WAP'][stock_to_update]
        PnL_dic['WAP'][stock_to_update]= (prev_wap*prev_position+trade_cost)/(prev_position+trade_quantity)
        PnL_dic['Position'][stock_to_update]+= trade_quantity
        PnL_dic['Position'][-1]-= trade_cost
        PnL_dic['Market'][-1]-= trade_cost
    else:
        PnL_dic['Position'][stock_to_update]-= trade_quantity
        PnL_dic['Position'][-1]+= trade_cost
        PnL_dic['Market'][-1]+= trade_cost
        PnL_dic['RPL'][stock_to_update] = trade_quantity*(trade_price-PnL_dic['WAP'][stock_to_update])
         
    return PnL_dic

#Update UPL according to current market price for each Ticker
def update_upl(PnL_dic):
    for i in range(0,len(PnL_dic['Ticker'])-1):
        market_price = float(get_price(PnL_dic['Ticker'][i]))
        PnL_dic['Market'][i] = market_price
        PnL_dic['UPL'][i]=PnL_dic['Position'][i]*(market_price-PnL_dic['WAP'][i]) 
    return PnL_dic


#Initialize PnL table and blotter table    
PnLt,PnLd = init_PnL_table()
blotter_dic = {'Side':[],'Ticker':[],'Quantity':[],'Executed Price':[],'Time':[]}
blotter_table =pd.DataFrame(blotter_dic,columns = blotter_dic.keys())

print('Welcome to use the system\n')

'''
Go through different items in the menu according to console input(1,2,3,4)
1 for enter new trade and update blotter table and PnL all columns except UPL
because UPL need real time update of market price when uesr ask to look PnL
2 for show the blotter table
3 for update UPL and show PnL table 
4 for exit the program
'''
while(True):
    action=menu()    
    if action== '3':
        PnLd = update_upl(PnLd)
        PnLt = convert_dic_to_table(PnLd)
        print(PnLt)
        action =input('Press Enter to go back to main menu\n')
        continue
    elif action == '1':
        new_trade = trade()
        PnLd=update_wap_cash_postion_rpl(PnLd,new_trade[1],new_trade[3],new_trade[2],new_trade[0])
        blotter_table = add_trade_to_blotter(blotter_table,new_trade)   
        action =input('Your trade has been executed,press Enter to go back to main menu\n')
        continue
    elif action == '2':
        if blotter_table.empty:
            print('No trade has been make yet')
        else:
            print(blotter_table)
        action =input('Press Enter to go back to main menu\n')
        continue
    elif action =='4':
        break
    else:
        print('Invaild input, go back to main menu\n')




    