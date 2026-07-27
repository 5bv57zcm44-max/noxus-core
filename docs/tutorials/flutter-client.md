# Tutorial: Flutter client

Authenticate over HTTPS to the same Frappe origin, retain the session cookie in a secure cookie jar,
fetch `/api/resource/<DocType>` with explicit fields, and call versioned whitelisted methods. Do not
embed administrator credentials or API secrets in the app. Handle 401, 403, 409, 429, and 503 states
explicitly and select translated object values using the device locale.
