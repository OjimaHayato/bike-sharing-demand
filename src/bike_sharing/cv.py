"""交差検証の分け方．

test は各月の 20 日〜月末で，train（各月の 1〜19 日）とは日がまとまって分かれている．
そこで train も月の中の日でブロックに分け，1〜5 日，6〜10 日，11〜14 日，15〜19 日の
4 つの fold にする．同じ日の時間が学習側と検証側の両方に入らないようにするためと，
検証する日の「日」の値が学習側に出てこないようにして，test と同じ条件にするため．
どの fold でも，学習側には 24 か月すべてのデータが入る．

  Typical usage example:

  from sklearn.model_selection import PredefinedSplit, cross_val_score

  cv = PredefinedSplit(get_folds(train))
  scores = cross_val_score(model, X, y, cv=cv, scoring="neg_root_mean_squared_error")
"""
import pandas as pd

N_FOLDS = 4


def get_folds(df: pd.DataFrame) -> pd.Series:
    """各行が何番目の fold で検証に使われるかを返す．

    月の中の日で分ける．1〜5 日が 0，6〜10 日が 1，11〜14 日が 2，15〜19 日が 3．

    Args:
        df: datetime 列（日時型）を持つ DataFrame．train を渡す．

    Returns:
        fold の番号（0〜3）の Series．形は (len(df),) で，index は df と同じ．

    Raises:
        ValueError: 日が 20 日以降の行があるとき（test を渡したときなど）．
    """
    day = df["datetime"].dt.day
    if (day >= 20).any():
        raise ValueError("20 日以降の行がある．get_folds には train を渡す")

    folds = pd.Series(0, index=df.index)
    folds[day >= 6] = 1
    folds[day >= 11] = 2
    folds[day >= 15] = 3
    return folds
