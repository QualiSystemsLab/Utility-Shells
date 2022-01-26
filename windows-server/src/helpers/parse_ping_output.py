from textwrap import dedent
import pingparsing


def parse_ping_output(ping_output) -> pingparsing.PingStats:
    parser = pingparsing.PingParsing()
    return parser.parse(dedent(ping_output))
