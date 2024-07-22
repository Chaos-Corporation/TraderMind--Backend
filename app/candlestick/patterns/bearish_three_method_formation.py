from candlestick.patterns.candlestick_finder import CandlestickFinder

class BearishThreeMethodFormation(CandlestickFinder):
    def __init__(self, target=None):
        super().__init__(self.get_class_name(), 5, target=target)  # This pattern needs at least 5 candles

    def logic(self, idx):
        if idx < 4:
            return False  # Ensure there are enough candles before this point

        first_candle = self.data.iloc[idx - 4]
        second_candle = self.data.iloc[idx - 3]
        third_candle = self.data.iloc[idx - 2]
        fourth_candle = self.data.iloc[idx - 1]
        final_candle = self.data.iloc[idx]

        # Check the first and final candles are bearish
        if first_candle[self.close_column] < first_candle[self.open_column] and \
           final_candle[self.close_column] < final_candle[self.open_column]:
            # Check the final candle closes below the first candle's close
            if final_candle[self.close_column] < first_candle[self.close_column]:
                # Check all middle candles are contained within the first candle's range
                if (second_candle[self.high_column] <= first_candle[self.high_column] and \
                    second_candle[self.low_column] >= first_candle[self.low_column]) and \
                   (third_candle[self.high_column] <= first_candle[self.high_column] and \
                    third_candle[self.low_column] >= first_candle[self.low_column]) and \
                   (fourth_candle[self.high_column] <= first_candle[self.high_column] and \
                    fourth_candle[self.low_column] >= first_candle[self.low_column]):
                    return True
        return False