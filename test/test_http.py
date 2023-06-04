from libglobalping import client

class TestHTTP():
    def test_http(self):
        result = client().check_http("https://github.com/HackedServer/libglobalping-unofficial")
        assert result
        