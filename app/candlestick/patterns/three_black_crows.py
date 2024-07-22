from candlestick.patterns.candlestick_finder import CandlestickFinder

class ThreeBlackCrows(CandlestickFinder):
    def __init__(self, target=None):
        super().__init__(self.get_class_name(), 3, target=target)  # We need 3 candles to identify the pattern

    def logic(self, idx):
        first_candle = self.data.iloc[idx - 2]
        second_candle = self.data.iloc[idx - 1]
        third_candle = self.data.iloc[idx]

        # Check all three candles are bearish
        if first_candle[self.close_column] < first_candle[self.open_column] and \
           second_candle[self.close_column] < second_candle[self.open_column] and \
           third_candle[self.close_column] < third_candle[self.open_column]:
            # Check each candle opens within the body of the previous candle
            if second_candle[self.open_column] < first_candle[self.open_column] and \
               third_candle[self.open_column] < second_candle[self.open_column]:
                # Check each candle closes lower than the previous candle
                if second_candle[self.close_column] < first_candle[self.close_column] and \
                   third_candle[self.close_column] < second_candle[self.close_column]:
                    return True
        return False
