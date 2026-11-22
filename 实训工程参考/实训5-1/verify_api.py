import importlib
import sys
from pathlib import Path

from fastapi.testclient import TestClient

PROJECT_DIR = Path(__file__).resolve().parent / "项目"
sys.path.insert(0, str(PROJECT_DIR))

main_module = importlib.import_module("main")
model = importlib.import_module("app.modules.department.model")
app = main_module.app


def main() -> None:
    model.TABLE.clear()
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200, response.text
        assert response.json() == {"status": "healthy"}
        print(f"PASS GET /health -> {response.status_code} {response.json()}")

        response = client.get("/departments")
        assert response.status_code == 200, response.text
        payload = response.json()
        assert set(payload) == {"items", "total"}
        assert payload == {"items": [], "total": 0}
        print(f"PASS GET /departments -> {response.status_code} {payload}")

        response = client.post(
            "/departments",
            json={"dept_code": "D51", "full_name": "五一中队", "address": "实训楼"},
        )
        assert response.status_code == 201, response.text
        assert response.json()["dept_code"] == "D51"
        print(f"PASS POST /departments -> {response.status_code} {response.json()}")

        response = client.delete("/departments/D51")
        assert response.status_code == 204, response.text
        assert response.content == b""
        print(f"PASS DELETE /departments/D51 -> {response.status_code} empty body")

    print("PASS: 4/4 smoke checks")


if __name__ == "__main__":
    main()
