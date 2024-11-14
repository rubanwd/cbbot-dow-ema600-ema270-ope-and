import pandas as pd
from indicators import Indicators
import logging

class Strategies:
    def __init__(self, data_fetcher):
        self.indicators = Indicators()
        self.data_fetcher = data_fetcher  # Dependency to fetch real-time price

    def prepare_dataframe(self, historical_data):
        """
        Prepares the DataFrame from historical data, sorting and formatting it correctly.
        """
        df = pd.DataFrame(historical_data)
        df.columns = ["timestamp", "open", "high", "low", "close", "volume", "turnover"]
        df['close'] = df['close'].astype(float)
        df.sort_values('timestamp', inplace=True)
        return df

    def ema_trend_strategy(self, df):
        """
        Determines the trend based on EMA-600 and EMA-270.
        Returns 'uptrend' if EMA-90 > EMA-600, otherwise 'downtrend'.
        """
        df['ema_600'] = self.indicators.calculate_ema(df, 600)
        df['ema_120'] = self.indicators.calculate_ema(df, 120)

        ema_200 = df['ema_600'].iloc[-1]
        ema_270 = df['ema_270'].iloc[-1]

        logging.info(f"EMA-600: {ema_200}, EMA-270: {ema_270}")
        return 'uptrend' if ema_270 > ema_200 else 'downtrend'
    
    def sma_trend_strategy(self, df):
        """
        Determines the trend based on SMA-600 and SMA-270.
        Returns 'uptrend' if SMA-270 > SMA-600, otherwise 'downtrend'.
        """
        df['sma_600'] = self.indicators.calculate_sma(df, 600)
        df['sma_270'] = self.indicators.calculate_sma(df, 270)

        sma_600 = df['sma_600'].iloc[-1]
        sma_270 = df['sma_270'].iloc[-1]

        logging.info(f"SMA-600: {sma_600}, SMA-170: {sma_270}")
        return 'uptrend' if sma_270 > sma_600 else 'downtrend'

    def rsi_bollinger_macd_confirmation(self, df, trend, current_price):
        """
        Confirms trade signals using RSI, Bollinger Bands, and MACD cross.
        - For uptrend: RSI < 40, current price < lower Bollinger Band, or MACD line crosses above signal line (buy signal).
        - For downtrend: RSI > 60, current price > upper Bollinger Band, or MACD line crosses below signal line (sell signal).
        """
        # Calculate indicators
        df['rsi'] = self.indicators.calculate_rsi(df, 14)
        df['bollinger_upper'], df['bollinger_middle'], df['bollinger_lower'] = self.indicators.calculate_bollinger_bands(df)
        macd, macd_signal = self.indicators.calculate_macd(df)

        # Latest values
        rsi = df['rsi'].iloc[-1]
        lower_band = df['bollinger_lower'].iloc[-1]
        upper_band = df['bollinger_upper'].iloc[-1]
        macd_line = macd.iloc[-1]
        macd_signal_line = macd_signal.iloc[-1]
        prev_macd_line = macd.iloc[-2]
        prev_macd_signal_line = macd_signal.iloc[-2]

        logging.info(f"RSI: {rsi}, Current Price: {current_price}, Bollinger Bands: [{lower_band}, {upper_band}]")
        logging.info(f"MACD: {macd_line}, Signal: {macd_signal_line}, Previous MACD: {prev_macd_line}, Previous Signal: {prev_macd_signal_line}")

        # Confirmations using current price
        # if trend == 'uptrend' and (rsi < 30 or current_price < lower_band or
        #                            (prev_macd_line < prev_macd_signal_line and macd_line > macd_signal_line)):
        #     return 'buy'
        # elif trend == 'downtrend' and (rsi > 70 or current_price > upper_band or
        #                                (prev_macd_line > prev_macd_signal_line and macd_line < macd_signal_line)):
        #     return 'sell'
        # return None
    
        if trend == 'uptrend' and (rsi < 30 or current_price < lower_band):
            return 'buy'
        
        if trend == 'downtrend' and (rsi > 70 or current_price > upper_band):
            return 'sell'
        
        return None

