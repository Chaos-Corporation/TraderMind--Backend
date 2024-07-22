from candlestick.patterns.candlestick_finder import CandlestickFinder

class TweezerBottoms(CandlestickFinder):
    def __init__(self, target=None):
        super().__init__(self.get_class_name(), 2, target=target)  # This pattern needs 2 candles

    def logic(self, idx):
        if idx < 1:
            return False  # Ensure there are at least two candles before this point

        first_candle = self.data.iloc[idx - 1]
        second_candle = self.data.iloc[idx]

        # Check if both candles have similar lows
        if abs(first_candle[self.low_column] - second_candle[self.low_column]) <= (first_candle[self.low_column] * 0.005):  # Allows for a small variance
            # Check if the first candle is bearish and the second candle is bullish
            if first_candle[self.close_column] < first_candle[self.open_column] and \
               second_candle[self.close_column] > second_candle[self.open_column]:
                # Check if the second candle closes above the midpoint of the first candle's body
                midpoint_first_candle = (first_candle[self.close_column] + first_candle[self.open_column]) / 2
                if second_candle[self.close_column] > midpoint_first_candle:
                    return True
        return False
