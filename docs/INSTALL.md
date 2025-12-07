# Swagger2Repeater – Installation Guide

Swagger2Repeater is a Jython-based extension for **Burp Suite**. It loads a Swagger JSON specification, generates HTTP requests, and sends them directly to Burp Repeater.

---

## 1. Requirements

- Burp Suite (Community or Professional)
- Jython standalone JAR (e.g., `jython-standalone-2.7.3.jar`)
- Java 8+

---

## 2. Install and Configure Jython

### Step 1 — Download Jython

Download a standalone Jython JAR such as:

jython-standalone-2.7.3.jar

Place it somewhere permanent, such as:

- Windows: `C:\tools\jython\jython-standalone-2.7.3.jar`
- Linux/macOS: `/opt/jython/jython-standalone-2.7.3.jar`

---

### Step 2 — Configure in Burp Suite

1. Open **Extender → Options**
2. Under **Python Environment**:
   - Set the path to the Jython standalone JAR
3. Click **Apply**

---

## 3. Install the Extension

1. Clone this repository or download `Swagger2Repeater.py`
2. In Burp Suite, open **Extender → Extensions**
3. Click **Add**:
   - **Extension type**: `Python`
   - **Extension file**: select `Swagger2Repeater.py`
4. A new **Swagger2Repeater** tab should appear

---

## 4. Usage

1. Open the **Swagger2Repeater** tab
2. Enter a Swagger 2.0 JSON source:
   - A URL (example: `https://example.com/swagger.json`)
   - Or a local JSON file path
3. Select the HTTP methods you want to generate
4. (Optional) Add custom headers — one per line

### Example custom headers

- Authorization: Bearer <token>
- X-API-Key: 12345
  
5. Click **Load Requests**
6. Select requests and click **Send Selected to Repeater**

---

## 5. Known Limitations

- Only **Swagger 2.0 (OpenAPI 2.0)** JSON is supported  
- YAML is **not** supported  
- Bodies are generated using best-effort example values  
- Authentication is not read from the spec  
- Deprecated operations (`deprecated: true`) are skipped  

---

## 6. Troubleshooting

| Issue | Cause |
|------|--------|
| `Failed to load Swagger` | Invalid URL, network issue, or incorrect file path |
| `Failed to parse JSON` | File is not valid Swagger JSON |
| No requests generated | No HTTP methods selected |

Check Burp’s **Extender Output** for error messages.
