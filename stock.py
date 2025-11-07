from argparse import ArgumentParser
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def opt():
    parser = ArgumentParser()
    parser.add_argument('-m', '--money', help="The number of money for investment every month", type=float, default=40_000)
    parser.add_argument('-r', '--ratio', help="The ratio of stock to bond (stock/bond).", type=float, default=1.0)
    parser.add_argument('-y', '--year', help="The period of investment.", type=int, default=15)
    parser.add_argument('-b', '--bonus', help="The bonus every year.", type=float, default=140_000)
    parser.add_argument('-s', '--show', help="Showing the chart", action="store_true")

    return parser.parse_args()

def roi(stock, bond, total_investment):
    return ((stock + bond) / total_investment - 1) * 100

def print_label(msg: str):
    print("="*40 + f" {msg} " + "="*40)

def generate_monthly_factors(N, ratio=0.1, max_iter=10000):
    """
    產生 12 個因子，其乘積為 N , 且每個因子 ∈ [1 - ratio, 1 + ratio]
    
    參數：
        N (float): 目標乘積（例如 1.5)
        ratio (float): 每個因子的最大偏移比例（例如 0.1 表 ±10%)
        max_iter (int): 最多嘗試次數
        seed (int): 隨機種子（可選）
    
    回傳：
        np.ndarray: 長度為 12 的因子陣列，乘積 ≈ N
    """

    lower, upper = 1 - ratio, 1 + ratio
    for _ in range(max_iter):
        factors = np.random.normal(1, ratio/2, 12)
        scale = N / np.prod(factors)
        adjusted = factors * scale**(1/12)

        # tolerat 3 month dramatically change
        if ((adjusted >= lower) & (adjusted <= upper)).sum() >= 9 and np.all((adjusted >= 1-0.6) & (adjusted <= 1+0.6)):
            return adjusted - 1

    raise ValueError("Can't find factor")

def main(args):
    
    # option setting
    year = args.year
    bonus = args.bonus
    monthly_invest = args.money
    stock_bond_ratio = args.ratio
    is_show = args.show

    # Average annualized rate of return
    df = pd.read_csv("Annual_Returns.csv")
    stock_ret_rates = df['Rate'].to_numpy() / 100
    # exit()
    stock_rate = 0.08
    bond_rate = 0.015

    x_year = [0]
    y_total = [0]
    y_stock = [0]
    y_bond = [0]
    year_ret_rate = 1
    total_money = 0

    for i in range(year):
        print_label(f"{i+1} years")
        real_year_stock_rate = stock_ret_rates[i % len(stock_ret_rates)]
        month_stock_rates = generate_monthly_factors((1+real_year_stock_rate), ratio=0.2)

        year_stock_return = 1
        for j in range(12):
            if j == 11:
                funds = monthly_invest + bonus
            else:
                funds = monthly_invest
            total_money += funds
            stock_rate = month_stock_rates[j]
            year_ret_rate *= (1 + stock_rate)
            
            y_stock.append((y_stock[-1] + funds * stock_bond_ratio) * (1 + stock_rate))
            # y_stock.append(stock_rate) # watch the monthly stock rate
            x_year.append(i*12+j)
            y_bond.append(y_bond[-1] + funds * (1 - stock_bond_ratio))
            print(f"Monthly ROI: {roi(y_stock[-1], y_bond[-1], total_money):>8.4f}% , Month stock rate {stock_rate * 100:>8.4f}%")
        
        # assume return once per year
        y_bond[-1] = (y_bond[-1] + y_bond[-13] * (bond_rate))
        
        # year_ret_rate *= (year_stock_return * stock_bond_ratio + bond_rate * (1 - stock_bond_ratio))
        annyal_ret_rate = (year_ret_rate - 1) / (i + 1)
        print("")
        print(f"Total Property: {int(y_stock[-1] + y_bond[-1])}")
        print(f"Total ROI: {roi(y_stock[-1], y_bond[-1], total_money):.4f}%")
        print(f"Annualized ROI: {roi(y_stock[-1], y_bond[-1], total_money) / (i+1):.4f}%")
        print(f"Total Return Rate of Stock starting from first year: {year_ret_rate*100:.4f}%")
        print(f"Annualized ROI of Stock starting from first year: {annyal_ret_rate*100:.4f}%")
            
        # x_year.append(i+1)

    print_label("Summary")
    print(f"Investment per year: {monthly_invest*12 + bonus}")
    print(f"Total investment: {total_money}")
    print(f"Current property: {int(y_stock[-1] + y_bond[-1])}")
    y_stock = np.array(y_stock)
    y_bond = np.array(y_bond)

    # to K unit
    y_stock /= 1000
    y_bond /= 1000

    if is_show:
        plot_bond = stock_bond_ratio < 1.0
        show(x_year, y_stock, y_bond, plot_bond)

def show(x_year, y_stock, y_bond, plot_bond=False):
    # lable all point
    for i in range(0,len(x_year),12):
        plt.text(x_year[i], y_stock[i], f"{y_stock[i]:.2f}K", fontsize=9, ha='left', va='bottom')
        if plot_bond and not(i%5):
            plt.text(x_year[i], y_bond[i], f"{y_bond[i]:.2f}K", fontsize=9, ha='left', va='bottom')
    
    plt.plot(x_year, y_stock, label="Stock", marker='o', color='red')
    if plot_bond:
        plt.plot(x_year, y_bond, label="Bond", marker='x', color='blue')
    plt.xlabel("Month")
    plt.ylabel("Property (unit : k)")
    plt.legend()
    plt.show()

if __name__ == "__main__":
    args = opt()
    # np.random.seed(12)
    main(args)