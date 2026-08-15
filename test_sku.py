import urllib.request
import json
import ssl

def main():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # Login
    req = urllib.request.Request(
        "http://localhost:8000/api/v1/auth/login",
        data=json.dumps({"email": "admin@stockpilot.com", "password": "password123"}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    
    try:
        res = urllib.request.urlopen(req, context=ctx)
        token = json.loads(res.read())["access_token"]
        print("Logged in!")
    except Exception as e:
        print("Login failed:", e)
        # try owner
        req = urllib.request.Request(
            "http://localhost:8000/api/v1/auth/login",
            data=json.dumps({"email": "owner@stockpilot.com", "password": "password123"}).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        try:
            res = urllib.request.urlopen(req, context=ctx)
            token = json.loads(res.read())["access_token"]
            print("Logged in as owner!")
        except Exception as e2:
            print("Login owner failed:", e2)
            try:
                print(e2.read())
            except:
                pass
            return

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print("\n--- Test 1 (sku='') ---")
    req1 = urllib.request.Request(
        "http://localhost:8000/api/v1/products",
        data=json.dumps({"name": "Test Product", "sku": "", "price": 10.99}).encode("utf-8"),
        headers=headers
    )
    try:
        res1 = urllib.request.urlopen(req1, context=ctx)
        print(res1.status, res1.read())
    except Exception as e:
        print("Failed:", e)
        try:
            print(e.read().decode())
        except:
            pass

    print("\n--- Test 2 (sku omitted) ---")
    req2 = urllib.request.Request(
        "http://localhost:8000/api/v1/products",
        data=json.dumps({"name": "Test Product 2", "price": 10.99}).encode("utf-8"),
        headers=headers
    )
    try:
        res2 = urllib.request.urlopen(req2, context=ctx)
        print(res2.status, res2.read())
    except Exception as e:
        print("Failed:", e)
        try:
            print(e.read().decode())
        except:
            pass

if __name__ == "__main__":
    main()
