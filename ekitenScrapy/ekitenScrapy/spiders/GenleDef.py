"""_summary_\n
[feature/ImprovementStoreSearch]:店舗検索時間を短縮するため、
以下に、固定値である、各小ジャンルのＵＲＬ接頭辞を辞書型で記載することにする。\n
"""
from __future__ import annotations
from typing import Final as const, Type, TypeVar


class Genre():
    """_summary_\n
    すべて辞書型。\n
    大ジャンル名 = {\n
        小ジャンル名:ＵＲＬ接頭辞,\n
        ....,\n
    }
    """
    
    RELAX_BODYCARE: const = {
        "リラク・ボディケア": {
            "整体":"/cat_seitai/",
            "":"",
        }
    }