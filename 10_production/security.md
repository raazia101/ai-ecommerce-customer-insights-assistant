\# Week 11 Security and Governance



\## Secrets Management



Sensitive configuration is supplied through environment variables.



Real credentials must not be committed to Git.



`.env.example` contains configuration placeholders only.



Sensitive local files such as:



\- `.env`

\- API keys

\- credential files

\- `04\_data\_eng/key.txt`



are excluded from version control.



\---



\## Input Validation



The API uses Pydantic request models.



Validation includes:



\- non-empty session IDs

\- bounded session ID length

\- non-empty messages

\- bounded message length

\- validated request structure



Customer and order identifiers are validated before approved tools are called.



\---



\## Tool Allowlisting



The agent has access only to approved read-only tools:



\- `customer\_lookup`

\- `order\_status`

\- `kpi\_query`

\- `documentation\_search`



The system does not expose arbitrary tool execution.



\---



\## No Destructive Operations



The current application does not allow:



\- order cancellation

\- refunds

\- customer deletion

\- arbitrary record updates

\- database mutations

\- arbitrary SQL

\- arbitrary Python execution



This significantly limits the impact of prompt injection and malicious tool requests.



\---



\## Prompt Injection Protection



The system uses deterministic routing and a bounded workflow rather than allowing unrestricted model-driven actions.



Security testing includes:



\- direct prompt injection

\- embedded injection

\- system prompt extraction

\- database credential extraction

\- excessive data requests

\- unauthorized tool requests



\---



\## Output Boundaries



Tool and query results are bounded.



The existing agent/tool design uses limits such as:



\- maximum result rows

\- maximum query length

\- maximum workflow steps

\- maximum tool retries



These controls reduce excessive resource consumption and unintended data exposure.



\---



\## Error Handling



Internal implementation errors are not exposed directly to users.



The conversation layer returns a generic service error instead of returning raw exception details.



This prevents leakage of:



\- database configuration

\- filesystem paths

\- dependency information

\- internal stack traces



\---



\## Session Isolation



Each conversation has its own session identifier.



The conversation manager maintains bounded session history.



Clearing a session removes its active context.



Cross-session context leakage is explicitly tested.



\---



\## Dependency Security



Python dependencies are checked using:



```powershell

pip-audit

## Dependency Security Audit

A dependency vulnerability audit was performed using `pip-audit`.

Initial audit result:

- 21 known vulnerabilities
- 8 affected packages

Affected packages:

| Package | Installed Version | Audit Result |
|---|---:|---|
| chromadb | 1.5.9 | Multiple known vulnerabilities |
| jupyterlab | 4.6.3 | Known vulnerabilities |
| multidict | 6.7.1 | CVE-2026-104874 |
| notebook | 7.6.2 | Known vulnerability |
| oauthlib | 3.3.1 | Known vulnerability |
| pymongo | 4.18.0 | Multiple known vulnerabilities |
| tornado | 6.5.8 | Multiple known vulnerabilities |
| urllib3 | 2.7.0 | Multiple known vulnerabilities |

The audit was performed against the complete internship virtual environment. The environment contains both production/runtime dependencies and development/notebook tooling.

Because the internship environment contains a large development dependency set, vulnerabilities were not blindly resolved by upgrading all packages. Doing so could introduce compatibility regressions into the existing RAG, agent, ML, and API stack.

The Week 11 production deployment therefore separates production deployment requirements from the broader development environment where possible.

Known limitations:

- The current audit covers the complete virtual environment rather than only a minimal production lockfile.
- Some flagged packages are development/notebook dependencies and are not necessarily included in the production API/UI containers.
- A future production release should maintain a minimal, pinned runtime dependency set and re-run `pip-audit` against that environment before deployment.
- Vulnerability remediation should be performed with compatibility testing for the RAG, agent, API, and UI layers.
