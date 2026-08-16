# Justor AI Frontend Integration Contract

The frontend is production-oriented but intentionally fail-closed: without configured services it shows clear unavailable states and never substitutes invented legal records, statuses, citations or answer text.

## Environment

Configure these build-time variables:

- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_ANON_KEY`
- `VITE_BACKEND_URL`

Google OAuth must be enabled in Supabase and each deployed callback URL must be allow-listed.

## Public read endpoints

The frontend currently expects:

- `GET /public/library?q=&type=`
- `GET /public/guides?status=published&q=&cluster=&page=`
- `GET /public/guides/:slug`
- `GET /public/legal-updates`
- `GET /public/legal-updates/:id`
- `GET /public/product-proof`

Responses may be either a JSON array/object or wrapped in `{ "data": ... }`. Empty arrays produce an honest no-results state. Missing configuration, network failure or non-success responses produce an unavailable state.

## Authenticated research

`POST /chat` receives:

```json
{
  "query": "string",
  "user_role": "citizen | student | professional",
  "language": "en | bn",
  "chat_history": [],
  "context": {
    "id": "optional guide id",
    "title": "optional guide title",
    "topic": "optional guide topic"
  }
}
```

The request includes `Authorization: Bearer <Supabase access token>`. A `401` returns the user to the authentication boundary. The query and Citizen guide context are retained across sign-in.

The response may expose `authorities` or `sources`. Each source should provide stable `id`, `title`, citation/provision where applicable, excerpt, URL, legal status and an explicit verification status. Only these exact verification statuses receive UI badges:

- `Primary Source`
- `Source Checked`
- `Human Legal Reviewed`

Unknown or missing statuses receive no badge.

Quota should be returned as:

```json
{
  "quota": {
    "remaining": 2,
    "limit": 3
  }
}
```

The frontend shows product allowances before use—Citizen `3`, Law Student `30`, Legal Professional `50`—but displays live remaining usage only from this backend quota response.

## Data safety rules

- Legal Library, guides, updates, source links, legal statuses and review badges are backend-driven.
- The 60-guide Markdown pack is not bundled into the active application.
- The public guide count is derived from returned published records, not the editorial pack size.
- A missing Bangla guide body displays the approved disclosure and links to the English route; it never silently places English body content under the Bangla UI.
