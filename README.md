# Swagger2Repeater

Swagger2Repeater is a Burp Suite extension written in Jython that automatically converts Swagger/OpenAPI JSON documents into HTTP requests and sends them directly to Burp's Repeater tab.

It is designed for penetration testers who want to quickly generate and test API endpoints without manually crafting each request.

---

## 🚀 Features

- Parse **Swagger 2.0** and **OpenAPI 3.x** JSON documents
- Generate HTTP requests automatically
- Easily send requests to Burp Repeater
- Add custom headers (e.g., Authorization tokens)
- Supports file paths and URLs
- Skips deprecated operations
- Simple and fast interface

---

## 📦 Installation

See: `docs/INSTALL.md`

---

## 🧰 Usage Overview

1. Open the **Swagger2Repeater** tab in Burp Suite.  
2. Enter a Swagger/OpenAPI URL or file path.  
3. Select HTTP methods to generate.  
4. Optionally add custom headers.  
5. Load and review generated requests.  
6. Send selected requests to Burp Repeater.

---

## 📁 Examples

Example Swagger files are located in:

- examples/swagger2-simple.json
- examples/openapi3-simple.json

---

## ⚠ Limitations

- Only JSON Swagger/OpenAPI is supported (YAML not supported)
- Request bodies generated using best-effort placeholder data
- No automatic processing of security schemes
- Complex schemas may produce simplified payloads

---

## 🤝 Contributing

Pull requests are welcome!  
Before submitting changes:

1. Follow Jython-compatible style  
2. Ensure Burp loads the extension without errors  
3. Add/update example files when necessary  

---

## 📜 License

This project is licensed under the terms of the MIT license.
