"""データの取得・読み込みと，提出ファイルの書き出し．

パスはすべてプロジェクトのルートを基準にした絶対パスで持つので，ノートブックをどこから
実行しても同じ場所を読み書きする．データが手元になければ Kaggle API でダウンロードする．
ダウンロードには Kaggle の API トークン（プロジェクト直下の .env か ~/.kaggle/access_token）と，
コンペのルールへの同意が必要．

  Typical usage example:

  train, test = load_data()
  submission = pd.DataFrame({"datetime": test["datetime"], "count": predictions})
  save_submission(submission, "01_baseline")
"""
import os
from pathlib import Path

import kagglehub
import pandas as pd

# このファイル（src/bike_sharing/data.py）から 2 つ上がプロジェクトのルート．
# ノートブックをどこから実行しても同じ場所を指すように，ルートを基準にした絶対パスで持つ
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
SUBMISSIONS_DIR = PROJECT_ROOT / "submissions"
# Kaggle の API トークンを書くファイル（.env.example をコピーして作る．git には入れない）
ENV_FILE = PROJECT_ROOT / ".env"

COMPETITION = "bike-sharing-demand"

# 提出ファイルの datetime の書式．test.csv と sampleSubmission.csv はこの書式で書かれている
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def _load_env_file(path: Path) -> None:
    """KEY=値 の形で書かれたファイルを読み，まだ設定されていない環境変数に入れる．

    空行と # で始まる行は飛ばす．値が空の行も飛ばすので，.env.example をコピーしただけで
    トークンを貼っていないときは，何も設定しない．すでに設定されている環境変数は上書きしない．

    Args:
        path: 読むファイルのパス．無ければ何もしない．
    """
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = (part.strip() for part in line.split("=", 1))
        value = value.strip("\"'")
        if value:
            os.environ.setdefault(key, value)


def download_data() -> None:
    """コンペのデータを data/ にダウンロードする．

    data/train.csv がすでにあれば何もしない．API トークンは，.env の KAGGLE_API_TOKEN があれば
    それを，無ければ ~/.kaggle/access_token を使う（kagglehub は環境変数を先に見る）．

    Raises:
        kagglehub.exceptions.UnauthenticatedError: Kaggle の API トークンが見つからないとき．
    """
    # kagglehub 1.0.2 はダウンロード済みの output_dir を指定するとエラーになるので，
    # train.csv があるときは呼ばない
    if (DATA_DIR / "train.csv").exists():
        return
    _load_env_file(ENV_FILE)
    kagglehub.competition_download(COMPETITION, output_dir=str(DATA_DIR))


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """train.csv と test.csv を読み込む．

    手元になければ，先に download_data() でダウンロードする．datetime 列は日時型にして返す．

    Returns:
        (train, test) のタプル．train は形が (10886, 12) で目的変数 count と，その内訳の
        casual・registered を含む．test は形が (6493, 9) で，この 3 列を含まない．
    """
    download_data()
    return (
        pd.read_csv(DATA_DIR / "train.csv", parse_dates=["datetime"]),
        pd.read_csv(DATA_DIR / "test.csv", parse_dates=["datetime"]),
    )


def save_submission(submission: pd.DataFrame, name: str) -> Path:
    """提出ファイルの形式を確かめて，submissions/<name>.csv に書き出す．

    Args:
        submission: datetime と count の 2 列からなる DataFrame．datetime は test.csv の
            日時と過不足なく一致させる（行の順番は問わない）．count は 0 以上の数値．
        name: 拡張子を除いたファイル名．ノートブックと同じ名前（例: "01_baseline"）にする．

    Returns:
        書き出したファイルのパス．

    Raises:
        ValueError: 列・datetime・count が，提出ファイルの条件を満たさないとき．
    """
    if list(submission.columns) != ["datetime", "count"]:
        raise ValueError(f"列は datetime と count の 2 つだけにする: {list(submission.columns)}")

    # 日時型でも文字列でも受け取れるように，test.csv と同じ書式の文字列にそろえてから比べる
    written = pd.to_datetime(submission["datetime"]).dt.strftime(DATETIME_FORMAT)
    expected = pd.read_csv(DATA_DIR / "test.csv", usecols=["datetime"])["datetime"]
    if sorted(written) != sorted(expected):
        raise ValueError("datetime が test.csv と一致しない（抜け・重複・余分な日時がある）")

    count = submission["count"]
    if not pd.api.types.is_numeric_dtype(count) or count.isna().any():
        raise ValueError("count は欠損のない数値にする")

    if (count < 0).any():
        raise ValueError(f"count は 0 以上にする（負の値が {(count < 0).sum()} 件ある）")

    SUBMISSIONS_DIR.mkdir(exist_ok=True)
    path = SUBMISSIONS_DIR / f"{name}.csv"
    # index=False を付けないと，行番号の列が余分に書き出されて提出エラーになる
    submission.assign(datetime=written).to_csv(path, index=False)
    return path
