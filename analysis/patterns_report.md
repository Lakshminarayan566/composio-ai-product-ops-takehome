# 100-App Pattern Analysis

Dataset size: **100 apps**

## Headline findings

- **73/100 (73.0%)** are classified as directly buildable.
- **12/100 (12.0%)** are partially buildable because of meaningful restrictions.
- **1/100 (1.0%)** are currently classified as not buildable.
- **67/100 (67.0%)** have self-serve credential access.
- **8/100 (8.0%)** have a paid/admin/partner gate.
- **50/100 (50.0%)** have MCP marked Yes by the research agent.

## Authentication

| Method | Apps | % |
|---|---:|---:|
| OAuth2 | 41 | 41.0% |
| API key | 28 | 28.0% |
| token | 25 | 25.0% |
| Basic | 6 | 6.0% |
| bearer | 1 | 1.0% |
| password | 1 | 1.0% |
| magic link | 1 | 1.0% |
| OTP | 1 | 1.0% |
| social login | 1 | 1.0% |
| SSO | 1 | 1.0% |
| application key | 1 | 1.0% |
| API token | 1 | 1.0% |
| OAuth2/token | 1 | 1.0% |
| API key/token | 1 | 1.0% |

## Self-serve vs gated access

| Access type | Apps | % |
|---|---:|---:|
| Self-serve | 67 | 67.0% |
| Unknown | 24 | 24.0% |
| Paid-plan required | 4 | 4.0% |
| Partner/Sales gated | 3 | 3.0% |
| Admin approval | 1 | 1.0% |
| Trial | 1 | 1.0% |

## API surface

| Surface | Apps | % |
|---|---:|---:|
| REST | 80 | 80.0% |
| SDK | 12 | 12.0% |
| Webhooks | 11 | 11.0% |
| GraphQL | 5 | 5.0% |
| CLI | 4 | 4.0% |
| MCP | 1 | 1.0% |

## MCP support

| MCP | Apps | % |
|---|---:|---:|
| Yes | 50 | 50.0% |
| Unknown | 46 | 46.0% |
| No | 4 | 4.0% |

## Buildability

| Verdict | Apps | % |
|---|---:|---:|
| Yes | 73 | 73.0% |
| Unknown | 14 | 14.0% |
| Partial | 12 | 12.0% |
| No | 1 | 1.0% |

## Most common blockers

- **None** — 63 apps (63.0%)
- **Unknown** — 14 apps (14.0%)
- **Client registration plus user authorization; MCP authentication is OAuth and follows the user's CRM permissions.** — 1 apps (1.0%)
- **OAuth app registration requires contacting Copper; individual API keys can be generated from Copper settings.** — 1 apps (1.0%)
- **Authentication method not specified in the evidence** — 1 apps (1.0%)
- **Customer/admin authorization is required; distributed apps must use global OAuth.** — 1 apps (1.0%)
- **Requires an OAuth-capable MCP server or a supported static credential; a public MCP server with no authentication cannot be connected.** — 1 apps (1.0%)
- **Rate limit of 180 requests per minute per API key may restrict high‑volume usage** — 1 apps (1.0%)
- **API keys are created for machine users with fine-grained permissions; MCP uses the user's existing Plain account.** — 1 apps (1.0%)
- **Requires Meta business portfolio/WABA, phone-number setup, permissions, and access-token configuration.** — 1 apps (1.0%)

## Easy-win candidates

**63 apps** are both self-serve/trial and classified as buildable.

Salesforce, HubSpot, Pipedrive, Attio, Twenty, Podio, Zoho CRM, Intercom, Front, LiveAgent, Plain, Gorgias, Slack, Twilio, Lark (Larksuite), Pumble, Telegram, Aircall, Vonage, Meta Ads, Mailchimp, systeme.io, Shopify, WooCommerce, BigCommerce, Squarespace, Gumroad, DataForSEO, SE Ranking, MrScraper, Apify, Firecrawl, Clay, GitHub, Vercel, Netlify, Cloudflare, Supabase, Neo4j, MongoDB Atlas

## Outreach / high-friction candidates

**14 apps** have a partial/no buildability verdict or an explicit access gate.

Copper, DealCloud, Zendesk, Pylon, WhatsApp Business, Google Ads, LinkedIn Ads, Pinterest, Ahrefs, Brex, PitchBook, NotebookLM, Otter AI, Mermaid CLI

## Evidence / uncertainty

| Field | Unknown | % |
|---|---:|---:|
| auth_methods | 20 | 20.0% |
| self_serve_or_gated | 24 | 24.0% |
| api_surface | 16 | 16.0% |
| api_breadth | 31 | 31.0% |
| mcp | 46 | 46.0% |
| buildability | 14 | 14.0% |
| main_blocker | 14 | 14.0% |
| evidence_url | 7 | 7.0% |

## Category × buildability

- **CRM and Sales** → Yes: 8, Partial: 2
- **Support and Helpdesk** → Partial: 2, Yes: 7, Unknown: 1
- **Communications and Messaging** → Yes: 9, Partial: 1
- **Marketing, Ads, Email and Social** → Partial: 3, Yes: 4, Unknown: 3
- **Ecommerce** → Yes: 6, Unknown: 4
- **Data, SEO and Scraping** → Yes: 6, Partial: 1, Unknown: 3
- **Developer, Infra and Data platforms** → Yes: 9, Unknown: 1
- **Productivity and Project Management** → Yes: 9, Unknown: 1
- **Finance and Fintech** → Yes: 8, Unknown: 1, Partial: 1
- **AI, Research and Media-native** → Partial: 2, Yes: 7, No: 1

## Category × credential access

- **CRM and Sales** → Self-serve: 7, Unknown: 2, Partner/Sales gated: 1
- **Support and Helpdesk** → Admin approval: 1, Self-serve: 5, Unknown: 4
- **Communications and Messaging** → Self-serve: 8, Unknown: 2
- **Marketing, Ads, Email and Social** → Self-serve: 5, Partner/Sales gated: 1, Unknown: 3, Trial: 1
- **Ecommerce** → Self-serve: 5, Unknown: 5
- **Data, SEO and Scraping** → Self-serve: 6, Paid-plan required: 1, Unknown: 3
- **Developer, Infra and Data platforms** → Self-serve: 9, Unknown: 1
- **Productivity and Project Management** → Self-serve: 9, Unknown: 1
- **Finance and Fintech** → Self-serve: 7, Unknown: 1, Paid-plan required: 2
- **AI, Research and Media-native** → Paid-plan required: 1, Partner/Sales gated: 1, Self-serve: 6, Unknown: 2

## Verification status in dataset

- **Unverified** — 80
- **Verified** — 19
- **Unresolved** — 1

Generated automatically from `data/research_results.csv`.