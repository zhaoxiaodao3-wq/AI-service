import ipaddress
import re
import socket
from urllib.parse import urlparse

INJECTION_PATTERNS = [
    r"ignore (all )?(previous|prior) instructions",
    r"ignore (the )?system prompt",
    r"forget your instructions",
    r"reveal your (system )?prompt",
    r"输出你的(系统)?提示词",
    r"忽略(之前的|所有)?(指令|系统提示)",
    r"不要遵守(规则|指令)",
    r"扮演系统",
]


SUSPICIOUS_PATTERNS = [
    r"ignore",
    r"instruction",
    r"system prompt",
    r"提示词",
    r"角色",
    r"无视",
    r"不要遵守",
    r"扮演",
]


def is_prompt_injection(text: str) -> bool:
    """检测常见 Prompt 注入特征，命中返回 True。"""
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in INJECTION_PATTERNS)


def normalize_input(text: str, max_length: int = 4000) -> str:
    """输入规范化：去控制字符、压缩空白、限制长度。"""
    text = re.sub(r"[\x00-\x1f\x7f]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_length]


def is_suspicious(text: str) -> bool:
    """弱信号：语义可能涉及指令/角色，需要模型复核。"""
    return any(
        re.search(pattern, text, re.IGNORECASE)
        for pattern in SUSPICIOUS_PATTERNS
    )


def validate_url(url: str) -> bool:
    """SSRF 防护：只允许 http/https，并拦截内网/回环/保留地址。"""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False
    host = parsed.hostname
    if not host:
        return False
    try:
        infos = socket.getaddrinfo(host, None)
    except Exception:
        return False
    for info in infos:
        raw_ip = info[4][0]
        try:
            ip = ipaddress.ip_address(raw_ip)
        except ValueError:
            continue
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
        ):
            return False
    return True
