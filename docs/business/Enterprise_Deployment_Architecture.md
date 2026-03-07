# ScriptPulse vNext.5 Enterprise Deployment Architecture
## Secure, Scalable, Audit-Ready Infrastructure

This document specifies the deployment architecture for ScriptPulse in high-security enterprise environments (Studios, Research Institutions).

---

### 1. The Production API Boundary Layer (PABL)

ScriptPulse is NOT accessed directly via `runner.py` in production.
It is accessed **strictly** via the `ScriptPulseAPI` facade (`scriptpulse/api.py`).

**Guarantees:**
*   **Single-Script Semantics:** No batch processing allowed.
*   **Stateless Execution:** No data persistence between calls.
*   **Role Enforcement:** Every call requires a signed `APIContext`.

---

### 2. Role-Aware Access Control (RAAC)

The system enforces 4 strict roles (`scriptpulse/roles.py`):

| Role | Permissions | Forbidden |
| :--- | :--- | :--- |
| **WRITER** | Full Analysis, Intent Control | Metrics, Scoring |
| **READER** | Full Analysis | Intent Override, Scoring |
| **ADMIN** | System Health | **Content Access** |
| **RESEARCHER** | Aggregate Telemetry | **Content Access** |

**Implementation:**
*   `check_permission(role, action)` is called before pipeline instantiation.
*   Violation raises `PermissionError` (403 Forbidden).

---

### 3. Security & Privacy Isolation Layer (SPIL)

#### Data Lifecycle
1.  **Ingest:** Text arrives via TLS 1.3 encrypted stream.
2.  **Process:** Analysis runs in ephemeral memory.
3.  **Scrub:** `security.scrub_memory()` is called immediately after JSON generation.
4.  **Zero-Retention:** No text is written to disk. Only the `ComplianceLog` (metadata) persists.

#### Isolation Modes
*   **SaaS Mode:** Multi-tenant via `tenant_id` logic.
*   **On-Prem Mode:** Air-gapped container execution.

---

### 4. Deployment Specifications (Docker)

Recommended Container Spec:

```dockerfile
FROM python:3.9-slim-buster
# Lock dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
# Copy Source (Immutable)
COPY scriptpulse /app/scriptpulse
# Create non-root user
RUN useradd -m pulseuser
USER pulseuser
# Entrypoint
ENTRYPOINT ["gunicorn", "scriptpulse.api:app"]
```

**Network Policies:**
*   **Inbound:** Port 443 (HTTPS) only.
*   **Outbound:** Blocked (Zero-Exfiltration Policy).

---

### 5. Compliance & Legal Defense (CLDL)

Every execution generates a **Compliance Record**:
*   `RunID` (Deterministic Hash)
*   `Timestamp`
*   `Role invoked`
*   `Assertion`: "NON_DECISIONAL_SUPPORT"

This log proves that the system was used for **descriptive analysis**, not **automated decision making** (hiring/firing), supporting EU AI Act compliance.

---

### 6. Telemetry Without Surveillance (TWOS)

We collect **structural statistics only** (`security.AnonymousTelemetry`):
*   Scene counts
*   Line type ratios
*   Alert frequency
*   **ZERO** text content

This allows product improvement without IP exposure.
