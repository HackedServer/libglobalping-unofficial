from libglobalping import client

class TestPing():
    def test_ping(self):
        result = client().check_ping4("1.1.1.1")
        assert result
        