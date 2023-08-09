##import mplfinance as mpf
##import matplotlib.dates as mpl_dates
##import matplotlib.pyplot as plt
##from datetime import datetime
##from matplotlib import cm
##from matplotlib.ticker import LinearLocator
##import matplotlib.gridspec as gridspec
##from mpl_toolkits.mplot3d import Axes3D
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

def backtest(lock,ii,daysconsidered,lastdateconsidered,minsl,ns):
    global pn,ln,nifty5,c1,c2
    pn=0
    ln=0
    b=int(1807-lastdateconsidered)
    
    a=int(b-daysconsidered)
    c2['Balance'][a*75] = 100000
    proftolossratio=4
    
    tgt=0.0
    sl=0.0
    slp=0.0
    leverage=35
    sellflag=1
    buyflag=0
    slip=1/100
    gap=0.05/100
    minsl=minsl/100
    profp=[]
    for i in range(a,b):
        if i>a:
            c2.at[i*75, 'Balance'] = c2.loc[i*75-1, 'Balance']
        #n=max(1,math.floor(c2.loc[i*75, 'Balance']/nifty5['Open'][i*75]))
        profit=0
        k=0
        for j in range(1,75):
            n=c2.loc[i*75, 'Balance']*leverage/nifty5['Open'][i*75]
            if j<k+1:
                continue  

            if j!=k:
                c2.at[i*75+j, 'Balance'] = c2.loc[i*75+j-1, 'Balance']

            if sellflag==1 and nifty5['Open'][i*75+j-1]>nifty5['EMA'][i*75+j-1] and nifty5['Close'][i*75+j-1]>nifty5['EMA'][i*75+j-1]:
                if (min(nifty5['Open'][i*75+j-1],nifty5['Close'][i*75+j-1])-nifty5['EMA'][i*75+j-1])<gap*nifty5['Close'][i*75+j-1]:
                    if nifty5['Low'][i*75+j]<nifty5['Low'][i*75+j-1] and (nifty5['High'][i*75+j-1]-nifty5['Low'][i*75+j-1])>minsl*nifty5['Open'][i*75+j-1]:
                        slp=nifty5['Low'][i*75+j-1]
                        sl=nifty5['High'][i*75+j-1]
                        tgt=slp-(sl-slp)*proftolossratio
                        k, byp=sell(i,j,tgt,sl,slp)       
                        for j1 in range(j,k+1):
                            c2.at[i*75+j1, 'Balance'] = c2.loc[i*75+j1-1, 'Balance']
                        c1.at[i*75,'Number of trades'] += 1
                        profit=(slp-byp)/byp
                        c2.at[i*75+k,'Balance'] = c2.loc[i*75+k,'Balance']*(1+profit*leverage)-slip*slp
                        profp.append(profit)
                        #print('Percentage Profit of {:.2f}% and slippage Rs {:.2f}'.format(profit*leverage*100,slip*slp))
                        continue
                        
            if c2.at[i*75+k, 'Balance']<0:
               #print("Total Loss")
                break
        if c2.at[i*75+k, 'Balance']<0:
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
    row1 = [minsl,minsl*nifty5[a*75:b*75]['Close'].mean(),lastdateconsidered,nt, ddd, popp, nr,np.array(profp).mean()]
    lock.acquire()
    try:
        #print(row1)
        c3=ns.df
        c3.loc[ii] = row1
        ns.df=c3
    finally:
        lock.release()

def main(): #last date considered from 0-take 169 for 7 years from starting, days considered 234 for a year.
    nn=10#int(input('Enter nn value:'))
    threads = min(nn,10)
    ld = np.linspace(169,169*7,7)
    minsl_values = np.linspace(0,0.15,nn)
    barlength=len(ld)*nn
    strch = [' ']*(102)
    strch[0]='|'
    strch[-1]='|'
    ii=0
    c3 = pd.DataFrame(index=range(barlength),columns=['Minimum SL','MinSL Abs','StartYear','Number of trades','Maximum Drawdown','POP','Net Return','AvgProfit'])
   
    lock = multiprocessing.Lock()
    mgr = multiprocessing.Manager()
    ns = mgr.Namespace()
    ns.df = c3
    os.system('cls')
    print('\n  '+"".join(strch)+' {:.2f}% Done. Estimated time left: {:.2f}s'.format(ii/barlength*100,0))
    start=time.time()
    for i in range(len(ld)):
         for j in range(0,nn,threads):
            start1=time.time()  
            processes=[]
            for k in range(threads):
                if (j+k)<nn:
                    p = multiprocessing.Process(target = backtest, args=(lock,ii, 234, ld[i], minsl_values[j+k],ns))
                    p.start()
                    processes.append(p)
                    ii+=1
                
            for p in processes:
                p.join()

            strch[1:int(100*(ii/barlength))+1]=['█']*(int(100*ii/barlength))
            t1=(time.time()-start1)*(nn-j-1)*(len(ld)-i-1)/threads
            hh=int(t1/3600)
            mm=int((t1-3600*hh)/60)
            ss=int(t1-3600*hh-60*mm)
            os.system('cls')
            print('\n  '+"".join(strch)+' {:.2f}% Done. Estimated time left: {}:{}:{}'.format(ii/barlength*100,hh,mm,ss))

    print('Actual time taken is: {:.2f} mins'.format((time.time()-start)/60))
    c4 = ns.df
    c4 = c4.sort_values(by = ['StartYear','Minimum SL'])
    c4.reset_index(inplace = True, drop = True)
    c4 = c4.fillna(0)
    c4.to_csv('out.csv',index=False)
##    plott(c4,nn)

##def plott(out,nn):
##    nt=np.zeros([nn,nn])
##    for i in range(nn):
##        for j in range(nn):
##            nt[i][j]=out.loc[i*nn+j,'Number of trades']
##    md=np.zeros([nn,nn])
##    for i in range(nn):
##        for j in range(nn):
##            md[i][j]=out.loc[i*nn+j,'Maximum Drawdown']
##    pop=np.zeros([nn,nn])
##    for i in range(nn):
##        for j in range(nn):
##            pop[i][j]=out.loc[i*nn+j,'POP']
##    nr=np.zeros([nn,nn])
##    for i in range(nn):
##        for j in range(nn):
##            nr[i][j]=out.loc[i*nn+j,'Net Return']
##    fig = plt.figure(figsize=(30,20))
##    Y = np.linspace(0,30,nn)
##    X = np.linspace(0,3,nn)
##    X, Y = np.meshgrid(X, Y)
##    spec = gridspec.GridSpec(ncols=2, nrows=2, figure=fig)
##    ax1 = fig.add_subplot(spec[0, 0], projection='3d')
##    ax1.set_title("Number of Trades per Day")
##    surf = ax1.plot_surface(X, Y, nt, cmap=cm.coolwarm,linewidth=0, antialiased=True)
##
##    ax2 = fig.add_subplot(spec[0, 1], projection='3d')
##    ax2.set_title("Maximum Drawdown")
##    surf = ax2.plot_surface(X, Y, md, cmap=cm.coolwarm,linewidth=0, antialiased=True)
##
##    ax3 = fig.add_subplot(spec[1, 0], projection='3d')
##    ax3.set_title("Probability of Profit")
##    surf = ax3.plot_surface(X, Y, pop, cmap=cm.coolwarm,linewidth=0, antialiased=True)
##
##    ax4 = fig.add_subplot(spec[1, 1], projection='3d')
##    ax4.set_title("Net Returns")
##    surf = ax4.plot_surface(X, Y, nr, cmap=cm.coolwarm,linewidth=0, antialiased=True)
##    plt.show()
##    
if __name__ == "__main__":
    main()
