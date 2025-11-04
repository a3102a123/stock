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
    bond_rate = 0.04

    x_year = [0]
    y_total = [0]
    y_stock = [0]
    y_bond = [0]
    total_ret_rate = 1

    for i in range(year):
        year_stock_rate = stock_ret_rates[i % len(stock_ret_rates)]
        month_stock_rates = generate_monthly_factors((1+year_stock_rate), ratio=0.2)
        for j in range(12):
            if j == 11:
                funds = monthly_invest + bonus
            else:
                funds = monthly_invest
            stock_rate = month_stock_rates[j]
            y_stock.append((y_stock[-1] + funds * stock_bond_ratio) * (1 + stock_rate))
            # y_stock.append(stock_rate)
            y_bond.append((y_bond[-1] + funds * (1 - stock_bond_ratio)) * (1 + bond_rate))
            x_year.append(j+1)
        
        total_ret_rate *= (1 + year_stock_rate * stock_bond_ratio + bond_rate * (1 - stock_bond_ratio))
        annyal_ret_rate = (total_ret_rate - 1) / (i + 1)
        print("="*40 + f" {i+1} years " + "="*40)
        print(f"Total Property: {int(y_stock[-1] + y_bond[-1])}")
        print(f"Total Return Rate: {total_ret_rate*100:.4f}%")
        print(f"Annualized Rate of Return: {annyal_ret_rate*100:.4f}%")
            
        # x_year.append(i+1)

    y_stock = np.array(y_stock)
    y_bond = np.array(y_bond)

    # to K unit
    # y_stock /= 1000
    y_stock *= 100
    y_bond /= 1000

    if is_show:
        plot_bond = stock_bond_ratio < 1.0
        show(x_year, y_stock, y_bond, plot_bond)
    

def generate_monthly_factors(N, ratio=0.1, max_iter=10000):
    """
    產生 12 個因子，其乘積為 N，且每個因子 ∈ [1 - ratio, 1 + ratio]
    
    參數：
        N (float): 目標乘積（例如 1.5）
        ratio (float): 每個因子的最大偏移比例（例如 0.1 表 ±10%）
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
        # TODO : limit value range not to too big
        if ((adjusted >= lower) & (adjusted <= upper)).sum() >= 9 and np.all((adjusted >= 1-0.6) & (adjusted <= 1+0.6)):
            return adjusted - 1

    raise ValueError("Can't find factor")

def show(x_year, y_stock, y_bond, plot_bond=False):
    # lable all point
    for i in range(len(x_year)):
        plt.text(x_year[i], y_stock[i], f"{y_stock[i]:.2f}K", fontsize=9, ha='left', va='bottom')
        if plot_bond and not(i%5):
            plt.text(x_year[i], y_bond[i], f"{y_bond[i]:.2f}K", fontsize=9, ha='left', va='bottom')
    
    plt.plot(x_year, y_stock, label="Stock", marker='o', color='red')
    if plot_bond:
        plt.plot(x_year, y_bond, label="Stock", marker='x', color='blue')
    plt.xlabel("Year")
    plt.ylabel("Property (unit : k)")
    plt.show()

if __name__ == "__main__":
    args = opt()
    np.random.seed(12)
    main(args)