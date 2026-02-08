from fastapi.testclient import TestClient
from app.main import app

def run_test():
    try:
        client = TestClient(app)
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "YouTube Technical Note-Taker API is running"}
        print("Test passed!")
    except ImportError:
        print("ImportError: missing dependencies (likely httpx)")
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    run_test()
