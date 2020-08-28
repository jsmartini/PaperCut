import pandas as pd
import datetime


class TradeBS:

    """
    buy/sell trade
    """

    def __init__(self, buy_in: float, shares: int, id: str):
        self.name = id
        self.buy_in = buy_in
        self.shares = shares
        self.date = datetime.datetime.now().timestamp()

    def close(self, close_out: float):
        self.close_out = close_out
        diff = self.close_out - self.buy_in
        profit = round(diff * self.shares, 2)
        self.loss = False
        self.gain = False
        if profit < 0:
            self.loss = True
        if profit > 0:
            self.gain = True
        self.profit = 0.99925 * profit
        self.close = datetime.datetime.now.timestamp()

    def check_id(self, query):
        if query == self.name:
            return True
        return False

    def info(self):
        return {
            "trade_name": self.name,
            "buy_in": self.buy_in,
            "close_out": self.close_out,
            "shares": self.shares,
            "profit": self.profit,
            "loss": self.loss,
            "gain": self.gain,
            "init": str(self.date),
	    "end" : str(self.close)
        }

class TradeSSSBSS(TradeBS):

    """
    buy short // sell short
    """

    def __init__(self, buy_in, shares, id):
        super().__init__(buy_in, shares, id)

    def close(self, close_out):
        self.close_out = close_out
        diff = self.buy_in - self.close_out
        profit = 0.99925 * round(diff * self.shares, 2)
        self.loss = False
        self.gain = False
        if profit < 0:
            self.loss = True
        if profit > 0:
            self.gain = True
        self.profit = profit
        self.close = datetime.datetime.now().timestamp()

class PaperCut:
    """
    Paper Trading for small-scale chart algorithms

    only supports one trade at a time
    """

    def __init__(self, initial: float):
        self.Account = {
            "equity" : {
                "initial": initial,
                "current": initial
            },
            "trades" : {
                "open" : None,
                "closed" :[],
            }

        }
        self.max_trades="N/A"

    def __init__(self, initial: float, max_trades: int):
        self.Account = {
            "equity" : {
                "initial": initial,
                "current": initial
            },
            "trades" : {
                "open" : None,
                "closed" : [],
            }

        }
        self.max_trades = max_trades

    #regular buying
    def openBS(self, buy_in, shares, id):
        self.Account["trades"]["open"] = TradeBS(buy_in, shares, id)

    def closeBS(self, close_out):
        self.Account["trades"]["open"].close(close_out)
        self.Account["trades"]["closed"].append(self.Account["trades"]["open"])
        self.recompute_balance()

    #short selling
    def openSSS(self, buy_in, shares, id):
        self.Account["trades"]["open"]= TradeSSSBSS(buy_in, shares, id)

    def closeBSS(self, close_out):
        self.Account["trades"]["open"].close(close_out)
        self.Account["trades"]["closed"].append(self.Account["trades"]["open"])
        self.recompute_balance()

    def recompute_balance(self):
        balance = self.Account["equity"]["initial"]
        for trade in self.Account["trades"]["closed"]:
            balance += trade.info()["profit"]

    def get_free_cash(self):
        self.recompute_balance()
        return self.Account["equity"]["current"]

    def get_max_shares(self, price):
        return self.Account["equity"]["current"] / price

    def data_backup(self):
        trades = pd.DataFrame([x.info() for x in self.Account["trades"]["closed"]])
        trades.to_csv("trade-backup.csv")

    def algo_statistics(self):
        profit, success, fail, stag, volume = [0,0,0,0,0]
        if len(self.Account["trades"]["closed"]) == 0:
            return {
                "status": "waiting for first trade"
            }
        for trade in self.Account["trades"]["closed"]:
            trade = trade.info()
            profit += trade["profit"]
            if trade["gain"]:
                success += 1
            elif trade["loss"]:
                fail += 1
            else:
                stag += 1
            volume += trade["shares"]
        return {
            "profit": profit,
            "volume": volume,
            "trades": len(self.Account["trades"]["closed"]),
            "success" : success,
            "fail": fail,
            "stagnant": stag,
            "Gains %": str(round(success/len(self.Account["trades"]["closed"]), 2) * 100) + " %",
            "losses %": str(round(fail/len(self.Account["trades"]["closed"]), 2) * 100) + " %"
        }

    def end(self, file_name = "test.csv"):
        self.recompute_balance()
        if len(self.Account["trades"]["closed"]) >= self.max_trades:
            trades = pd.DataFrame([x.info() for x in self.Account["trades"]["closed"] ])
            print(trades.head(20))
            trades.to_csv(file_name)
            print(self.algo_statistics())
            exit("Exitting Paper Environment")
