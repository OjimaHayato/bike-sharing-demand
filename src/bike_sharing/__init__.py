"""Kaggle Bike Sharing Demand で，複数のノートブックから使うコード．

データの取得・読み込みと提出ファイルの書き出しは bike_sharing.data に，交差検証の分け方は
bike_sharing.cv に，グラフの見た目の設定は bike_sharing.visualize にまとめている．
pip install -e . でインストールして使う．

  Typical usage example:

  from bike_sharing.data import load_data
  train, test = load_data()
"""
