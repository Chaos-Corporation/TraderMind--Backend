import requests
import pandas as pd
from fastapi import APIRouter, Depends, status, HTTPException, Query
from tradingpatterns import tradingpatterns
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.core.security.password import get_password_hash
from app.models import User
from app.schemas.requests import UserUpdatePasswordRequest
from app.schemas.responses import UserResponse
import numpy as np
from app.candlestick import candlestick
import re

router = APIRouter()


@router.get("/me", response_model=UserResponse, description="Get current user")
async def read_current_user(
    current_user: User = Depends(deps.get_current_user),
) -> User:
    return current_user


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete current user",
)
async def delete_current_user(
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> None:
    await session.execute(delete(User).where(User.user_id == current_user.user_id))
    await session.commit()


@router.post(
    "/reset-password",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Update current user password",
)
async def reset_current_user_password(
    user_update_password: UserUpdatePasswordRequest,
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
) -> None:
    current_user.hashed_password = get_password_hash(user_update_password.password)
    session.add(current_user)
    await session.commit()

def detect_head_shoulder(df, window=3):
    # Define the rolling window
    roll_window = window
    
    # Create a copy of the DataFrame to avoid SettingWithCopyWarning
    df = df.copy()
    
    # Handle None values and ensure numeric data types
    df['high'] = pd.to_numeric(df['high'], errors='coerce')
    df['low'] = pd.to_numeric(df['low'], errors='coerce')
    
    # Replace None values with a default (0 or np.nan)
    df['high'].fillna(0, inplace=True)
    df['low'].fillna(0, inplace=True)
    
    # Create a rolling window for High and Low
    df.loc[:, 'high_roll_max'] = df['high'].rolling(window=roll_window).max()
    df.loc[:, 'low_roll_min'] = df['low'].rolling(window=roll_window).min()
    
    # Create a boolean mask for Head and Shoulder pattern
    mask_head_shoulder = (
        (df['high_roll_max'].notna()) &  # Check for NaN values after rolling calculation
        (df['low_roll_min'].notna()) &   # Check for NaN values after rolling calculation
        (df['high_roll_max'] > df['high'].shift(1)) &
        (df['high_roll_max'] > df['high'].shift(-1)) &
        (df['high'] < df['high'].shift(1)) &
        (df['high'] < df['high'].shift(-1))
    )
    
    # Create a boolean mask for Inverse Head and Shoulder pattern
    mask_inv_head_shoulder = (
        (df['low_roll_min'].notna()) &   # Check for NaN values after rolling calculation
        (df['low_roll_min'] < df['low'].shift(1)) &
        (df['low_roll_min'] < df['low'].shift(-1)) &
        (df['low'] > df['low'].shift(1)) &
        (df['low'] > df['low'].shift(-1))
    )
    
    # Create a new column for Head and Shoulder and its inverse pattern and populate it using the boolean masks
    df['head_shoulder_pattern'] = np.nan
    df.loc[mask_head_shoulder, 'head_shoulder_pattern'] = 'Head and Shoulder'
    df.loc[mask_inv_head_shoulder, 'head_shoulder_pattern'] = 'Inverse Head and Shoulder'
    
    # Drop temporary columns used for calculations
    df.drop(['high_roll_max', 'low_roll_min'], axis=1, inplace=True)
    
    return df

@router.post("/test", response_model=list[dict])
async def test_trading_pattern():
    try:
        # Fetch data from Binance API
        candles = requests.get('https://api.binance.com/api/v1/klines?symbol=BTCUSDT&interval=1d&limit=1000')
        candles_dict = candles.json()

          # Convert data to DataFrame
        candles_df = pd.DataFrame(candles_dict, columns=['T', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])

        # Convert timestamp to datetime
        candles_df['T'] = pd.to_datetime(candles_df['T'], unit='ms')

        # Select necessary columns for pattern detection
        stock_data = candles_df[['T', 'high', 'low']]
        print(stock_data)

        # Apply pattern indicator screener
        stock_data = detect_head_shoulder(stock_data)

        # Convert DataFrame to list of dictionaries for JSON response
        pattern_list = stock_data.to_dict(orient='records')

        return pattern_list

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


def pascal_to_snake(name):
    # Convert from PascalCase to snake_case
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


@router.post("/test-candlestick")
async def test_trading_pattern(
    symbol: str = Query("BTCUSDT", description="Trading pair symbol"),
    interval: str = Query("1d", description="Candlestick interval"),
    limit: int = Query(1000, description="Number of candlesticks to return"),
    target: str = Query("BullishHarami", description="Candlestick pattern to detect")
):
    try:
        # Fetch data from Binance API
        response = requests.get('https://api.binance.com/api/v1/klines', params={
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        })
        candles_data = response.json()

        # Convert data to DataFrame
        candles_df = pd.DataFrame(candles_data, columns=['T', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
        
        # Convert timestamp to datetime
        candles_df['T'] = pd.to_datetime(candles_df['T'], unit='ms')

        func = pascal_to_snake(target)

        # Applying the candlestick pattern detection from the candlestick module
        if hasattr(candlestick, func):
            pattern_function = getattr(candlestick, func)
            pattern_df = pattern_function(candles_df)
            detected_patterns = pattern_df[pattern_df[target] == True][['T', target]]
        else:
            return {"error": f"No pattern detection function found for {target}"}

        # Convert DataFrame to list of dictionaries for JSON response
        return detected_patterns.to_dict(orient='records')

    except Exception as e:
        # In case of an error, raise an HTTPException with status code 500
        raise HTTPException(status_code=500, detail=str(e))

