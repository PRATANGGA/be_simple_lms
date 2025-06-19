from ninja.testing import TestClient
from lms_core.api import router

client = TestClient(router)

def test_hello():
    response = client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}
