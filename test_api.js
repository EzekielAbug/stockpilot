async function test() {
  try {
    let res = await fetch('http://localhost:8000/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: 'admin@stockpilot.dev',
        password: 'password123'
      })
    });
    let data = await res.json();
    if (!res.ok) {
        res = await fetch('http://localhost:8000/api/v1/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: 'test_user@example.com',
            password: 'password123'
          })
        });
        data = await res.json();
    }
    const token = data.access_token;
    console.log("Token acquired", token ? "Yes" : "No");
    
    // test post (sku omitted)
    let postRes = await fetch('http://localhost:8000/api/v1/products', {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}` 
      },
      body: JSON.stringify({
        name: 'Test',
        price: 10,
        image_url: null
      })
    });
    let postData = await postRes.json();
    console.log("STATUS (omitted):", postRes.status);
    console.log("DATA (omitted):", JSON.stringify(postData, null, 2));

    console.log("--- TEST WITH SKU AS EMPTY STRING ---");
    let postRes2 = await fetch('http://localhost:8000/api/v1/products', {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}` 
      },
      body: JSON.stringify({
        name: 'Test2',
        sku: "",
        price: 10,
        image_url: null
      })
    });
    let postData2 = await postRes2.json();
    console.log("STATUS (empty string):", postRes2.status);
    console.log("DATA (empty string):", JSON.stringify(postData2, null, 2));
    
  } catch (err) {
    console.log("ERROR:", err.message);
  }
}
test();
