"""特徴量を作る処理．

datetime から取り出す時間の特徴量，天気の前後関係（04_improve），特別な日の holiday・workingday の
補正（05_kernel_ideas）をまとめる．どれも元の DataFrame は書き換えず，列を足したり直したりしたコピーを返す．

  Typical usage example:

  train, test = load_data()
  train = add_time_features(train)
  test = add_time_features(test)
  train, test = add_weather_lags(train, test)
  train = fix_special_days(train)
  test = fix_special_days(test)
"""
import pandas as pd

# データでは祝日（holiday = 1）だが，勤務日として扱う日．
# D.C. の奴隷解放記念日で，D.C. の祝日だが連邦の祝日ではなく，通勤の山がふつうの勤務日と同じように出ている．
WORKING_HOLIDAYS = ["2011-04-15", "2012-04-16"]

# データでは勤務日か土日だが，休みとして扱う日．すべて test の日．
DAYS_OFF = [
    "2011-11-25", "2012-11-23",  # 感謝祭の翌日
    "2012-10-29", "2012-10-30",  # ハリケーン・サンディ．連邦政府が D.C. 周辺の官庁を閉めた
    "2011-12-24", "2011-12-31",  # 年末（土曜日）
    "2012-12-24",  # 大統領令で連邦政府が休み
    "2012-12-26", "2012-12-31",  # 年末
]


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """datetime から year，month，hour，dow（曜日）を取り出して足す．

    dow は月曜が 0，日曜が 6．day（日）は足さない．test の 20〜31 日は train に一度も出てこないため．

    Args:
        df: datetime 列（日時型）を持つ DataFrame．

    Returns:
        year，month，hour，dow の列を足したコピー．
    """
    df = df.copy()
    df["year"] = df["datetime"].dt.year
    df["month"] = df["datetime"].dt.month
    df["hour"] = df["datetime"].dt.hour
    df["dow"] = df["datetime"].dt.dayofweek
    return df


def add_weather_lags(train: pd.DataFrame, test: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """1 時間前の天気（weather_prev）と，雨が何時間続いているか（rain_hours）を足す．

    weather は test にもあるので，train と test をつなげて 1 時間ごとに並べてから作る
    （test の 20 日 0 時の 1 時間前は，train の 19 日 23 時になる）．データが抜けている時間があるので，
    全部の時間を並べ直してから 1 時間ずらす．1 時間前が抜けている行の weather_prev は NaN になる．
    rain_hours は weather が 3 以上の時間が何時間続いているかで，雨でない時間は 0．抜けた時間があると数え直す．

    Args:
        train: datetime 列と weather 列を持つ train の DataFrame．
        test: datetime 列と weather 列を持つ test の DataFrame．

    Returns:
        weather_prev と rain_hours の列を足した train と test のコピー．
    """
    weather = pd.concat([train, test]).set_index("datetime")["weather"].sort_index()
    hours = pd.date_range(weather.index.min(), weather.index.max(), freq="h")
    weather = weather.reindex(hours)
    weather_prev = weather.shift(1)

    rain_hours = []
    n = 0
    for w in weather:
        if w >= 3:
            n += 1
        else:
            n = 0
        rain_hours.append(n)
    rain_hours = pd.Series(rain_hours, index=hours)

    train = train.copy()
    test = test.copy()
    for df in [train, test]:
        df["weather_prev"] = df["datetime"].map(weather_prev)
        df["rain_hours"] = df["datetime"].map(rain_hours)
    return train, test


def fix_special_days(df: pd.DataFrame) -> pd.DataFrame:
    """特別な日の holiday と workingday を直す．

    WORKING_HOLIDAYS の日は holiday = 0，workingday = 1 にし，DAYS_OFF の日は holiday = 1，workingday = 0 にする．
    train では holiday = 1 の日はすべて workingday = 0 なので，休みにする日もその組み合わせにそろえる．
    train にあるのは WORKING_HOLIDAYS の 2 日だけで，DAYS_OFF はすべて test の日．

    Args:
        df: datetime，holiday，workingday 列を持つ DataFrame．

    Returns:
        holiday と workingday を直したコピー．
    """
    df = df.copy()
    date = df["datetime"].dt.strftime("%Y-%m-%d")

    working = date.isin(WORKING_HOLIDAYS)
    df.loc[working, "holiday"] = 0
    df.loc[working, "workingday"] = 1

    off = date.isin(DAYS_OFF)
    df.loc[off, "holiday"] = 1
    df.loc[off, "workingday"] = 0
    return df
