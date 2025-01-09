import re

from unstructured.cleaners.core import (
    clean,
    clean_non_ascii_chars,
    replace_unicode_quotes,
)

def unbold_text(text):
    # 粗体数字到普通数字的映射
    bold_numbers = {
        "𝟬": "0",
        "𝟭": "1",
        "𝟮": "2",
        "𝟯": "3",
        "𝟰": "4",
        "𝟱": "5",
        "𝟲": "6",
        "𝟳": "7",
        "𝟴": "8",
        "𝟵": "9",
    }

    # 转换粗体字符（字母和数字）的函数
    def convert_bold_char(match):
        char = match.group(0)
        # 转换粗体数字
        if char in bold_numbers:
            return bold_numbers[char]
        # 转换粗体大写字母
        elif "\U0001d5d4" <= char <= "\U0001d5ed":
            return chr(ord(char) - 0x1D5D4 + ord("A"))
        # 转换粗体小写字母
        elif "\U0001d5ee" <= char <= "\U0001d607":
            return chr(ord(char) - 0x1D5EE + ord("a"))
        else:
            return char  # 如果不是粗体数字或字母，则返回字符本身

    # 匹配粗体字符（数字、大写字母和小写字母）的正则表达式
    bold_pattern = re.compile(
        r"[\U0001D5D4-\U0001D5ED\U0001D5EE-\U0001D607\U0001D7CE-\U0001D7FF]"
    )
    text = bold_pattern.sub(convert_bold_char, text)

    return text

def unitalic_text(text):
    # 转换斜体字符（字母）的函数
    def convert_italic_char(match):
        char = match.group(0)
        # 斜体大写字母的Unicode范围
        if "\U0001d608" <= char <= "\U0001d621":
            return chr(ord(char) - 0x1D608 + ord("A"))
        # 斜体小写字母的Unicode范围
        elif "\U0001d622" <= char <= "\U0001d63b":
            return chr(ord(char) - 0x1D622 + ord("a"))
        else:
            return char  # 如果不是斜体字母，则返回字符本身

    # 匹配斜体字符（大写字母和小写字母）的正则表达式
    italic_pattern = re.compile(r"[\U0001D608-\U0001D621\U0001D622-\U0001D63B]")
    text = italic_pattern.sub(convert_italic_char, text)

    return text

def remove_emojis_and_symbols(text):
    # 扩展的模式，包括特定的符号，如↓（U+2193）或↳（U+21B3）
    emoji_and_symbol_pattern = re.compile(
        "["
        "\U0001f600-\U0001f64f"  # 表情符号
        "\U0001f300-\U0001f5ff"  # 符号和象形文字
        "\U0001f680-\U0001f6ff"  # 交通和地图符号
        "\U0001f1e0-\U0001f1ff"  # 国旗（iOS）
        "\U00002193"  # 向下箭头
        "\U000021b3"  # 向下箭头带右侧尖端
        "\U00002192"  # 向右箭头
        "]+",
        flags=re.UNICODE,
    )

    return emoji_and_symbol_pattern.sub(r" ", text)

def replace_urls_with_placeholder(text, placeholder="[URL]"):
    # 用于匹配URL的正则表达式模式
    url_pattern = r"https?://\S+|www\.\S+"

    return re.sub(url_pattern, placeholder, text)

def remove_non_ascii(text: str) -> str:
    text = text.encode("ascii", "ignore").decode("ascii")
    return text

def clean_text(text_content: str) -> str:
    cleaned_text = unbold_text(text_content)
    cleaned_text = unitalic_text(cleaned_text)
    cleaned_text = remove_emojis_and_symbols(cleaned_text)
    cleaned_text = clean(cleaned_text)
    cleaned_text = replace_unicode_quotes(cleaned_text)
#    cleaned_text = clean_non_ascii_chars(cleaned_text)
    cleaned_text = replace_urls_with_placeholder(cleaned_text)

    return cleaned_text
