# Commercialisation and private production policy

This public repository is a portfolio and reference implementation released under the MIT License. It demonstrates the product concept, constrained analytics architecture, testing approach, and safety boundary.

A future revenue-generating production application must not be developed directly in this public repository.

## Required separation

Commercial development should use a separate private repository with proprietary licensing. The private product may reuse MIT-licensed components from this repository, but commercial-only features, customer data handling, internal prompts, deployment configuration, infrastructure code, billing logic, monitoring, and operational controls should remain private.

## Minimum production controls

Before accepting paying users or sensitive data, the private system should include:

- least-privilege identity and access management
- protected default branches and mandatory pull-request review
- multi-factor authentication for maintainers and cloud accounts
- secret storage through a managed secrets service
- separate development, staging, and production environments
- encrypted transport and encrypted storage
- tenant and data-access isolation
- audit logging and security monitoring
- dependency, container, and code vulnerability scanning
- backups and tested recovery procedures
- data retention and deletion controls
- rate limiting, abuse protection, and cost controls
- privacy documentation and applicable regulatory review
- incident response and vulnerability disclosure procedures
- regular penetration testing before high-risk or enterprise use

## Repository rules

Never commit API keys, production credentials, customer datasets, private certificates, database backups, or infrastructure secrets. Public issues and logs must not contain customer or confidential information.

## Licensing model

- Public portfolio/reference repository: MIT License.
- Future commercial product repository: private and proprietary unless a deliberate open-core strategy is approved.
- Shared open-source components: tracked with dependency and licence notices.

Security is an ongoing engineering and operational process. No repository can truthfully be described as completely secure; production readiness must be demonstrated through layered controls, testing, monitoring, and response capability.
