# Session Lifetime Enforcement

LimaCharlie can enforce a maximum lifetime on web-app sessions for users in a specific email domain. Once enabled, users are automatically signed out of the web app after the configured duration, measured from the moment they last entered their credentials. They must then sign in again to continue.

This is typically used by enterprise and regulated customers who require periodic re-authentication, regardless of whether a user is actively using the web app.

## How It Works

- The configured maximum lifetime is applied to every user whose email belongs to the enrolled domain.
- The countdown starts when the user authenticates (entering password, completing SSO, or completing MFA). Background token refreshes do **not** reset it.
- When the limit is reached, the web app shows a brief notice and signs the user out. The user can sign back in immediately and a new countdown begins.
- The control affects the web app only. API tokens, sensor enrollment, and integrations are not impacted.

## Scope

- The setting is configured per email domain. All users authenticating with an email in the enrolled domain are subject to the same limit.
- Customers with multiple email domains (for example, primary and secondary brands) can enroll each domain independently.
- The setting can be combined with [Strict SSO Enforcement](sso.md) and other per-domain authentication controls.

## User Experience

- During the session, no banner or countdown is shown — the experience is identical to a normal session.
- At expiry, the user sees a short message indicating that the session has reached its maximum lifetime, and is redirected to the sign-in page.
- For users who are already signed in at the moment the policy is first enabled for their domain, the countdown applies from their most recent sign-in. They will typically be signed out shortly after enablement and asked to sign in once; subsequent sessions follow the configured limit.

## Requesting Enrollment

Session lifetime enforcement is configured by LimaCharlie staff. To enable it for your domain, contact your LimaCharlie account team or open a support request including:

- The email domain (or domains) to enroll.
- The maximum session duration (for example, "8 hours" or "7 days").

## Related Articles

- [Single Sign-On](sso.md)
- [User Access](user-access.md)
