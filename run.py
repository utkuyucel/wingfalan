import yfinance as yf  # type: ignore
import pandas as pd  # type: ignore
import matplotlib.pyplot as plt
import seaborn as sns  # type: ignore
import os


class StockMomentum:
    def __init__(self, tickers, start_date):
        self.tickers = tickers
        self.start_date = start_date
        self.data = pd.DataFrame()
        self.adj_close_data = pd.DataFrame()

    def fetch_data(self):
        def fetch_ticker_data(ticker):
            # Explicitly set auto_adjust=True as its default has changed in yfinance
            df = yf.download(ticker, start=self.start_date, auto_adjust=True)[["Close"]]
            df = df.rename(columns={"Close": ticker})
            return df

        ticker_data = [fetch_ticker_data(ticker) for ticker in self.tickers]
        self.data = pd.concat(ticker_data, axis=1).dropna()
        self.adj_close_data = self.data.copy()

    def calculate_momentum(self, window=4):
        self.data = self.data.apply(
            lambda x: x.pct_change().rolling(window=window).mean()
        ).dropna()

    def plot_combined_chart(self):
        fig, ax1 = plt.subplots(figsize=(14, 8))
        sns.set(style="whitegrid")

        ax1.set_xlabel("Date", fontsize=14)
        ax1.set_ylabel("Close", fontsize=14)
        for ticker in self.tickers:
            ax1.plot(
                self.adj_close_data.index,
                self.adj_close_data[ticker],
                label=f"{ticker} Close",
                linewidth=2,
            )
        ax1.tick_params(axis="x", rotation=45)
        ax1.tick_params(axis="y")

        ax2 = ax1.twinx()
        ax2.set_ylabel("Momentum", fontsize=14)
        for ticker in self.tickers:
            ax2.plot(
                self.data.index,
                self.data[ticker],
                linestyle="--",
                label=f"{ticker} Momentum",
                linewidth=2,
                color="red"
            )   
        ax2.tick_params(axis="y")

        lines, labels = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines + lines2, labels + labels2, loc="upper left", fontsize="11")

        plt.title("Stock Close and Momentum Over Time", fontsize=16)
        plt.grid(True)
        plt.tight_layout()
        
        os.makedirs("img", exist_ok=True)
        ticker_str = "_".join([ticker.replace(".", "_") for ticker in self.tickers])
        file_path = f"img/stock_momentum_chart_{ticker_str}.png"
        plt.savefig(file_path)
        print(f"Plot saved to {file_path}")

    def main(self):
        self.fetch_data()
        self.calculate_momentum(window=4)
        self.plot_combined_chart()
        return self.data


if __name__ == "__main__":
    tickers = ["TUPRS"]
    tickers_mapped = [f"{ticker}.IS" for ticker in tickers]
    start_date = "2024-01-01"

    stock_momentum = StockMomentum(tickers_mapped, start_date)
    stock_momentum.main()
