from pytest import fixture
from helpers.parse_ping_output import parse_ping_output


@fixture()
def linux_ping_output():
    return """
    PING google.com (142.250.200.238) 56(84) bytes of data.
    64 bytes from mrs08s18-in-f14.1e100.net (142.250.200.238): icmp_seq=1 ttl=116 time=39.4 ms
    64 bytes from mrs08s18-in-f14.1e100.net (142.250.200.238): icmp_seq=2 ttl=116 time=39.5 ms
    64 bytes from mrs08s18-in-f14.1e100.net (142.250.200.238): icmp_seq=3 ttl=116 time=39.4 ms
    64 bytes from mrs08s18-in-f14.1e100.net (142.250.200.238): icmp_seq=4 ttl=116 time=39.3 ms
    
    --- google.com ping statistics ---
    4 packets transmitted, 4 received, 0% packet loss, time 3005ms
    rtt min/avg/max/mdev = 39.360/39.458/39.576/0.077 ms
    [root@localhost ~]#
    """


def test_ping_parser(linux_ping_output):
    result = parse_ping_output(linux_ping_output)
    assert(result.packet_loss_rate == 0.0)