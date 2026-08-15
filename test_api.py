import urllib.request
import json
import ssl

def main():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(
        "http://localhost:8000/api/v1/auth/login",
        data=json.dumps({"email": "test_user@example.com", "password": "password123"}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    try:
        res = urllib.request.urlopen(req, context=ctx)
        token = json.loads(res.read())["access_token"]
        print("Logged in!")
    except Exception as e:
        print("Login failed:", e)
        try:
            print(e.read().decode())
        except:
            pass
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print("\n--- Test GET /customers ---")
    req1 = urllib.request.Request("http://localhost:8000/api/v1/customers", headers=headers)
    try:
        res1 = urllib.request.urlopen(req1, context=ctx)
        print(res1.status, res1.read()[:100])
    except Exception as e:
        print("Failed:", e)
        try:
            print(e.read().decode())
        except:
            pass
            
    print("\n--- Test GET /products ---")
    req2 = urllib.request.Request("http://localhost:8000/api/v1/products", headers=headers)
    try:
        res2 = urllib.request.urlopen(req2, context=ctx)
        print(res2.status, res2.read()[:100])
    except Exception as e:
        print("Failed:", e)
        try:
            print(e.read().decode())
        except:
            pass

if __name__ == "__main__":
    main()
