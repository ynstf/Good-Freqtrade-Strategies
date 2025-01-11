# Import necessary libraries
from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import talib.abstract as ta

class EnhancedIndicatorStrategy(IStrategy):
    # Define the strategy parameters
    # Minimal ROI (Take Profit)
    minimal_roi = {
        "0": 0.01,  # Take profit at 1% ROI immediately
    }

    # Stoploss configuration (-5%)
    stoploss = -0.05

    # Use 5-minute candles
    timeframe = "5m"

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Add indicators to the dataframe.
        """
        # Add RSI indicator (14-period)
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)

        # Add MACD indicators (standard settings)
        macd = ta.MACD(dataframe)
        dataframe["macd"] = macd["macd"]
        dataframe["signal"] = macd["macdsignal"]

        # Add EMA for trend confirmation (200-period)
        dataframe["ema200"] = ta.EMA(dataframe, timeperiod=200)

        # Add Stochastic RSI
        stoch = ta.STOCH(dataframe)
        dataframe["stoch_k"] = stoch["slowk"]
        dataframe["stoch_d"] = stoch["slowd"]

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Define entry conditions.
        """
        dataframe.loc[
            (
                # Buy when RSI is below 40 (relaxed oversold)
                (dataframe["rsi"] < 40)
                &
                # MACD is above signal OR trending upwards
                (
                    (dataframe["macd"] > dataframe["signal"]) |
                    (dataframe["macd"] > dataframe["macd"].shift(1))
                )
                &
                # Price is above the 200 EMA (bullish trend confirmation)
                (dataframe["close"] > dataframe["ema200"])
                &
                # Stochastic RSI is below 20 (oversold)
                (dataframe["stoch_k"] < 20)
            ),
            "enter_long",
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Define exit conditions.
        """

        return dataframe
