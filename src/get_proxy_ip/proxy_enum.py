from enum import Enum, unique


@unique
class ProxyTypeEnum(Enum):
    UNKNOWN = 0
    HTTP = 1
    HTTPS = 2
    HTTP_AND_HTTPS = 3


@unique
class AnonymityEnum(Enum):
    _type = "en"

    if _type == "en":
        UNKNOWN = "unknown"
        TRANSPARENT = "transparent"
        NORMAL_COVER = "common"
        HIGH_COVER = "high"
    if _type == "num":
        UNKNOWN = 0
        TRANSPARENT = 1
        NORMAL_COVER = 2
        HIGH_COVER = 3
    if _type == "cn":
        UNKNOWN = "未知"
        TRANSPARENT = "透明"
        NORMAL_COVER = "普匿"
        HIGH_COVER = "高匿"
