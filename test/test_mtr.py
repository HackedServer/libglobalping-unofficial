from libglobalping import client

class TestMTR():
    def test_mtr(self):
        result = client().check_mtr("api.globalping.io")
        assert result
        