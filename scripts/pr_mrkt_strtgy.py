import requests as rqsts
from bs4 import BeautifulSoup as BFS
import yfinance as yf
import pandas as pd
from datetime import datetime as dt, timedelta as td,date
from tabulate import tabulate
from colorama import Fore as Fr, Style as Sty, init as nt

nt(autoreset=True)

prft_blnc = 0
ntrl_bdgt = 500
rslts = []
mnt_dt_cch = {}
today=date(2025,1,3)
yesterday=date(2025,1,2)
def gt_prmkt_stcks():
    rl = "https://www.tradingview.com/markets/stocks-usa/market-movers-pre-market-gainers/"
    try:
        rspns = rqsts.get(rl)
        rspns.raise_for_status()
    except rqsts.exceptions.RequestException as r:
        print(f"{Fr.RED}Err ftchng prmkt dt: {r}")
        return []
    sp = BFS(rspns.content, "html.parser")
    rws = scrp_rws(sp)
    return [scrp_tckr(rw) for rw in rws]

def scrp_rws(sp):
    st_cls = {"row-RdUXZpkv","listRow"}
    return sp.find_all("tr", class_=lambda c: c and st_cls == set(c.split()))

def scrp_tckr(rw):
    tg_cls = {"apply-common-tooltip","tickerNameBox-GrtoTeat","tickerName-GrtoTeat"}
    t = rw.find("a", class_=lambda c: c and tg_cls == set(c.split()))
    r = rw.find_all("td")
    if r and len(r) > 4:
        pv = r[4].text
    else:
        pv = "0"
    return {"tckr": t.text if t else "NKN", "pr": ntrpr_pr(pv)}

def gt_dt(smb):
    if smb in mnt_dt_cch:
        return mnt_dt_cch[smb]
    d = yf.download(smb, period="max", interval="1m")
    mnt_dt_cch[smb] = d
    return d

def gt_clms(df, clm, smb, idx):
    try:
        return df[(clm, smb)].iloc[idx]
    except IndexError:
        return None

def gt_ystrdy_cls(df, smb):
    global yesterday
    yst = yesterday
    yst = pd.Timestamp(yst)
    ydf = df[df.index.date == yst.date()]
    return gt_clms(ydf, "Close", smb, -1)

def clc_stck(bdgt, prc):
    return bdgt / prc

def ntrpr_pr(pr):
    nm = pr.split()[0]
    try:
        nm_fl = float(nm)
    except:
        nm_fl = 0
    if len(pr.split()) == 2:
        mtp = pr.split()[1]
        if mtp == "K":
            nm_fl *= 1000
        elif mtp == "M":
            nm_fl *= 1000000
    return nm_fl

def cnvrt_ntr_pr(nm):
    if nm >= 1000000:
        return f"{nm/1000000}M"
    elif nm >= 1000:
        return f"{nm/1000}K"
    else:
        return str(nm)

def clc_rl_vl(tckr, pr):
    d = yf.download(tckr, period="max", interval="1d")
    rv = 0
    if not d.empty:
        av = d[("Volume",tckr)].iloc[-11:-1].mean()
        if av > 0:
            rv = pr / av
    else:
        print(f"{Fr.RED}N dt {tckr}")
    return rv

def stck_rls(frst, prv, prcnt, t, pr):
    if frst < 1:
        print(f"{Fr.RED}Skipping {t}. Open Price Below 1")
        return False
    if frst > 10:
        print(f"{Fr.RED}Skipping {t}. Open Price Above 10")
        return False
    if prcnt <= 10:
        print(f"{Fr.RED}Not Trading {t} .Change Not Enough")
        return False
    if pr< 1000000:
        print(f"{Fr.RED}Not Trading {t}. Pre Market Volume too Low. ")
        return False

def shld_buy(b_vl, s_vl, b_trshld, s_trshld):
    if s_vl >= b_vl * b_trshld:
        return True
    if s_vl <= b_vl * s_trshld:
        return True
    return False

def clc_prft(s_vl,b_vl,bdgt,trnsctn_cst):
    return (s_vl - b_vl) * (bdgt / b_vl) - trnsctn_cst

def clc_prc_dff(t, pr):

    global ntrl_bdgt, prft_blnc, rslts,today
    bdgt = ntrl_bdgt
    try:
        df = gt_dt(t)
        if df is None or df.empty:
            print(f"{Fr.RED}N dt {t}")
            return False
        df.index = pd.to_datetime(df.index)
        td_y =today
        if td_y.weekday() in [5, 6]:
            td_y -= td(days=(td_y.weekday() - 4))
        tdy_dt = df[df.index.date == td_y]
        if tdy_dt.empty:
            print(f"{Fr.RED}N dt {td_y} {t}")
            return False
        frst_opn = gt_clms(tdy_dt, "Open", t, 0)
        if frst_opn is None or frst_opn is None:
            print(f"{Fr.RED}Mssng dt {t}")
            return False
        prv_cls = gt_ystrdy_cls(df, t) if not df.empty else None
        if prv_cls is not None:
            cls_opn_ch = ((frst_opn - prv_cls) / prv_cls) * 100
        else:
            cls_opn_ch = None
        prcnt_df = ((frst_opn - prv_cls) / prv_cls) * 100 if prv_cls else 0
        rls_rslt = stck_rls(frst_opn, prv_cls, prcnt_df, t, pr)
        if rls_rslt is False:
            return False
        value=0
        index=0
        high=0
        low=0
        bght=False
        dt_30=yf.download(t,period="1d",interval="30m")

        l={"High":gt_clms(dt_30,"High",t,0),"Low":gt_clms(dt_30,"Low",t,0)}

        while bght==False:
            for i in range(0,30):
                value=gt_clms(tdy_dt,"Open",t,i)

                print(f"{Fr.BLUE}Checking minute {i}...")
                if(shld_buy(frst_opn,value,1.05,0.8)):
                    index=i
                    bght=True
                    break
            if(bght!=True):
                index=30
            bght=True

        

        prft = clc_prft(value,frst_opn,bdgt,5)
        prft_perc=(value-frst_opn)/frst_opn*100
        prft_blnc += prft
        rv = clc_rl_vl(t, pr)
        rslts.append({
            "Ticker": t,
            "Bought at": frst_opn,
            "Sold at ": value,
            "Minute/ Index ": index,
            "High":l["High"],
            "Max-Profit": clc_prft(l["High"],frst_opn,bdgt,5),
            "Low": l["Low"],
            "Max-Loss":clc_prft(l["Low"],frst_opn,bdgt,5),
            "Premarket Volume": cnvrt_ntr_pr(pr),
            "RVOL": rv,
            "Profit/Loss(%)":prft_perc,
            "Profit/Loss($)": prft,
            "Profit Balance": prft_blnc,
        })
        print(f"{Fr.GREEN}Ticker: {t}")
        print(f" {Sty.BRIGHT}Bought at: {frst_opn:.2f}")
        print(f" {Sty.BRIGHT}Sold at: {value:.2f}")
        print(f" {Sty.BRIGHT}Profit/Loss(%): {prft_perc}%")
        print(f" {Sty.BRIGHT}Blnc: {prft_blnc:.2f}\n")
        return 2 if prft > 0 else 1
    except Exception as x:
        print(f"{Fr.RED}Err {t}: {x}")
        return False

def rrprt():
    tckrs = gt_prmkt_stcks()
    ttl_tckrs = len(tckrs)
    sccssfll_trds = 0
    print(f"{Fr.CYAN}Nlyzng {ttl_tckrs} tckrs...\n")
    for t in tckrs:
        rslt = clc_prc_dff(t["tckr"], t["pr"])
        if rslt == 2:
            sccssfll_trds += 1
        elif rslt is False:
            ttl_tckrs -= 1
    if ttl_tckrs > 0:
        pc_gn = (sccssfll_trds / ttl_tckrs) * 100
    else:
        pc_gn = 0
    print(f"{Fr.YELLOW}\Summary:\n{'='*40}")
    print(f"{Fr.GREEN}Final Balance: {prft_blnc:.2f}")
    print(f"{Fr.GREEN}Succesful Trades: {sccssfll_trds} / {ttl_tckrs}")
    print(f"{Fr.GREEN}Success Rate: {pc_gn:.2f}%")
    
    if rslts:
        srt_r = sorted(rslts, key=lambda x: x["Profit/Loss($)"], reverse=True)
        tp_p = srt_r[0]
        wrst_p = srt_r[-1]
        print(f"\n{Fr.BLUE}Tp: {tp_p['Ticker']} (+{tp_p['Profit/Loss(%)']:.2f}%)")
        print(f"{Fr.RED}Wrst: {wrst_p['Ticker']} ({wrst_p['Profit/Loss(%)']:.2f}%)")
        print(f"\n{Fr.BLUE}Top Performers:")
        print(tabulate(srt_r[:3], headers="keys", tablefmt="fancy_grid", floatfmt=".2f"))
        print(f"\n{Fr.RED}Worst Performers:")
        print(tabulate(srt_r[-3:], headers="keys", tablefmt="fancy_grid", floatfmt=".2f"))

def mn():
    rrprt()
   

mn()
