import requests
import pandas as pd
from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.core.security.password import get_password_hash
from app.models import User
from app.schemas.requests import UserUpdatePasswordRequest,CandlestickRequest
from app.schemas.responses import UserResponse
import numpy as np
from app.candlestick import candlestick
import re
from app.neurotrader.TechnicalAnalysisAutomation.head_shoulders import extract_hs_pattern_info,find_hs_patterns
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


def pascal_to_snake(name):
    # Convert from PascalCase to snake_case
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


@router.post("/test-candlestick")
async def test_trading_pattern(request: CandlestickRequest):
    try:
        print(request)
        symbol = request.symbol
        target = request.target
        pattern_type = request.pattern_type
        interval = request.interval
        limit = request.limit

        # Fetch data from Binance API
        response = requests.get('https://api.binance.com/api/v1/klines', params={
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        })
        candles_data = response.json()

        # Convert data to DataFrame
        candles_df = pd.DataFrame(candles_data, columns=['T', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
        # print(candles_df.shape,candles_df)
        candles_df['close'] = pd.to_numeric(candles_df['close'], errors='coerce')
        candles_df['T'] = pd.to_datetime(candles_df['T'], unit='ms')

        if pattern_type == 'candlestickPatterns':
            func = pascal_to_snake(target)
            if hasattr(candlestick, func):
                print(func)
                pattern_function = getattr(candlestick, func)
                print(pattern_function)
                pattern_df = pattern_function(candles_df)
            
                detected_patterns = pattern_df[pattern_df[target] == True][['T', target]]
                print(detected_patterns)
                last_20_patterns = detected_patterns.tail(20)

                return last_20_patterns.to_dict(orient='records')
            else:
                return {"error": f"No candlestick pattern detection function found for {target}"}
        elif pattern_type == 'chart':
            candles_df = candles_df.set_index('T')
            log_data = np.log(candles_df['close'].to_numpy())


            hs_patterns, ihs_patterns = find_hs_patterns(log_data, 6, early_find=False)
            if target == 'inverseHeadAndShoulders':
                ihs_info = [extract_hs_pattern_info(pat, candles_df) for pat in ihs_patterns]
                return ihs_info
            elif target == 'headAndShoulders':
                hs_info = [extract_hs_pattern_info(pat, candles_df) for pat in hs_patterns]
                return hs_info
            else:
                return {"error": "Unsupported chart pattern target type specified"}
        else:
            return {"error": "Unsupported pattern type specified"}

        

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

