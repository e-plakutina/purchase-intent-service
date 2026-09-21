import pytest
from fastapi.testclient import TestClient

from purchase_intent.service.app import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def good_row():
    return {
        "Administrative": 2,
        "Administrative_Duration": 45.5,
        "Informational": 1,
        "Informational_Duration": 30.0,
        "ProductRelated": 35,
        "ProductRelated_Duration": 1200.5,
        "BounceRates": 0.02,
        "ExitRates": 0.04,
        "PageValues": 25.7,
        "SpecialDay": 0.0,
        "Month": "Nov",
        "OperatingSystems": 2,
        "Browser": 2,
        "Region": 1,
        "TrafficType": 2,
        "VisitorType": "Returning_Visitor",
        "Weekend": False,
    }
