# OpsIT - Security & Compliance Architecture

## Overview
OpsIT is built with security-first principles and full compliance with ISO 27001 and European data protection standards (GDPR).

---

## ISO 27001 Compliance

### Information Security Management System (ISMS)

OpsIT implements ISO 27001:2022 controls across all domains:

#### A.5 Organizational Controls
- **Access Control Policy**: Role-based access control (RBAC)
- **Segregation of Duties**: Admin, agent, and user roles separated
- **Information Security Roles**: Clear responsibilities per role
- **Management Responsibility**: Audit logs for all administrative actions

#### A.6 People Controls
- **User Access Management**: Provisioning and de-provisioning workflows
- **User Authentication**: MFA support, strong password policies
- **Access Rights Review**: Periodic access audits (built-in reports)
- **Removal of Access Rights**: Automated deactivation on user termination

#### A.7 Physical Controls
- **Secure Areas**: Cloud deployment with SOC 2 certified providers
- **Equipment Security**: Docker containers, secure by design

#### A.8 Technological Controls
- **User Endpoint Devices**: Browser-based, no data storage on endpoints
- **Privileged Access Rights**: Separate admin accounts, MFA required
- **Information Access Restriction**: Row-level security per tenant
- **Authentication Information**: Hashed passwords (Argon2), encrypted tokens
- **Secure System Engineering**: Security built into SDLC
- **Secure Development Lifecycle**: Code scanning, dependency checks
- **Change Management**: All changes logged and auditable
- **Capacity Management**: Auto-scaling, performance monitoring
- **Protection from Malware**: Input validation, CSP headers
- **Logging and Monitoring**: Comprehensive audit logs
- **Clock Synchronization**: NTP, UTC timestamps
- **Use of Privileged Utility Programs**: Admin actions logged
- **Software Installation**: Controlled deployment, signed containers
- **Network Security**: TLS 1.3, HTTPS only, security headers
- **Security of Network Services**: API rate limiting, DDoS protection
- **Secure Coding**: OWASP Top 10 compliance
- **Security Testing**: Automated security tests in CI/CD
- **Outsourced Development**: Third-party library audits

---

## Security Architecture

### 1. Authentication & Authorization

#### Authentication Methods
```
Primary: JWT (JSON Web Tokens)
- Access tokens: Short-lived (15 minutes)
- Refresh tokens: Long-lived (7 days), rotating
- Token storage: HttpOnly cookies (frontend)
- Token signing: RS256 (asymmetric)

Enterprise SSO:
- SAML 2.0 support
- OAuth 2.0 / OpenID Connect
- LDAP/Active Directory integration
- Azure AD, Okta, Google Workspace

Multi-Factor Authentication (MFA):
- TOTP (Time-based One-Time Password) via authenticator apps
- SMS backup (optional)
- Email OTP backup
- Required for admin accounts
- Configurable per tenant
```

#### Password Security
```
- Minimum 12 characters (configurable)
- Complexity requirements (uppercase, lowercase, number, special char)
- Password history (prevent reuse of last 5 passwords)
- Hashing: Argon2id (OWASP recommended)
- Salting: Unique salt per password
- Failed login attempts: Account lockout after 5 attempts
- Password expiry: 90 days (configurable)
- Password reset: Secure token-based flow
```

#### Authorization (RBAC)
```
Built-in Roles:
- Super Admin (platform management)
- Tenant Admin (tenant configuration)
- Incident Manager
- Request Manager
- Service Desk Agent
- Knowledge Manager
- End User

Permissions:
- Granular permissions per resource
- Action-based (create, read, update, delete, approve, assign)
- Custom roles with permission sets
- Role inheritance
- Permission checking at API and UI level

Multi-tenancy Security:
- Tenant isolation at database query level
- All queries filtered by tenant_id
- No cross-tenant data access
- Separate encryption keys per tenant
```

---

### 2. Data Encryption

#### Encryption at Rest
```
Database:
- PostgreSQL with transparent data encryption (TDE)
- Encrypted columns for sensitive data (passwords, API keys, personal data)
- pgcrypto extension for field-level encryption
- Encrypted backups

File Storage:
- S3-compatible storage with server-side encryption (SSE)
- Client-side encryption for highly sensitive files
- Encrypted attachment storage
- AES-256-GCM encryption

Encryption Keys:
- Key management system (KMS) - AWS KMS, Azure Key Vault, or HashiCorp Vault
- Key rotation every 90 days
- Separate keys per tenant
- Master key encryption
```

#### Encryption in Transit
```
- TLS 1.3 (minimum TLS 1.2)
- HTTPS everywhere (HSTS enabled)
- Certificate management (Let's Encrypt auto-renewal)
- Perfect Forward Secrecy (PFS)
- Strong cipher suites only
- WebSocket connections over WSS (secure WebSocket)
```

---

### 3. Data Privacy & GDPR Compliance

#### GDPR Requirements Implementation

**Right to Access (Article 15)**
```
- User can export all their personal data
- API endpoint: GET /api/v1/users/me/data-export
- Includes: tickets, comments, attachments, profile data
- Format: JSON or PDF
```

**Right to Erasure (Article 17)**
```
- User can request account deletion
- API endpoint: DELETE /api/v1/users/me
- Personal data anonymization (replace with "Deleted User")
- Ticket history preserved (pseudonymized)
- Hard delete after retention period (configurable)
```

**Right to Data Portability (Article 20)**
```
- Export data in machine-readable format (JSON, CSV)
- API endpoint: GET /api/v1/users/me/data-export?format=json
```

**Right to Rectification (Article 16)**
```
- User can update their profile data
- Audit log tracks all changes
```

**Data Minimization (Article 5)**
```
- Collect only necessary data
- No optional fields without explicit consent
- Regular data cleanup (archived tickets after X years)
```

**Consent Management**
```
- Explicit consent for optional data collection
- Consent tracking in database
- Withdraw consent option
- Cookie consent banner (for portal)
```

#### Data Residency
```
- European data centers (AWS eu-central-1, eu-west-1)
- No data transfer outside EU without explicit consent
- Schrems II compliance
- Data Processing Agreements (DPA) with all vendors
```

#### Data Retention Policy
```
- Active tickets: Unlimited
- Closed tickets: 7 years (default, configurable)
- Audit logs: 7 years (compliance requirement)
- User data: Until account deletion + 30 days
- Backups: 90 days retention
- Deleted data: Unrecoverable after retention period
```

---

### 4. Audit Logging & Monitoring

#### Comprehensive Audit Trail
```
Logged Events:
- All authentication attempts (success/failure)
- All authorization failures
- All CRUD operations on sensitive entities
- Administrative actions
- Configuration changes
- Data exports
- User access to sensitive data
- API calls (with IP, user agent)
- File uploads/downloads

Audit Log Fields:
- Timestamp (UTC, ISO 8601)
- User ID
- Tenant ID
- Action (verb + resource)
- Entity type and ID
- Old values (JSON)
- New values (JSON)
- IP address
- User agent
- Result (success/failure)
- Error message (if failed)

Log Storage:
- Immutable logs (append-only)
- Encrypted at rest
- 7-year retention (ISO 27001 requirement)
- Separate log database (prevent tampering)
- SIEM integration ready (Splunk, ELK)
```

#### Security Monitoring
```
Real-time Alerts:
- Multiple failed login attempts
- Privilege escalation attempts
- Mass data export
- Suspicious API usage patterns
- Configuration changes by admins
- Access from unusual locations/IPs

Metrics Tracked:
- Authentication success/failure rate
- API response times
- Error rates
- Database query performance
- Resource utilization
- Security events per hour

Dashboard:
- Security overview for admins
- Failed login attempts map
- Active sessions
- Recent audit events
- Compliance status
```

---

### 5. API Security

#### API Authentication
```
- Bearer token (JWT) in Authorization header
- API keys for service integrations
- OAuth 2.0 for third-party apps
- Scope-based permissions for OAuth
```

#### API Security Measures
```
Rate Limiting:
- Per user: 1000 requests/hour
- Per IP: 5000 requests/hour
- Per tenant: 50,000 requests/hour
- Configurable per endpoint
- HTTP 429 (Too Many Requests) response

Input Validation:
- Pydantic models for all inputs
- Strict type checking
- Maximum length validation
- SQL injection prevention (ORM with parameterized queries)
- XSS prevention (output encoding)
- CSRF protection (for web UI)
- NoSQL injection prevention (if using MongoDB for any feature)

Output Sanitization:
- Remove sensitive data from responses
- No stack traces in production
- Generic error messages to users
- Detailed errors in logs only

API Versioning:
- Version in URL (/api/v1/)
- Deprecation warnings
- Backward compatibility guarantees

Security Headers:
- Content-Security-Policy (CSP)
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Strict-Transport-Security (HSTS)
- Referrer-Policy: strict-origin-when-cross-origin
- Permissions-Policy
```

#### API Documentation Security
```
- No sensitive endpoints in public docs
- Example requests with dummy data only
- Authentication required for Swagger UI in production
- API key redaction in examples
```

---

### 6. Application Security (OWASP Top 10)

#### A01 - Broken Access Control
```
✅ Row-level security (tenant_id filtering)
✅ Permission checks on every request
✅ No direct object references (use UUIDs)
✅ Ownership validation (user can only edit their tickets)
✅ Admin actions separated and logged
```

#### A02 - Cryptographic Failures
```
✅ TLS 1.3 for all connections
✅ Encrypted sensitive data at rest
✅ Strong hashing (Argon2id)
✅ No sensitive data in logs
✅ Secure random number generation
```

#### A03 - Injection
```
✅ ORM with parameterized queries (SQLAlchemy)
✅ Input validation with Pydantic
✅ No dynamic SQL construction
✅ Prepared statements only
✅ Least privilege database user
```

#### A04 - Insecure Design
```
✅ Threat modeling during design phase
✅ Security by default
✅ Fail securely (deny by default)
✅ Defense in depth
✅ Secure development lifecycle
```

#### A05 - Security Misconfiguration
```
✅ Secure defaults
✅ No default credentials
✅ Minimal attack surface (no unnecessary features)
✅ Automated security scanning
✅ Regular updates and patching
```

#### A06 - Vulnerable and Outdated Components
```
✅ Dependency scanning (Snyk, Dependabot)
✅ Automated updates for security patches
✅ Regular vulnerability assessments
✅ Software Bill of Materials (SBOM)
```

#### A07 - Identification and Authentication Failures
```
✅ MFA support
✅ Strong password requirements
✅ Account lockout policy
✅ Session timeout (30 minutes inactive)
✅ No credential stuffing (rate limiting)
```

#### A08 - Software and Data Integrity Failures
```
✅ Signed container images
✅ Integrity checks for uploads
✅ Immutable audit logs
✅ Secure CI/CD pipeline
```

#### A09 - Security Logging and Monitoring Failures
```
✅ Comprehensive audit logs
✅ Real-time alerting
✅ Log tampering prevention
✅ SIEM integration
```

#### A10 - Server-Side Request Forgery (SSRF)
```
✅ Whitelist allowed URLs for webhooks
✅ No user-controlled URLs in backend requests
✅ Network segmentation
```

---

### 7. Infrastructure Security

#### Docker Security
```
- Non-root user in containers
- Read-only root filesystem where possible
- Minimal base images (Alpine Linux)
- No secrets in Dockerfile or images
- Secrets via environment variables or secrets management
- Container scanning (Trivy, Clair)
- Signed images (Docker Content Trust)
- Resource limits (CPU, memory)
- Network policies (isolate containers)
```

#### Database Security
```
PostgreSQL Hardening:
- Separate database user per tenant (option)
- Least privilege principle
- SSL/TLS connections only
- No public internet access
- Firewall rules (only app server can connect)
- Regular backups (encrypted, tested restores)
- Point-in-time recovery (PITR)
- Row-level security (RLS) for multi-tenancy
- Audit logging enabled (pgaudit extension)
```

#### Network Security
```
- Private VPC/VNET
- Network segmentation (DMZ, app, database tiers)
- No SSH access to production (bastion host if needed)
- Firewall rules (allow only necessary ports)
- DDoS protection (Cloudflare, AWS Shield)
- VPN for admin access
- IP whitelisting for admin panel (optional)
```

#### Secrets Management
```
- No secrets in code or config files
- Environment variables for configuration
- HashiCorp Vault or cloud KMS for secrets
- Automatic secret rotation
- Secrets encrypted at rest
- Access logging for secret retrieval
```

---

### 8. Incident Response & Business Continuity

#### Security Incident Response
```
Detection:
- Automated alerts
- Log analysis
- User reports

Response Plan:
1. Identification: Confirm security incident
2. Containment: Isolate affected systems
3. Eradication: Remove threat
4. Recovery: Restore services
5. Lessons Learned: Post-incident review

Responsibilities:
- Incident Response Team (designated users)
- Communication plan
- Escalation procedures
- External notification (GDPR 72-hour rule)
```

#### Business Continuity
```
Backup Strategy:
- Automated daily backups
- Off-site backup storage
- Encrypted backups
- Tested restore procedures
- RPO: 1 hour (recovery point objective)
- RTO: 4 hours (recovery time objective)

Disaster Recovery:
- Multi-region deployment (optional)
- Failover procedures
- DR testing (quarterly)
- Documentation and runbooks
```

---

### 9. Secure Development Lifecycle (SDL)

#### Development Phase
```
- Secure coding guidelines
- OWASP guidelines followed
- Code reviews (mandatory)
- Threat modeling for new features
- Static Application Security Testing (SAST)
```

#### CI/CD Security
```
- Automated security tests
- Dependency vulnerability scanning
- Container image scanning
- Secret scanning (prevent commits with secrets)
- Infrastructure as Code (IaC) scanning
- SAST and DAST tools
- Code signing
```

#### Testing Phase
```
- Unit tests for security functions
- Integration tests for auth flows
- Penetration testing (annual)
- Vulnerability assessments (quarterly)
- Bug bounty program (future)
```

#### Deployment Phase
```
- Immutable infrastructure
- Blue-green deployments
- Automated rollback on errors
- Change management process
- Production access logging
```

---

### 10. Compliance & Certifications

#### ISO 27001:2022
- Full ISMS implementation
- Risk assessment and treatment
- Internal audits (semi-annual)
- Management review (quarterly)
- Continual improvement

#### GDPR (EU General Data Protection Regulation)
- Privacy by design
- Data protection impact assessment (DPIA)
- Data Processing Agreement (DPA) with customers
- EU-based data centers
- Breach notification procedures

#### SOC 2 Type II (Future)
- Security, availability, confidentiality controls
- Annual audit by third-party

#### ISO 9001 (Quality Management) (Future)
- Quality processes
- Customer satisfaction
- Continual improvement

---

### 11. Third-Party Risk Management

#### Vendor Security
```
- Due diligence before vendor selection
- Security questionnaires
- SOC 2 reports required
- Data Processing Agreements (DPA)
- Regular vendor reviews
- Exit strategy planning
```

#### Dependencies
```
- Only trusted libraries (npm, PyPI)
- License compliance checks
- Regular updates
- Vulnerability monitoring
- Minimal dependencies principle
```

---

### 12. User Privacy & Data Handling

#### Personal Data Collected
```
Minimal necessary data:
- Email (required)
- Name (required)
- Phone (optional)
- Job title (optional)
- Department (optional)

Ticket data:
- Description (may contain PII - encrypted)
- Attachments (scanned for malware)
- Comments (may contain PII)

Not collected:
- Payment information (handled by third-party payment processor)
- Social media data
- Biometric data
- Sensitive personal data (health, religion, etc.) unless explicitly needed
```

#### Data Anonymization
```
- Anonymize closed tickets after retention period
- Pseudonymization for analytics
- Aggregate statistics only (no individual tracking)
```

---

### 13. Training & Awareness

#### Security Training
```
- Onboarding security training for developers
- Annual security awareness training
- Phishing simulation tests
- Secure coding workshops
- Incident response drills
```

#### Documentation
```
- Security policies published
- Privacy policy for users
- Terms of Service
- Data Processing Agreement template
- Security best practices guide
```

---

## Security Checklist (Pre-Production)

- [ ] All passwords hashed with Argon2id
- [ ] MFA enabled for admin accounts
- [ ] TLS 1.3 configured and enforced
- [ ] Security headers implemented
- [ ] Rate limiting active
- [ ] Audit logging comprehensive and tested
- [ ] GDPR compliance verified (DPA, privacy policy, consent management)
- [ ] Backups automated and tested
- [ ] Incident response plan documented
- [ ] Vulnerability scan passed
- [ ] Penetration test completed
- [ ] SAST and DAST clean
- [ ] Docker images scanned
- [ ] Secrets not in code/repo
- [ ] Database hardened
- [ ] Network segmented
- [ ] Monitoring and alerts configured
- [ ] Admin access restricted and logged
- [ ] Data retention policy implemented
- [ ] User data export/delete functions working
- [ ] ISO 27001 controls implemented

---

## Continuous Security

### Monthly
- Review audit logs
- Check for failed login attempts
- Update dependencies
- Review access rights

### Quarterly
- Vulnerability assessment
- Access rights audit
- DR test
- Compliance review

### Annually
- Penetration testing
- ISO 27001 internal audit
- Security training
- Disaster recovery full test
- Risk assessment update
- Policy review

---

## Contact

**Security Issues**: security@opsit.eu
**Data Privacy**: privacy@opsit.eu
**Compliance**: compliance@opsit.eu

**Responsible Disclosure**: 90-day disclosure policy for security vulnerabilities
