from src.enum.common import ProxyTypeEnum, AnonymityEnum


class ProxyEntity():
    """
    ip代理对象
    :param url url地址
    :param ip ip地址
    :param port 端口
    :param protocol 协议
    :param source 代理源头网站名
    :param proxy_type 代理类型 {@link ProxyType}
    :param anonymity 代理隐蔽性 {@link CoverOfProxy}
    :param check_count 有效性检验的次数
    :param last_check_time 最后进行有效性检验的时间
    :param reliability 代理可靠性, 默认为5
    """

    def __init__(
            self,
            url: str,
            ip: str,
            port: str,
            protocol: str = "http",
            source: str = "unknown",  # 来源
            supplier: str = "",  # 运营商
            proxy_type: int = ProxyTypeEnum.UNKNOWN.value,
            anonymity: int = AnonymityEnum.UNKNOWN.value,
            check_count: int = 0,
            country: str = "中国",  # 国家
            region: str = "",  # 地区
            city: str = "",  # 城市
            last_check_time=None,  # 上次检查时间
            reliability: str = "",  # 可用性
            response_speed: str = "",  # 响应速度
            transfer_speed: str = "",  # 传输速度
    ):
        self.url = url
        self.ip = ip
        self.port = port
        self.protocol = protocol
        self.source = source
        self.supplier = supplier
        self.proxy_type = proxy_type
        self.anonymity = anonymity
        self.check_count = check_count
        self.Country = country
        self.region = region
        self.city = city
        self.last_check_time = last_check_time
        self.reliability = reliability
        self.response_speed = response_speed
        self.transfer_speed = transfer_speed
