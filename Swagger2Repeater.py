# -*- coding: utf-8 -*-
#
# Swagger2Repeater
#
# A Burp Suite extension that generates HTTP requests from a Swagger/OpenAPI
# specification and sends them to Burp Repeater.
#
# Features:
#   - Swagger 2.0 & OpenAPI 3.x support (basic)
#   - Load Swagger from URL or local file
#   - Parse host / scheme / basePath / servers
#   - Build path/query/header/cookie parameters
#   - Generate simple JSON request bodies from schemas
#   - Custom Header input in the UI
#   - CRLF fix ensuring proper request formatting for Repeater
#
# Requires:
#   - Burp Suite
#   - Jython (for Python extensions)


from burp import IBurpExtender, ITab
from java.net import URL, HttpURLConnection
from java.io import FileInputStream, InputStreamReader, BufferedReader
from java.awt import BorderLayout, GridBagLayout, GridBagConstraints, Insets
from java.awt.event import ActionListener
from javax.swing import (
    JPanel, JLabel, JTextField, JButton, JCheckBox,
    JScrollPane, JTextArea, JList, DefaultListModel, ListSelectionModel,
    JFileChooser
)

import json
import re


MAX_SCHEMA_DEPTH = 3


class BurpExtender(IBurpExtender, ITab, ActionListener):

    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        self._stdout = callbacks.getStdout()

        callbacks.setExtensionName("Swagger2Repeater")

        self._requests = []
        self.swagger = None
        self.is_oas3 = False

        self._init_ui()
        callbacks.addSuiteTab(self)

        self._println("[+] Swagger2Repeater loaded.")

    # -------------------------------------------------------------------
    # UI
    # -------------------------------------------------------------------

    def _init_ui(self):
        self.mainPanel = JPanel(BorderLayout())

        topPanel = JPanel()
        topPanel.setLayout(GridBagLayout())
        gbc = GridBagConstraints()
        gbc.insets = Insets(2, 2, 2, 2)
        gbc.fill = GridBagConstraints.HORIZONTAL
        row = 0

        # Swagger Source
        gbc.gridx = 0
        gbc.gridy = row
        topPanel.add(JLabel("Swagger Source (file path or URL):"), gbc)

        gbc.gridx = 1
        self.swaggerField = JTextField("https://api.example.com/swagger.json", 40)
        pathPanel = JPanel()
        pathPanel.add(self.swaggerField)

        self.browseButton = JButton("Browse...")
        self.browseButton.addActionListener(self)
        pathPanel.add(self.browseButton)

        topPanel.add(pathPanel, gbc)

        row += 1

        # Methods
        gbc.gridx = 0
        gbc.gridy = row
        topPanel.add(JLabel("HTTP Methods:"), gbc)

        gbc.gridx = 1
        methodsPanel = JPanel()
        self.methodCheckboxes = {}
        for m in ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]:
            cb = JCheckBox(m, m in ["GET", "POST"])
            self.methodCheckboxes[m] = cb
            methodsPanel.add(cb)
        topPanel.add(methodsPanel, gbc)

        row += 1

        # Custom Header
        gbc.gridx = 0
        gbc.gridy = row
        topPanel.add(JLabel("Custom Header (optional):"), gbc)

        gbc.gridx = 1
        self.customHeaderField = JTextField("", 40)
        topPanel.add(self.customHeaderField, gbc)

        row += 1

        # Action Buttons
        gbc.gridx = 0
        gbc.gridy = row
        topPanel.add(JLabel("Actions:"), gbc)

        gbc.gridx = 1
        buttonsPanel = JPanel()

        self.loadButton = JButton("Load Requests")
        self.loadButton.addActionListener(self)
        buttonsPanel.add(self.loadButton)

        self.sendButton = JButton("Send Selected to Repeater")
        self.sendButton.addActionListener(self)
        buttonsPanel.add(self.sendButton)

        topPanel.add(buttonsPanel, gbc)

        self.mainPanel.add(topPanel, BorderLayout.NORTH)

        # Request List
        centerPanel = JPanel(BorderLayout())
        self.requestListModel = DefaultListModel()
        self.requestList = JList(self.requestListModel)
        self.requestList.setSelectionMode(ListSelectionModel.MULTIPLE_INTERVAL_SELECTION)
        centerPanel.add(JScrollPane(self.requestList), BorderLayout.CENTER)
        self.mainPanel.add(centerPanel, BorderLayout.CENTER)

        # Log Area
        self.logArea = JTextArea()
        self.logArea.setEditable(False)
        self.mainPanel.add(JScrollPane(self.logArea), BorderLayout.SOUTH)

    def getTabCaption(self):
        return "Swagger2Repeater"

    def getUiComponent(self):
        return self.mainPanel

    # -------------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------------

    def actionPerformed(self, event):
        src = event.getSource()
        if src == self.loadButton:
            self._on_load_clicked()
        elif src == self.sendButton:
            self._on_send_clicked()
        elif src == self.browseButton:
            self._on_browse_clicked()

    def _println(self, msg):
        try:
            self._stdout.write(msg + "\n")
        except:
            pass
        try:
            self.logArea.append(msg + "\n")
            self.logArea.setCaretPosition(self.logArea.getDocument().getLength())
        except:
            pass

    # -------------------------------------------------------------------
    # Swagger loading
    # -------------------------------------------------------------------

    def _on_browse_clicked(self):
        chooser = JFileChooser()
        r = chooser.showOpenDialog(self.mainPanel)
        if r == JFileChooser.APPROVE_OPTION:
            file = chooser.getSelectedFile()
            self.swaggerField.setText(file.getAbsolutePath())

    def _load_swagger_text(self, source):
        if source.startswith("http://") or source.startswith("https://"):
            self._println("[*] Loading Swagger from URL: %s" % source)
            url = URL(source)
            conn = url.openConnection()
            conn.setRequestMethod("GET")
            reader = BufferedReader(InputStreamReader(conn.getInputStream(), "UTF-8"))
        else:
            self._println("[*] Loading Swagger from file: %s" % source)
            reader = BufferedReader(InputStreamReader(FileInputStream(source), "UTF-8"))

        lines = []
        line = reader.readLine()
        while line is not None:
            lines.append(line)
            line = reader.readLine()
        reader.close()
        return "\n".join(lines)

    def _on_load_clicked(self):
        source = self.swaggerField.getText().strip()
        if not source:
            self._println("[!] Please provide a Swagger file path or URL.")
            return

        try:
            text = self._load_swagger_text(source)
        except Exception as e:
            self._println("[!] Failed to load Swagger: %s" % e)
            return

        try:
            swagger = json.loads(text)
        except Exception as e:
            self._println("[!] Failed to parse JSON: %s" % e)
            return

        self.swagger = swagger
        self.is_oas3 = bool(swagger.get("openapi"))

        if self.is_oas3:
            self._println("[+] Detected OpenAPI 3.x")
            host, port, https, base_path = self._extract_oas3_base(swagger)
        else:
            self._println("[+] Detected Swagger 2.0")
            host, port, https, base_path = self._extract_swagger2_base(swagger)

        self._println("[*] Base: %s://%s:%d%s" %
                      ("https" if https else "http", host, port, base_path))

        self._requests = []
        self.requestListModel.clear()

        selected_methods = [
            m.lower() for m, cb in self.methodCheckboxes.items() if cb.isSelected()
        ]
        if not selected_methods:
            self._println("[!] No HTTP methods selected.")
            return

        paths = swagger.get("paths", {})
        count = 0

        for path, item in paths.items():
            if not isinstance(item, dict):
                continue

            common_params = item.get("parameters", [])

            for method, operation in item.items():
                if method.lower() not in selected_methods:
                    continue
                if not isinstance(operation, dict):
                    continue

                op = dict(operation)
                op["parameters"] = list(op.get("parameters", [])) + list(common_params)

                try:
                    label, req = self._build_request_bytes(
                        host, port, https, base_path, path, method.upper(), op
                    )
                    self._requests.append({
                        "label": label,
                        "host": host,
                        "port": port,
                        "https": https,
                        "request_bytes": req
                    })
                    self.requestListModel.addElement(label)
                    count += 1
                except Exception as e:
                    self._println("[!] Failed to build request for %s %s: %s" %
                                  (method.upper(), path, e))

        self._println("[*] Loaded %d requests." % count)

    # -------------------------------------------------------------------
    # Sending to Repeater
    # -------------------------------------------------------------------

    def _on_send_clicked(self):
        indices = self.requestList.getSelectedIndices()
        if not indices:
            self._println("[!] Select at least one request to send.")
            return

        for i in indices:
            if 0 <= i < len(self._requests):
                req = self._requests[i]
                try:
                    self._callbacks.sendToRepeater(
                        req["host"], req["port"], req["https"],
                        req["request_bytes"], req["label"]
                    )
                    self._println("[+] Sent to Repeater: %s" % req["label"])
                except Exception as e:
                    self._println("[!] Failed to send: %s" % e)

    # -------------------------------------------------------------------
    # Base URL parsing
    # -------------------------------------------------------------------

    def _extract_swagger2_base(self, swagger):
        host = swagger.get("host", "localhost")
        schemes = swagger.get("schemes", ["http"])
        scheme = schemes[0]
        base_path = swagger.get("basePath", "")
        if base_path and not base_path.startswith("/"):
            base_path = "/" + base_path

        port = 443 if scheme == "https" else 80
        if ":" in host:
            host, p = host.split(":", 1)
            try:
                port = int(p)
            except:
                pass

        return host, port, scheme == "https", base_path

    def _extract_oas3_base(self, swagger):
        servers = swagger.get("servers", [])
        if not servers:
            return "localhost", 80, False, ""

        url = servers[0].get("url", "")
        m = re.match(r"^(https?)://([^/]+)(/.*)?$", url)
        if not m:
            return "localhost", 80, False, ""

        scheme = m.group(1)
        host_port = m.group(2)
        base_path = m.group(3) or ""
        if base_path and not base_path.startswith("/"):
            base_path = "/" + base_path

        port = 443 if scheme == "https" else 80
        host = host_port
        if ":" in host_port:
            host, p = host_port.split(":", 1)
            try:
                port = int(p)
            except:
                pass

        return host, port, scheme == "https", base_path

    # -------------------------------------------------------------------
    # Request builder (CRLF fix + custom header)
    # -------------------------------------------------------------------

    def _fill_path_params(self, path):
        return re.sub(r"\{[^}]+\}", "1", path)

    def _build_query_string(self, operation):
        params = operation.get("parameters", [])
        qs = []
        for p in params:
            if p.get("in") == "query":
                qs.append("%s=%s" % (p.get("name", "q"), "value"))
        return "?" + "&".join(qs) if qs else ""

    def _build_headers_from_params(self, op):
        headers = []
        for p in op.get("parameters", []):
            if p.get("in") == "header":
                headers.append("%s: %s" % (p.get("name"), "value"))
        return headers

    def _build_cookie_header(self, op):
        cookies = []
        for p in op.get("parameters", []):
            if p.get("in") == "cookie":
                cookies.append("%s=%s" % (p.get("name"), "value"))
        if cookies:
            return "Cookie: " + "; ".join(cookies)
        return None

    def _needs_body(self, method, op):
        if method in ["POST", "PUT", "PATCH"]:
            return True
        if self.is_oas3 and op.get("requestBody"):
            return True
        for p in op.get("parameters", []):
            if p.get("in") == "body":
                return True
        return False

    def _get_body_schema(self, op):
        if self.is_oas3:
            rb = op.get("requestBody")
            if not isinstance(rb, dict):
                return None
            content = rb.get("content", {})
            for _, v in content.items():
                if isinstance(v, dict) and "schema" in v:
                    return v["schema"]
            return None
        else:
            for p in op.get("parameters", []):
                if p.get("in") == "body":
                    return p.get("schema")
            return None

    def _build_request_bytes(self, host, port, https,
                             base_path, path, method, op):

        full_path = base_path.rstrip("/") + "/" + self._fill_path_params(path).lstrip("/")
        qs = self._build_query_string(op)
        uri = full_path + qs

        body = ""
        has_body = self._needs_body(method, op)
        if has_body:
            schema = self._get_body_schema(op)
            if schema:
                try:
                    body = json.dumps(self._generate_example_from_schema(schema, 0))
                except:
                    body = "{}"
            else:
                body = "{}"

        lines = []
        lines.append("%s %s HTTP/1.1" % (method, uri))
        lines.append("Host: %s" % host)
        lines.append("User-Agent: Swagger2Repeater/1.0")
        lines.append("Accept: application/json")

        if has_body:
            lines.append("Content-Type: application/json")
            lines.append("Content-Length: %d" % len(body))

        for h in self._build_headers_from_params(op):
            lines.append(h)

        cookie = self._build_cookie_header(op)
        if cookie:
            lines.append(cookie)

        # Custom Header(s)
        custom_raw = ""
        try:
            custom_raw = self.customHeaderField.getText().strip()
        except:
            pass
        if custom_raw:
            for ch in custom_raw.split("\n"):
                ch = ch.strip()
                if ch:
                    lines.append(ch)

        lines.append("Connection: close")

        # CRLF FIX – Always add a blank line before the body
        req_str = "\r\n".join(lines) + "\r\n\r\n"
        if has_body:
            req_str += body

        return ("%s %s" % (method, path),
                self._helpers.stringToBytes(req_str))

    # -------------------------------------------------------------------
    # JSON Schema → Example Object
    # -------------------------------------------------------------------

    def _generate_example_from_schema(self, s, depth):
        if depth > MAX_SCHEMA_DEPTH:
            return "value"

        if "$ref" in s:
            target = self._resolve_ref(s["$ref"])
            return self._generate_example_from_schema(target, depth + 1) if target else {}

        t = s.get("type")
        if t == "object" or ("properties" in s and not t):
            obj = {}
            for name, prop in s.get("properties", {}).items():
                obj[name] = self._generate_example_from_schema(prop, depth + 1)
            return obj
        if t == "array":
            return [self._generate_example_from_schema(s.get("items", {}), depth + 1)]
        if t == "string":
            return "string"
        if t in ["integer", "number"]:
            return 1
        if t == "boolean":
            return True
        return "value"

    def _resolve_ref(self, ref):
        if not ref.startswith("#/"):
            return None
        parts = ref[2:].split("/")
        node = self.swagger
        for p in parts:
            if not isinstance(node, dict):
                return None
            node = node.get(p)
            if node is None:
                return None
        return node
