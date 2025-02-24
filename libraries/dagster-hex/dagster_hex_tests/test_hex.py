import dagster as dg

from dagster_hex.resources import HexResource


def test_resource_request(requests_mock):
    requests_mock.get(
        "https://testurl/someendpoint",
        headers={"Content-Type": "application/json"},
        json={"data": "success"},
    )
    hex = HexResource(api_key="abc", base_url="https://testurl/")
    res = hex.make_request(method="GET", endpoint="/someendpoint")
    assert res == {"data": "success"}


def test_run_project(requests_mock):
    requests_mock.post(
        "https://testurl/api/v1/project/abc-123/run",
        headers={"Content-Type": "application/json"},
        json={"data": "mocked response"},
    )

    hex = HexResource(api_key="abc", base_url="https://testurl/")
    response = hex.run_project("abc-123", inputs={"param": "var"})
    assert response == {"data": "mocked response"}
    assert requests_mock.last_request.json() == {
        "inputParams": {"param": "var"},
        "updateCache": False,
    }


def test_run_project_no_input(requests_mock):
    requests_mock.post(
        "https://testurl/api/v1/project/abc-123/run",
        headers={"Content-Type": "application/json"},
        json={"data": "mocked response"},
    )

    hex = HexResource(api_key="abc", base_url="https://testurl/")
    response = hex.run_project("abc-123")
    assert response == {"data": "mocked response"}
    assert requests_mock.last_request.json() == {
        "updateCache": False,
    }


def test_run_project_from_asset(requests_mock):
    project_id = "hex-project-id"
    requests_mock.post(
        f"https://testurl/api/v1/project/{project_id}/run",
        headers={"Content-Type": "application/json"},
        json={"data": "mocked response"},
    )

    @dg.asset()
    def example_hex_project_asset(hex: HexResource) -> dg.MaterializeResult:
        response = hex.run_project(project_id, inputs={"param": "var"})
        return dg.MaterializeResult(metadata={"data": response.get("data")})

    res = dg.materialize(
        [example_hex_project_asset],
        resources={
            "hex": HexResource(api_key="HEX_API_KEY", base_url="https://testurl/")
        },
    )
    assert res.success

    assert requests_mock.last_request.json() == {
        "inputParams": {"param": "var"},
        "updateCache": False,
    }
