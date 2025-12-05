# Swagger2Repeater

Swagger2Repeater is a Jython-based Burp Suite extension that loads a Swagger/OpenAPI JSON specification, generates HTTP requests for each operation, and sends them directly to Burp's Repeater.

## Features

- Load Swagger 2.0 or OpenAPI 3.x JSON from:
  - A URL (e.g., `https://api.example.com/swagger.json`)
  - A local file path
- Parse basic API metadata:
  - Host, scheme (http/https), base path / servers
- Generate HTTP requests for each path + method:
  - Fills path parameters (e.g., `/users/{id}` → `/users/1`)
  - Generates simple query/header/cookie parameters
  - Builds JSON request bodies from request schemas (best-effort)
- UI options:
  - Select HTTP methods to include (GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS)
  - Add one or more custom headers (e.g., `Authorization: Bearer <token>`)
- Sends selected requests directly to Burp Repeater
- Ensures proper CRLF separation between headers and body

## Files

- `Swagger2Repeater.py` — Burp extension (Jython). Load this file as a Python extension in Burp.
- `examples/` — small example Swagger JSON for quick testing.
- `docs/INSTALL.md` — installation instructions for Burp Suite + Jython.

## Installation (local)

1. Download a Jython standalone JAR (e.g., `jython-standalone-2.7.3.jar`) and note its path.
2. Clone this repository or copy `Swagger2Repeater.py` somewhere local.
3. Open **Burp Suite** → **Extender** → **Options** → **Python Environment** → point to the Jython standalone JAR.
4. Go to **Extender** → **Extensions** → **Add**:
   - **Extension type**: `Python`
   - **Extension file**: `Swagger2Repeater.py`
5. A new tab named **Swagger2Repeater** should appear in Burp.

For more details, see `docs/INSTALL.md`.

## Usage

1. Open the **Swagger2Repeater** tab in Burp.
2. Click in **Swagger Source (file path or URL)** and provide either:
   - A URL to a Swagger/OpenAPI JSON file, or
   - A full path to a local JSON file.
3. Select which HTTP methods you want to generate requests for.
4. (Optional) Enter one or more custom headers, for example:

   ```text
   Authorization: Bearer <token>
   X-API-Key: 12345
