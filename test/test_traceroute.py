from libglobalping import client

class TestTraceroute():
    def test_traceroute(self):
        result = client().check_traceroute("api.globalping.io")
        assert result
        