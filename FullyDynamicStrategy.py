# Import necessary libraries
from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import talib.abstract as ta


class FullyDynamicStrategy(IStrategy):
    # Remove ROI-based exits by setting a very high threshold
    minimal_roi = {
        "0": 10  # Unrealistically high to ensure it's ignored
    }

    # Initial stop-loss configuration (-5%)
    stoploss =  -0.5 #-0.03

    # Use 5-minute candles
    timeframe = "5m"

    # Dynamic TP/SL constants
    initial_take_profit = 0.02  # 2% initial take-profit
    tp_increment = 0.01        # Increment TP by 1% on each profit level
    trailing_stop_loss = 0.02  # Lock in profit with a 2% trailing stop

    use_custom_stoploss = True

    # def custom_stoploss(self, pair: str, trade, current_time, current_rate, current_profit, **kwargs):
    #     """
    #     Custom stop-loss logic with dynamic TP and SL adjustments.
    #     """
    #     # If profit exceeds the initial take-profit level
    #     if current_profit >= self.initial_take_profit:
    #         # Move the stop-loss up to lock in profits
    #         return max(current_profit - self.trailing_stop_loss, self.stoploss)

    #     # Keep the initial stop-loss otherwise
    #     return self.stoploss

    def custom_stoploss(self, pair: str, trade, current_time,
                        current_rate, current_profit, **kwargs):
        # Calculate as `-desired_stop_from_open + current_profit` to get the distance between current_profit and initial price
        if current_profit > 0.40:
            return (-0.25 + current_profit)
        if current_profit > 0.25:
            return (-0.15 + current_profit)
        if current_profit > 0.20:
            return (-0.7 + current_profit)
        return 1




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
        # Disable fixed exit logic; exits are handled by custom_stoploss
        return dataframe
