# Cookies and browser storage

**Inventory reviewed:** 24 September 2026, against the source code and an anonymous request to the live homepage (no `Set-Cookie` header was returned).

## Summary

Anonymous readers receive **no analytics, advertising or tracking cookies**. The only browser storage the site writes for readers is the reading list, and only when the reader saves a story.

## Inventory

| Name | Type | Set for | Purpose | Duration | Category |
|---|---|---|---|---|---|
| `healthcode.reading-list.v1` | `localStorage` | Readers who click **Save** | Stores the IDs of saved stories (maximum 100) on this device only; never sent to the server | Until removed by the reader or browser data is cleared | Strictly necessary for a feature the user requested |
| `wordpress_logged_in_*`, `wordpress_sec_*`, `wordpress_test_cookie` | HTTP cookies | Authorized editors only | WordPress authentication and session security | Session / WordPress default | Strictly necessary |
| Network Error Logging policy (`NEL` / `Report-To` headers) | Browser-stored reporting policy | Any visitor | Lets the browser report connection failures to Cloudflare (`a.nel.cloudflare.com`) | 7 days (`max_age=604800`) | Security/reliability, set by the CDN. **Observed** on the review date; can be disabled in Cloudflare |
| `__cf_bm` | HTTP cookie | Any visitor, **only if** Cloudflare bot-management features are enabled on the zone | Bot scoring by the CDN; Cloudflare states it does not track users across sites | 30 minutes of inactivity | Strictly necessary (security). Not observed on the review date |

Cloudflare documents its cookies at <https://developers.cloudflare.com/fundamentals/reference/policies-compliances/cloudflare-cookies/>.

## What is not used

- No analytics (Google Analytics, Cloudflare Web Analytics injection is suppressed with `no-transform`).
- No advertising or affiliate tracking pixels.
- No third-party fonts, so no font-provider requests. Fonts are served locally.
- No embedded social-media widgets.

## Consent position

The current storage is strictly necessary or explicitly requested by the user, so no consent banner is used. **Adding any analytics, advertising, A/B testing or third-party embed changes this.** Under the ePrivacy Directive and UK PECR, that requires prior consent, real blocking before consent, a refusal option as easy as acceptance, and withdrawal. Update this inventory in the same pull request.

## How to clear it

- Reading list: use **Clear reading list** on the reading-list page, or clear site data in your browser settings.
- Editors: sign out, or clear cookies for the site.
