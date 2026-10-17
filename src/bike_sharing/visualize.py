"""グラフの見た目の設定．

日本語フォントや目盛り線などを，どのノートブックでも同じ見た目にそろえる．色は指定せず，
matplotlib の既定の配色を使う．見た目は set_style() を呼んだときだけ変わり，import しただけでは
変わらない．複数のノートブックで同じグラフを描くようになったら，その関数もここに移す．

  Typical usage example:

  set_style()
  fig, ax = plt.subplots(figsize=(6, 3.5))
  train.groupby(train["datetime"].dt.hour)["count"].mean().plot(ax=ax)
  plt.show()
"""
import matplotlib.pyplot as plt
from matplotlib import font_manager

# 上から順に探して，最初に見つかった日本語フォントを使う（macOS，Windows，Linux の順）
JAPANESE_FONTS = ["Hiragino Sans", "Yu Gothic", "Meiryo", "Noto Sans CJK JP", "IPAexGothic"]


def set_style() -> None:
    """グラフ全体の見た目（日本語フォント，枠線，目盛り線など）を設定する．

    matplotlib の rcParams（グラフの既定の見た目を決める設定）を書き換えるので，ノートブックの
    最初に一度だけ呼ぶ．色は変えない．日本語フォントは JAPANESE_FONTS の順に探し，最初に
    見つかったものを使う．
    """
    available = {f.name for f in font_manager.fontManager.ttflist}
    japanese = [name for name in JAPANESE_FONTS if name in available]
    if not japanese:
        print("日本語フォントが見つからないので，日本語が豆腐（□）になるかもしれない")

    plt.rcParams.update({
        "font.family": [*japanese[:1], "sans-serif"],
        "figure.constrained_layout.use": True,
        "axes.titlesize": 12,
        "axes.titlelocation": "left",
        "axes.labelsize": 10,
        # 枠線は下だけ残し，横の目盛り線を引く
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
        "axes.grid": True,
        "axes.grid.axis": "y",
        "axes.axisbelow": True,
        "ytick.left": False,
        "legend.frameon": False,
    })
