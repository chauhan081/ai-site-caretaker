from src.checks import check_server



def test_check_server_localhost_closed_or_open_shape() -> None:
    result = check_server("127.0.0.1", port=65534)
    assert result.name == "check-server"
    assert isinstance(result.ok, bool)
    assert "host" in result.details
    assert result.details["port"] == 65534
