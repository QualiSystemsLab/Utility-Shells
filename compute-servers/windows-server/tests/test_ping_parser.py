import json

from pytest import fixture
from helpers.parse_ping_output import parse_ping_output


@fixture()
def windows_ping_output():
    return """
    Pinging google.com [216.58.205.206] with 32 bytes of data:
    Reply from 216.58.205.206: bytes=32 time=51ms TTL=116
    Reply from 216.58.205.206: bytes=32 time=50ms TTL=116
    Reply from 216.58.205.206: bytes=32 time=252ms TTL=116
    Reply from 216.58.205.206: bytes=32 time=107ms TTL=116
    
    Ping statistics for 216.58.205.206:
        Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),
    Approximate round trip times in milli-seconds:
        Minimum = 50ms, Maximum = 252ms, Average = 115ms
    """


def test_ping_parser(windows_ping_output):
    result = parse_ping_output(windows_ping_output)
    print(json.dumps(result.as_dict(), indent=4))
    assert(result.packet_loss_rate == 0.0)