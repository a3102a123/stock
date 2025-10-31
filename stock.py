from argparse import ArgumentParser
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def opt():
    parser = ArgumentParser()
    parser.add_argument('-m', '--money', help="The number of money for investment every month", type=float, default=40_000)
    parser.add_argument('-r', '--ratio', help="The ratio of stock to bond (stock/bond).", type=float, default=1.0)
    parser.add_argument('-p', '--period', help="The period of investment (unit : year).", type=int, default=15)
    parser.add_argument('-b', '--bonus', help="The bonus every year.", type=float, default=140_000)

    return parser.parse_args()

def main(args):
    
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

    for i in range(args.period):
        stock_rate = stock_ret_rates[i % len(stock_ret_rates)]
        funds = args.money * 12 + args.bonus
        y_stock.append((y_stock[-1] + funds * args.ratio) * (1 + stock_rate))
        y_bond.append((y_bond[-1] + funds * (1 - args.ratio)) * (1 + bond_rate))
        total_ret_rate *= (1 + stock_rate * args.ratio + bond_rate * (1 - args.ratio))
            
        x_year.append(i+1)
    
    annyal_ret_rate = total_ret_rate / args.period
    print(f"Total Return Rate: {total_ret_rate*100:.4f}%")
    print(f"Annualized Rate of Return: {annyal_ret_rate*100:.4f}%")

    y_stock = np.array(y_stock)
    y_bond = np.array(y_bond)

    # to K unit
    y_stock /= 1000
    y_bond /= 1000

    # lable all point
    for i in range(len(x_year)):
        plt.text(x_year[i], y_stock[i], f"{y_stock[i]:.2f}K", fontsize=9, ha='left', va='bottom')
        if args.ratio < 1.0 and not(i%5):
            plt.text(x_year[i], y_bond[i], f"{y_bond[i]:.2f}K", fontsize=9, ha='left', va='bottom')
    
    plt.plot(x_year, y_stock, label="Stock", marker='o', color='red')
    if args.ratio < 1.0:
        plt.plot(x_year, y_bond, label="Stock", marker='x', color='blue')
    plt.xlabel("Year")
    plt.ylabel("Property (unit : k)")
    plt.show()

if __name__ == "__main__":
    args = opt()
    main(args)