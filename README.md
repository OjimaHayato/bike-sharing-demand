Kaggle Bike Sharing Demand
==========================

## Description

Kaggle のコンペ「[Bike Sharing Demand](https://www.kaggle.com/competitions/bike-sharing-demand)」に取り組んでいる．ワシントン D.C. のシェアサイクル（Capital Bikeshare）の 2011〜2012 年の記録から，1 時間ごとの貸出台数（`count`）を予測する回帰で，評価指標は RMSLE（Root Mean Squared Logarithmic Error）．

```
.
├── notebooks/          # 1 実験 = 1 ノートブック．番号付きで増やし，前のものは書き換えない
├── src/bike_sharing/   # 複数のノートブックで使う処理（data.py: データと提出ファイル，cv.py: 交差検証の分け方，visualize.py: グラフの見た目）
├── data/               # Kaggle のデータ．ノートブックを実行すると自動でダウンロードされる
├── submissions/        # 提出ファイル．<ノートブック名>.csv で書き出す
└── .env.example        # Kaggle の API トークンを書く .env の見本
```

`data/`，`submissions/`，`.env` は git に入れていない．

### 実験の記録

| ノートブック | 内容 | CV | LB |
|---|---|---|---|
| 02_baseline | 線形回帰（hour などは数値のまま） | 1.0205 | 1.04979 |
| 02_baseline | ランダムフォレスト（sklearn の既定の設定） | 0.3460 | 0.43098 |
| 03_gbdt | 勾配ブースティング（HistGradientBoostingRegressor．既定の設定で，早期終了だけ切る） | 0.3172 | 0.40204 |

CV は交差検証での RMSLE の平均で，train を月の中の日で 4 つのブロック（1〜5，6〜10，11〜14，15〜19 日）に分けて出している（`src/bike_sharing/cv.py`）．LB は Kaggle に提出したときのスコア．どちらも小さいほどよい．

## Requirement

- Python 3.11 以上
- pandas，scikit-learn，matplotlib，kagglehub，ipykernel（バージョンは `pyproject.toml` に書いてある）
- データのダウンロードに，Kaggle のアカウントと API トークン，コンペのルールへの同意が要る（手順は Install に書いた）

## Usage

`notebooks/` のノートブックを番号順に，上から実行する．データが `data/` になければ，最初のセルで自動的にダウンロードされる．

提出ファイルは `submissions/<ノートブック名>.csv` に書き出される．コンペのページの Submit Predictions からアップロードして提出する．コンペは 2015 年に終わっているが，提出はいまも受け付けている（Late Submission，1 日 5 回まで）．

## Install

### 1. ディレクトリの準備

このリポジトリを手元に取得し，そのフォルダで以下を実行する．`data/` と `submissions/` は git に入れていないので，取得した直後は無い．どちらも手で作る必要はなく，`data/` はデータをダウンロードしたときに，`submissions/` は最初に提出ファイルを書き出したときに作られる．

### 2. 仮想環境

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/nbstripout --install   # コミット時にノートブックの出力を消す（git の設定に登録される）
```

`-e` を付けて入れているので，`src/bike_sharing/` を編集した内容は入れ直さなくても反映される．`[dev]` を付けると，コミット用の nbstripout も入る．VS Code でノートブックを開いたら，カーネルに `.venv` の Python を選ぶ．

### 3. Kaggle の準備

Kaggle API はデータのダウンロードにだけ使う．トークンが要るのも，最初にダウンロードするときだけ．

1. **API トークンを `.env` に書く**．Kaggle にログインし，Settings ページの API の欄で新しいトークンを作る．見本の `.env.example` を `.env` という名前でコピーし，`KAGGLE_API_TOKEN=` の右にトークンを貼り付けて保存する．

   ```bash
   cp .env.example .env
   ```
2. **コンペに参加する**．[コンペのルールのページ](https://www.kaggle.com/competitions/bike-sharing-demand/rules)を開き，ルールに同意する．

### 4. データのダウンロード

ノートブックの最初のセルで呼ぶ `load_data()` が，`data/train.csv` が無ければ kagglehub でダウンロードする．

ダウンロードが終わると，`data/` は次のようになる．

```
data/
├── train.csv              # 学習データ（10886 行）．2011〜2012 年の各月 1〜19 日
├── test.csv               # テストデータ（6493 行）．各月 20 日〜月末．count などの 3 列が無い
├── sampleSubmission.csv   # 提出ファイルの見本（count がすべて 0）
└── .complete/             # kagglehub がダウンロードの完了を記録するフォルダ．消さない
```

Kaggle API を使わない場合は，コンペの Data タブから手でダウンロードし，展開した 3 つの CSV を `data/` に置けば，`load_data()` はダウンロードせずにそれを読む．
