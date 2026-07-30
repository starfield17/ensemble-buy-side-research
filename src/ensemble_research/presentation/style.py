from __future__ import annotations

from matplotlib import font_manager, rcParams

CJK_CANDIDATES = [
    "Noto Sans CJK SC", "Noto Sans CJK JP", "Source Han Sans SC", "Microsoft YaHei",
    "PingFang SC", "Hiragino Sans GB", "SimHei", "Arial Unicode MS",
]


def configure_fonts() -> str | None:
    installed = {font.name for font in font_manager.fontManager.ttflist}
    for candidate in CJK_CANDIDATES:
        if candidate in installed:
            rcParams["font.sans-serif"] = [candidate, "DejaVu Sans"]
            rcParams["axes.unicode_minus"] = False
            return candidate
    rcParams["axes.unicode_minus"] = False
    return None
