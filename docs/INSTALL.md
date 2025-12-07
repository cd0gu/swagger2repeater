# Swagger2Repeater – Installation Guide

Swagger2Repeater is a Jython-based extension for **Burp Suite**. It parses Swagger/OpenAPI JSON documents and automatically generates HTTP requests that can be sent directly to Burp’s **Repeater** tab.

---

## 1. Requirements

- Burp Suite (Community or Professional)
- Jython standalone JAR (e.g., `jython-standalone-2.7.3.jar`)
- Java 8+

---

## 2. Install and Configure Jython

1. Download a Jython standalone JAR file (example: `jython-standalone-2.7.3.jar`).
2. Save it in a permanent location, for example:
   - Windows: `C:\tools\jython\jython-standalone-2.7.3.jar`
   - Linux/macOS: `/opt/jython/jython-standalone-2.7.3.jar`

### Configure Jython in Burp Suite

1. Open **Extender → Options**.
2. Under **Python Environment**:
   - Set the path to the Jython standalone JAR.
   - Click **Apply**.

---

## 3. Install the Extension

1. Clone this repository or download `Swagger2Repeater.py`.
2. In Burp Suite, open **Extender → Extensions**.
3. Click **Add**:
   - **Extension type**: `Python`
   - **Extension file**: select `Swagger2Repeater.py`
4. A new **Swagger2Repeater** tab should appear.

---

## 4. Usage

1. Open the **Swagger2Repeater** tab.
2. Enter either:
   - A URL to a Swagger/OpenAPI JSON file  
     *(example: `https://example.com/swagger.json`)*  
   **or**
   - A local JSON file path.
3. Select the HTTP methods you want to generate.
4. (Optional) Add custom headers — one per line.

### Example Custom Headers

- Authorization: Bearer <token>
- X-API-Key: 12345

5. Click **Load Requests**.
   - Parsed endpoints and generated requests will appear.
6. Select one or multiple requests and click **Send Selected to Repeater**.
   - Requests will be pushed to Burp’s Repeater tab.

---

## 5. Known Limitations

- Only **JSON** Swagger/OpenAPI files are supported — YAML is not supported.
- Request bodies are generated using a best-effort JSON schema example builder.
- Authentication (Bearer tokens, API keys, cookies) is **not automatically extracted**.
- Deprecated operations (`deprecated: true`) are skipped.

---

## 6. Troubleshooting

| Issue | Possible Cause |
|-------|----------------|
| `Failed to load Swagger` | Invalid URL, network issue, or incorrect file path. |
| `Failed to parse JSON` | The file is not valid JSON (it might be YAML). |
| No requests appear | No HTTP methods were selected. |

For further diagnostics, refer to:
- Burp’s **Extender Output**
- The log panel inside **Swagger2Repeater**
