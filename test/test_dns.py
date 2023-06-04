from libglobalping import client

class TestDNS():
    def test_dns(self):
        result = client().check_dns(target="api.globalping.io", query_type="NS")
        assert result
        for response in result.results:
            for answer in response.result.answers:
                assert answer.type == "NS"
        