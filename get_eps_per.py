# 銘柄選定のためのEPSとPERの計算コード(ChatGPT)
#basis="fy"：直近の通期当期純利益を使用
#basis="ttm"：直近4四半期の当期純利益合計を使用（PERの実務に近い）
#発行済株式数は Ticker.info["sharesOutstanding"] を使用するため、増資・自己株式・併合などがある銘柄では「平均株式数」とのズレが出る場合があります。
#厳密には決算短信の平均株式数で割るのが理想ですが、APIからの取得は難しいので概算としています。
#行名は英語で返るため、日本語の「当期純利益」は上記の候補（Net Income Common Stockholders 等）にマッピングしています。
#yfinanceのデータは遅延や欠損があり得ます。None が返る場合は、quarterly_financials/financialsの中身を一度 print() で確認してください。
# pip install yfinance pandas
import yfinance as yf
import pandas as pd
from typing import Optional, Dict

# ---------------------------
# 設定：行名のゆらぎ対策（Yahooの英語科目名を中心に候補を用意）
# ---------------------------
NET_INCOME_CANDIDATES = [
    "Net Income Common Stockholders",  # 最優先（親会社株主に帰属する当期純利益）
    "Net Income",                      # 次善
    "Net Income Including Noncontrolling Interests",
]
DILUTED_EPS_CANDIDATES = [
    "Diluted EPS", "Basic EPS"
]
SHARES_CANDIDATES_INFO = ["sharesOutstanding"]  # yfinance Ticker.infoのキー
PRICE_FIELDS = ["last_price", "lastPrice", "regularMarketPrice"]  # 価格取得の候補

def _find_row_value(df: pd.DataFrame, candidates: list) -> Optional[pd.Series]:
    """行名候補から最初に見つかった行（Series）を返す。なければNone。"""
    if df is None or df.empty:
        return None
    lower_index = {str(idx).strip().lower(): idx for idx in df.index}
    for key in candidates:
        k = key.strip().lower()
        if k in lower_index:
            return df.loc[lower_index[k]]
    # 部分一致のフォールバック
    for k in candidates:
        k = k.strip().lower()
        for low, orig in lower_index.items():
            if k in low:
                return df.loc[orig]
    return None

def _get_market_price(t: yf.Ticker) -> Optional[float]:
    """現在値を取得（fast_info優先、なければinfo）。"""
    # fast_info
    try:
        p = getattr(t, "fast_info", None)
        if p:
            # yfinance>=0.2系
            if hasattr(p, "last_price") and p.last_price:
                return float(p.last_price)
            if hasattr(p, "lastPrice") and p.lastPrice:
                return float(p.lastPrice)
    except Exception:
        pass
    # info
    try:
        info = t.info or {}
        for f in PRICE_FIELDS:
            v = info.get(f)
            if v:
                return float(v)
    except Exception:
        pass
    return None

def _get_shares_outstanding(t: yf.Ticker) -> Optional[int]:
    """発行済株式数（概算）を取得。"""
    try:
        info = t.info or {}
        for k in SHARES_CANDIDATES_INFO:
            v = info.get(k)
            if v:
                return int(v)
    except Exception:
        pass
    # fast_info にある場合
    try:
        p = getattr(t, "fast_info", None)
        if p and hasattr(p, "shares"):
            v = p.shares
            if v:
                return int(v)
    except Exception:
        pass
    return None

def get_net_income_latest_fy(ticker: str) -> Optional[float]:
    """
    直近の通期（年次）当期純利益を取得（単位：通貨単位そのまま）。
    Yahooの年次損益計算書からNet Income行を拾う。
    """
    t = yf.Ticker(ticker)
    fin = t.financials  # 年次 IS: 列が年度（datetime）
    row = _find_row_value(fin, NET_INCOME_CANDIDATES)
    if row is None:
        return None
    # 直近列（最新年度）をとる
    try:
        row = row.sort_index()  # 年度の昇順
        return float(row.iloc[-1])
    except Exception:
        return None

def get_net_income_ttm(ticker: str) -> Optional[float]:
    """
    直近4四半期（TTM）の当期純利益合計を取得（単位：通貨）。
    Yahooの四半期損益計算書からNet Income行を拾って合算。
    """
    t = yf.Ticker(ticker)
    qfin = t.quarterly_financials  # 四半期IS: 列が四半期（datetime）
    row = _find_row_value(qfin, NET_INCOME_CANDIDATES)
    if row is None:
        return None
    try:
        # 直近4期を合算（足りなければある分だけ）
        row = row.sort_index()  # 期の昇順
        last4 = row.iloc[-4:] if len(row) >= 4 else row
        return float(last4.sum())
    except Exception:
        return None

def get_eps_and_per(
    ticker: str,
    basis: str = "ttm",  # "ttm" or "fy"
) -> Dict[str, Optional[float]]:
    """
    EPSとPERを計算。
    basis="ttm": 直近4四半期合算の当期純利益を使用
    basis="fy" : 直近の通期（年次）当期純利益を使用
    EPS ≈ Net Income / Shares Outstanding（概算）
    PER = Price / EPS
    """
    t = yf.Ticker(ticker)

    # 当期純利益
    if basis == "fy":
        net_income = get_net_income_latest_fy(ticker)
    else:
        net_income = get_net_income_ttm(ticker)

    # EPS（ダイレクト行が取れればそちらを優先：参考）
    eps_direct = None
    try:
        src = t.financials if basis == "fy" else t.quarterly_financials
        row_eps = _find_row_value(src, DILUTED_EPS_CANDIDATES)
        if row_eps is not None:
            row_eps = row_eps.sort_index()
            if basis == "fy":
                eps_direct = float(row_eps.iloc[-1])
            else:
                # 四半期EPSを合算（TTM擬似）
                eps_direct = float(row_eps.iloc[-4:].sum()) if len(row_eps) >= 4 else float(row_eps.sum())
    except Exception:
        pass

    shares = _get_shares_outstanding(t)
    price = _get_market_price(t)

    # 概算EPS（当期純利益 ÷ 発行済株式数）
    eps_from_net = None
    if net_income is not None and shares:
        eps_from_net = float(net_income) / float(shares)

    # 最終EPSは、直接行が妥当ならそれ、なければ概算
    eps = eps_direct if (eps_direct is not None and eps_direct > 0) else eps_from_net

    per = None
    if eps and eps != 0 and price:
        per = float(price) / float(eps)

    return {
        "ticker": ticker,
        "basis": basis,
        "net_income": net_income,  # 当期純利益
        "shares_outstanding": shares,
        "price": price,
        "eps": eps,
        "per": per,
        "eps_from_net_income": eps_from_net,  # 参考（概算）
        "eps_direct_row": eps_direct,         # 参考（財務表のEPS）
    }

# ---------------------------
# 使い方例（トヨタ 7203.T、ソフトバンクG 9984.T）
# ---------------------------
if __name__ == "__main__":
    for tk in ["7203.T", "9984.T"]:
        print("=== ", tk, " ===")
        print("FY basis:", get_eps_and_per(tk, basis="fy"))
        print("TTM basis:", get_eps_and_per(tk, basis="ttm"))
