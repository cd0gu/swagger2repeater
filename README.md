# Swagger2Repeater

Swagger2Repeater is a Burp Suite extension written in Jython that loads a **Swagger 2.0** JSON specification, generates HTTP requests for each operation, and sends them directly to Burp Repeater.

---

## Features

- Supports **Swagger 2.0 JSON**
- Load Swagger spec from URL or local file
- Generate REST requests automatically:
  - Path parameters
  - Query parameters
  - Header parameters
  - Body parameters (simple JSON example generation)
- Add custom headers
- Skip deprecated endpoints
- Send selected requests directly to Burp Repeater

---

## Installation

See detailed installation instructions in:

docs/INSTALL.md

---

## Usage

1. Open the **Swagger2Repeater** tab in Burp
2. Enter a Swagger 2.0 JSON file or URL
3. Select HTTP methods
4. (Optional) Add custom headers

### Example:

- Authorization: Bearer <token>
- X-API-Key: 12345
  
5. Load requests  
6. Send selected items to Repeater

---

## Examples

examples/swagger2-simple.json

---

## Limitations

- Only Swagger 2.0 JSON is supported  
- YAML is not supported  
- No automatic authentication extraction  
- Complex schemas may produce simplified example bodies  

---

## Contributing

Contributions are welcome.  
Please ensure:
- Python 2.7 (Jython) compatibility  
- No Burp Extender errors  
- Documentation updated if needed  

---

## License

MIT License
