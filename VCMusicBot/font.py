# Mathematical sans-serif font mapping
_MAP = {}
_lower = "𝖺𝖻𝖼𝖽𝖾𝖿𝗀𝗁𝗂𝗃𝗄𝗅𝗆𝗇𝗈𝗉𝗊𝗋𝗌𝗍𝗎𝗏𝗐𝗑𝗒𝗓"
_upper = "𝖠𝖡𝖢𝖣𝖤𝖥𝖦𝖧𝖨𝖩𝖪𝖫𝖬𝖭𝖮𝖯𝖰𝖱𝖲𝖳𝖴𝖵𝖶𝖷𝖸𝖹"
_digit = "𝟢𝟣𝟤𝟥𝟦𝟧𝟨𝟩𝟪𝟫"

def _build():
    import re
    # iterate over actual characters (each math char may be 2 utf-16 code units but python iterates by codepoint)
    lows = list(_lower)
    ups  = list(_upper)
    nums = list(_digit)
    for i, c in enumerate("abcdefghijklmnopqrstuvwxyz"):
        _MAP[c] = lows[i]
    for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        _MAP[c] = ups[i]
    for i, c in enumerate("0123456789"):
        _MAP[c] = nums[i]
_build()

def f(text: str) -> str:
    return "".join(_MAP.get(ch, ch) for ch in str(text))
