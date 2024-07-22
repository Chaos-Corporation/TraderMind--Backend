import sys
sys.path.append('E:\\Projects\\candlestick-patterns')
from candlestick import candlestick
import pandas as pd
import requests

# Find candles where inverted hammer is detected

url = 'https://api.binance.com/api/v1/klines'
params = {
    'symbol': 'SOLUSDT',
    'interval': '1d',
    # 'limit': 1000  # Maximum number of data points
}
# candles = requests.get(url, params=params)
candles = requests.get('https://api.binance.com/api/v1/klines?symbol=BTCUSDT&interval=1d&limit=1000')
candles_dict = candles.json()

candles_df = pd.DataFrame(candles_dict,
                          columns=['T', 'open', 'high', 'low', 'close', 'V', 'CT', 'QV', 'N', 'TB', 'TQ', 'I'])

candles_df['T'] = pd.to_datetime(candles_df['T'], unit='ms')

# target = 'ThreeWhiteSoldiers'
# target = 'ThreeBlackCrows'
# target = 'BullishThreeMethodFormation'
# target = 'BearishThreeMethodFormation'
# target = 'TweezerTops'
# target = 'TweezerBottoms'

target = 'BullishHarami'



# candles_df = candlestick.inverted_hammer(candles_df, target=target)
# candles_df = candlestick.doji_star(candles_df)
# candles_df = candlestick.bearish_harami(candles_df)
candles_df = candlestick.bullish_harami(candles_df)
# candles_df = candlestick.dark_cloud_cover(candles_df)
# candles_df = candlestick.doji(candles_df)
# candles_df = candlestick.dragonfly_doji(candles_df)
# candles_df = candlestick.hanging_man(candles_df)
# candles_df = candlestick.gravestone_doji(candles_df)
# candles_df = candlestick.bearish_engulfing(candles_df)
# candles_df = candlestick.bullish_engulfing(candles_df)
# candles_df = candlestick.hammer(candles_df)
# candles_df = candlestick.morning_star(candles_df)
# candles_df = candlestick.morning_star_doji(candles_df)
# candles_df = candlestick.piercing_pattern(candles_df)
# candles_df = candlestick.rain_drop(candles_df)
# candles_df = candlestick.rain_drop_doji(candles_df)
# candles_df = candlestick.star(candles_df)
# candles_df = candlestick.shooting_star(candles_df)
# candles_df = candlestick.shooting_star(candles_df)
# candles_df = candlestick.three_white_soldiers(candles_df)
# candles_df = candlestick.three_black_crows(candles_df)
# candles_df = candlestick.bullish_three_method_formation(candles_df)
# candles_df = candlestick.bearish_three_method_formation(candles_df)
# candles_df = candlestick.tweezer_tops(candles_df)
candles_df = candlestick.tweezer_bottoms(candles_df)

print(candles_df[candles_df[target] == True][['T', target]].tail(25))
# print(candles_df)
