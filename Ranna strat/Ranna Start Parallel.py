#import mplfinance as mpf
import matplotlib.dates as mpl_dates
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib import cm
from matplotlib.ticker import LinearLocator
import matplotlib.gridspec as gridspec
from mpl_toolkits.mplot3d import Axes3D
import math
import warnings
import time
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None
import multiprocessing
import os

nifty5 = pd.read_csv('./in.csv')
nifty5['EMA']=nifty5['Close'].ewm(span=5, adjust=False).mean()
c1 = pd.DataFrame(columns=['Date', 'Number of trades'])
c2 = pd.DataFrame(columns=['Date', 'Time','Balance'])

 #Number of slippage/minimum sl combos       
daysconsidered = 1807 #Upto 1807
lastdateconsidered = 0 #0 for latest
c1['Date'] = nifty5['Date']
c1['Number of trades']=0

c2['Date'] = nifty5['Date']
c2['Time'] = nifty5['Time']

pn=0
ln=0

def sell(i,j,tgt,sl,slp):
    global nifty5,pn,ln
    j+=1
    k=j
    for k in range(j,74):
        if nifty5['High'][i*75+k]>sl:
            ln+=1
            return k, sl
        if nifty5['Low'][i*75+k]<tgt:            
            pn+=1
            return k, tgt

    return k, nifty5['Close'][i*75+k]

def backtest(lock,ii,daysconsidered,lastdateconsidered,slippage,minsl,ns):
    global pn,ln,nifty5,c1,c2
    pn=0
    ln=0
    b=nifty5.Date.nunique()-lastdateconsidered
    
    a=b-daysconsidered
    c2['Balance'][a*75] = round(25*nifty5['Open'][a*75],-4)
    proftolossratio=4
    
    tgt=0.0
    sl=0.0
    slp=0.0
    leverage=5
    sellflag=1
    buyflag=0
    slip=slippage/100
    gap=0.05/100
    for i in range(a,b):
        if i>a:
            c2.at[i*75, 'Balance'] = c2.loc[i*75-1, 'Balance']
        n=max(1,math.floor(c2.at[i*75, 'Balance']/nifty5['Open'][i*75]))
        profit=0
        k=0
        for j in range(1,nifty5.Time.nunique()):
            if j<k+1:
                continue  

            if j!=k:
                c2.at[i*75+j, 'Balance'] = c2.loc[i*75+j-1, 'Balance']

            if sellflag==1 and nifty5['Open'][i*75+j-1]>nifty5['EMA'][i*75+j-1] and nifty5['Close'][i*75+j-1]>nifty5['EMA'][i*75+j-1]:
                if (min(nifty5['Open'][i*75+j-1],nifty5['Close'][i*75+j-1])-nifty5['EMA'][i*75+j-1])<gap*nifty5['Close'][i*75+j-1]:
                    if nifty5['Low'][i*75+j]<nifty5['Low'][i*75+j-1] and (nifty5['High'][i*75+j-1]-nifty5['Low'][i*75+j-1])>minsl:
                        slp=nifty5['Low'][i*75+j-1]
                        sl=nifty5['High'][i*75+j-1]
                        tgt=slp-(sl-slp)*proftolossratio
                        k, byp=sell(i,j,tgt,sl,slp)       
                        for j1 in range(j,k+1):
                            c2.at[i*75+j1, 'Balance'] = c2.loc[i*75+j1-1, 'Balance']
                        c1.at[i*75,'Number of trades'] += 1
                        c2.at[i*75+k,'Balance'] = c2.loc[i*75+k,'Balance']+n*(slp-byp)*leverage-nifty5['Close'][i*75+j]*slip
                        continue
                        
        if c2.at[i*75+j, 'Balance']<0:
            #print("Total Loss")
            break

    nt=c1[c1['Number of trades']!=0]['Number of trades'].mean()
    ddd=100*min(np.array((c2['Balance'][a*75:b*75:75]/c2['Balance'][a*75:b*75:75].cummax() - 1.0).cummin()))
    balance=c2.loc[i*75+j, 'Balance']
    ini=c2.loc[a*75,'Balance']
    nr=((balance-ini)/ini)*100
    if (ln+pn)!=0:
        popp=100*pn/(ln+pn)
    else:
        popp=0
    row1 = [minsl, slippage,nt, ddd, popp, nr]
    lock.acquire()
    try:
        c3=ns.df
        c3.loc[ii] = row1
        ns.df=c3
    finally:
        lock.release()

def main():
    global c3,nn,daysconsidered,lastdateconsidered
    nn=int(input('Enter nn value:'))
    threads = 10
    slippage_values = np.linspace(0,3,nn)
    minsl_values = np.linspace(0,30,nn)
    barlength=len(slippage_values) * len(minsl_values)
    strch = [' ']*(102)
    strch[0]='|'
    strch[-1]='|'
    ii=0
    c3 = pd.DataFrame(index=range(nn*nn),columns=['Minimum SL','Slippage','Number of trades','Maximum Drawdown','POP','Net Return'])

    
    lock = multiprocessing.Lock()
    mgr = multiprocessing.Manager()
    ns = mgr.Namespace()
    ns.df = c3
    os.system('cls')
    print('\n  '+"".join(strch)+' {:.2f}% Done. Estimated time left: {:.2f}s'.format(ii/barlength*100,0))
    start=time.time()
    for i in range(len(slippage_values)):
         for j in range(0,len(minsl_values),threads):
            start1=time.time()
            processes=[]
            for k in range(threads):
                p = multiprocessing.Process(target = backtest, args=(lock,ii, daysconsidered, lastdateconsidered, slippage_values[i], minsl_values[j+k],ns))
                p.start()
                processes.append(p)
                ii+=1
                
            for p in processes:
                p.join()

            strch[1:int(100*(ii/barlength))+1]=['█']*(int(100*ii/barlength))
            t1=(time.time()-start1)*(len(minsl_values)-j-1)*(len(slippage_values)-i-1)/threads
            hh=int(t1/3600)
            mm=int((t1-3600*hh)/60)
            ss=int(t1-3600*hh-60*mm)
            os.system('cls')
            print('\n  '+"".join(strch)+' {:.2f}% Done. Estimated time left: {}:{}:{}'.format(ii/barlength*100,hh,mm,ss))

    print('Actual time taken is: {:.2f} mins'.format((time.time()-start)/60))
    c4 = ns.df
    c4 = c4.sort_values(by = ['Minimum SL','Slippage'])
    c4.reset_index(inplace = True, drop = True)
    c4 = c4.fillna(0)
    c4.to_csv('out.csv',index=False)
    plott(c4,nn)

def plott(out,nn):
    nt=np.zeros([nn,nn])
    for i in range(nn):
        for j in range(nn):
            nt[i][j]=out.loc[i*nn+j,'Number of trades']
    md=np.zeros([nn,nn])
    for i in range(nn):
        for j in range(nn):
            md[i][j]=out.loc[i*nn+j,'Maximum Drawdown']
    pop=np.zeros([nn,nn])
    for i in range(nn):
        for j in range(nn):
            pop[i][j]=out.loc[i*nn+j,'POP']
    nr=np.zeros([nn,nn])
    for i in range(nn):
        for j in range(nn):
            nr[i][j]=out.loc[i*nn+j,'Net Return']
    fig = plt.figure(figsize=(30,20))
    Y = np.linspace(0,30,nn)
    X = np.linspace(0,3,nn)
    X, Y = np.meshgrid(X, Y)
    spec = gridspec.GridSpec(ncols=2, nrows=2, figure=fig)
    ax1 = fig.add_subplot(spec[0, 0], projection='3d')
    ax1.set_title("Number of Trades per Day")
    surf = ax1.plot_surface(X, Y, nt, cmap=cm.coolwarm,linewidth=0, antialiased=True)

    ax2 = fig.add_subplot(spec[0, 1], projection='3d')
    ax2.set_title("Maximum Drawdown")
    surf = ax2.plot_surface(X, Y, md, cmap=cm.coolwarm,linewidth=0, antialiased=True)

    ax3 = fig.add_subplot(spec[1, 0], projection='3d')
    ax3.set_title("Probability of Profit")
    surf = ax3.plot_surface(X, Y, pop, cmap=cm.coolwarm,linewidth=0, antialiased=True)

    ax4 = fig.add_subplot(spec[1, 1], projection='3d')
    ax4.set_title("Net Returns")
    surf = ax4.plot_surface(X, Y, nr, cmap=cm.coolwarm,linewidth=0, antialiased=True)
    plt.show()
    
if __name__ == "__main__":
    main()
