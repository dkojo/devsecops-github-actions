from app import app

client = app.test_client()


def test_index():
    assert client.get("/").json["status"] == "ok"


def test_health():
    assert client.get("/health").status_code == 200


def test_list_scanners():
    assert len(client.get("/scanners").json) == 3


def test_get_scanner():
    assert client.get("/scanners/2").json["name"] == "Snyk"


def test_missing_scanner():
    assert client.get("/scanners/99").status_code == 404
