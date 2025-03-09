Below is a concise summary of the **Pyvider Logging Emoji Matrix** reference:

---

### Overview

- **Purpose:** Provide a compact, visual prefix for log messages to improve observability.
- **Structure:** Each log message is prefixed with three emojis indicating:
  - **Domain** (e.g., Server, Client, Plugin)
  - **Action** (e.g., Start, Handshake, Read)
  - **Status** (e.g., Success, Error, Warn)

---

### Emoji Mapping

#### Domain (First Emoji)
- **🛎️:** Server
- **🙋:** Client
- **🔌:** Plugin
- **🌐:** TCP
- **📞:** Unix
- **🤝:** Handshake
- **🔐:** Security
- **⚙️:** Config
- **📡:** Protocol
- **🧰:** Utils
- **❗:** Exception
- **🛰️:** Telemetry
- **💉:** DI

#### Action (Second Emoji)
- **🚀:** Start
- **🤝:** Handshake
- **🕵️:** Connect
- **🕹:** Listen
- **📖:** Read
- **📤:** Write
- **📥:** Receive
- **🔒:** Close
- **🔍:** Parse
- **📝:** Build
- **🔁:** Retry
- **🧪:** Test
- **📜:** Cert
- **🔑:** Key
- **🛡️:** Encrypt

#### Status (Third Emoji)
- **✅:** Success
- **❌:** Error
- **🚫:** Fail
- **⚠️:** Warn
- **🛑:** Stop
- **👍:** Affirm
- **👀:** Monitor
- **💥:** Crash
- **⭕:** None
- **⏸️:** Suspend
- **▶️:** Resume
- **⏳:** Pending
- **💤:** Idle
- **🔄:** Ongoing

---

### Usage & Integration

- **Log Format:**
  ```
  [Domain Emoji][Action Emoji][Status Emoji]  Message
  ```
  *Example:* `🔌🚀✅ Starting plugin server`

- **Benefits:**
  - **Visual Scanning:** Quickly identify operational context.
  - **Contextual Clues:** Understand the domain and status at a glance.
  - **Component Identification:** Easily distinguish logs by source (client, server, etc.).

