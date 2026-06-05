# TWEO — Project Context for Claude

## Keeping this file up to date

**Claude must update this file whenever any of the following change:**
- A new domain class is designed or implemented (add it to the domain model table)
- A key design decision is made or reversed (update or add to the decisions section)
- A new principle, workflow preference, or coding convention is agreed with the user
- A new media type (TV Series, Game, etc.) moves from "planned" to "in progress" or "done"
- The tech stack, project structure, or local environment changes

Update the relevant section in-place — do not append a changelog. This file should always read as current, not historical. After updating, commit the change alongside the code that triggered it.

---

## What is TWEO?

A group activity organiser. Groups of people coordinate and vote on a shared activity: watch a movie, play video games, board games, role play, etc. The first media type being built is **Movie**, with **TV Series** and **Game** planned next.

## Stack

- **Backend**: Python 3.12 (targeting; currently running on 3.11 locally)
- **Web framework**: FastAPI + Uvicorn (ASGI)
- **Frontend**: TBD — React is the leading candidate
- **CI**: GitHub Actions (`.github/workflows/ci.yml`) — single sequential pipeline: Backend → Frontend → Docs
- **Repo**: https://github.com/adrien-fort/tweo
- **Observability**: structlog (structured logging) + OpenTelemetry SDK (traces + metrics). Auto-instruments FastAPI and SQLAlchemy. Uses `OTEL_SDK_DISABLED=true` to suppress OTel in CI/tests.

## Principles — non-negotiable

- **SOLID** throughout. Dependencies point inward; abstractions live in `core/interfaces/`.
- **OOP** — domain modelled as entities and value objects.
- **TDD** — tests are written before implementation, always.
- **Docstrings** — Google style, Sphinx-ready, on every public class and method.

## Workflow preferences

1. **Discuss design before coding.** For any non-trivial class or feature, share the proposed class map and raise design questions first. Only proceed to code once the user confirms.
2. **Tests first.** Write the test file completely before writing the implementation.
3. **Field validation is mandatory** on all domain fields, including trusted-source data. Use `__post_init__` with `object.__setattr__` for frozen dataclasses.
4. **Use `pytest.approx()`** for any float assertion in tests.
5. **No code comments** unless the WHY is non-obvious. Docstrings only.

## Project structure

```
twe/                                  ← git repo root
├── CLAUDE.md
├── sonar-project.properties
├── .github/workflows/backend-ci.yml  ← lint, typecheck, pytest, SonarCloud
├── infra/
│   ├── terraform/                    ← AKS, PostgreSQL Flexible Server, Key Vault (skeleton)
│   └── ansible/playbooks/            ← deploy.yml, db_migrate.yml (runs alembic upgrade head)
├── backend/
│   ├── pyproject.toml                ← setuptools.build_meta, runtime + dev deps
│   ├── alembic.ini                   ← reads DATABASE_URL env var
│   ├── alembic/versions/             ← migration scripts
│   ├── scripts/reset_dev_db.py       ← drops + recreates dev DB (SQLite only, guards against prod)
│   ├── app/
│   │   ├── main.py                   ← create_app() factory; health + readiness probes; RequestIDMiddleware
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── router.py         ← v1 APIRouter; GET /api/v1/ping
│   │   │       └── dependencies.py   ← get_db_session, get_current_user (501 stub), get_current_admin
│   │   ├── core/
│   │   │   ├── domain/
│   │   │   │   ├── validators.py         ← validate_country_code / validate_language_code / validate_https_url / validate_email
│   │   │   │   ├── enums.py              ← SystemRole, ActivityType, RecurrenceType, EventPrivacy, EventStatus, EventRole, MembershipStatus
│   │   │   │   ├── value_objects/        ← Certification, MediaLinks, CollectionMembership, Ratings, CastMember
│   │   │   │   └── entities/             ← Person, Studio, Collection, Movie, User, UserGroup, UserGroupMembership, EventSeries, Event, EventMembership
│   │   │   ├── interfaces/
│   │   │   │   └── repositories.py       ← ABCs: UserRepository, UserGroupRepository, EventSeriesRepository, EventRepository, EventMembershipRepository
│   │   │   └── telemetry/
│   │   │       ├── setup.py          ← setup_telemetry(app, engine); wires OTel traces + metrics
│   │   │       ├── logging.py        ← configure_logging(); structlog JSON/console + OTel trace correlation
│   │   │       ├── metrics.py        ← module-level counters: events_created, votes_cast, users_registered, gen_ai_token_usage
│   │   │       └── ai_spans.py       ← gen_ai_span() context manager; GenAI OTel semantic conventions
│   │   └── infrastructure/
│   │       └── persistence/
│   │           ├── database.py           ← engine + SessionFactory (DATABASE_URL env var)
│   │           ├── encryption.py         ← Fernet encrypt/decrypt + email_hmac (DATABASE_ENCRYPTION_KEY env var)
│   │           ├── models/               ← SQLAlchemy ORM models (separate from domain entities)
│   │           └── sqlite/               ← concrete repository implementations
│   └── tests/
│       ├── unit/
│       │   ├── domain/               ← 298 unit tests (validators, value objects, entities)
│       │   └── telemetry/            ← logging config + GenAI span unit tests
│       └── integration/
│           ├── api/                  ← health/ready probes, request ID middleware, v1 ping
│           └── persistence/          ← repository tests using in-memory SQLite session fixture
└── frontend/                         ← placeholder, TBD
```

## Domain model — current state

### Validators (`domain/validators.py`)
- `validate_country_code(code, field_name)` → uppercase ISO 3166-1 alpha-2
- `validate_language_code(code, field_name)` → lowercase ISO 639-1 alpha-2

### Value objects (structural equality, `frozen=True`)

| Class | Key fields |
|---|---|
| `Certification` | `country` (ISO 3166-1), `rating` (e.g. "PG-13") |
| `MediaLinks` | `poster_url`, `trailer_url` (both `str \| None`, must be HTTPS) |
| `CollectionMembership` | `collection_id`, `collection_name`, `order \| None` |
| `Ratings` | `community_score \| None`, `vote_count \| None`, `certifications: tuple[Certification]` |
| `CastMember` | `person: Person`, `character_name` |

### Entities — media (immutable TMDB sources, `frozen=True, eq=False`)

| Class | Primary key | Notable fields |
|---|---|---|
| `Person` | `tmdb_id` | `name`, `nationalities`, `mother_tongue \| None`, `spoken_languages` |
| `Studio` | `tmdb_id` | `name`, `country \| None` |
| `Collection` | `collection_id` | `name` |
| `Movie` | `tmdb_id` | `title`, `synopsis`, `release_year`, `director: Person`, `cast`, `studios`, `media_links`, `ratings`, `original_language`, `collection_membership \| None` |

### Entities — platform (mutable, `eq=False`)

| Class | Primary key | Notable fields |
|---|---|---|
| `User` | `id` (UUID) | `firebase_uid`, `email` (encrypted), `system_role`, `anonymized_at` |
| `UserGroup` | `id` | `name`, `owner_id` |
| `UserGroupMembership` | `id` | `group_id`, `user_id`, `added_by` |
| `EventSeries` | `id` | `title`, `organiser_id`, `recurrence`, `voting_system` |
| `Event` | `id` | `title`, `activity_type`, `organiser_id`, `privacy`, `status`, `series_id \| None` |
| `EventMembership` | `id` | `event_id`, `user_id`, `role`, `status`, `invited_by` |
| `WishlistEntry` | `id` | `series_id`, `activity_type`, `tmdb_id`, `added_by`, `status`, `completed_event_id \| None` |
| `EventCandidate` | `id` | `event_id`, `wishlist_entry_id`, `added_by: UUID \| None` (None = system) |
| `EventBallot` | `id` | `event_id`, `user_id`, `round`, `payload: dict`, `superseded_at \| None` |

## Key design decisions

- **`tmdb_id` is the strict primary key** for all TMDB-sourced entities. No fallback to title+year. Fix ID issues at the source.
- **Immutable domain objects**: movies are loaded from TMDB and stored as-is; the app never mutates them.
- **`Person` is universal**: directors and actors are the same class. A director acting in their own film appears as the same `Person` instance in both `Movie.director` and a `CastMember` in `Movie.cast`.
- **`CollectionMembership` pattern**: a movie carries a lightweight value object describing its place in a collection, rather than holding a reference to a full `Collection` aggregate. Avoids circular dependencies. The same pattern will apply to TV Series and Game.
- **`Collection` is media-agnostic**: designed to group movies, TV series, and games within the same franchise. Cross-media franchises use internally managed IDs; TMDB movie collections map to `belongs_to_collection.id`.
- **`Ratings` holds both**: TMDB community score (`vote_average` + `vote_count`) and age certifications per country. `vote_count` requires `community_score` (they are always set together in TMDB data).
- **`mother_tongue` ≠ `spoken_languages`**: native language is a single optional field; additional languages spoken are a separate tuple.
- **Validators module**: shared helpers for ISO code validation to avoid duplicating logic across domain classes. Every class that stores a country or language code delegates to these.
- **Wishlist is series-level, ballot is event-level**: `WishlistEntry` belongs to `EventSeries` (the full pool). For each `Event`, an organiser (or future algorithm) picks a shortlist via `EventCandidate` rows. Members then vote only on those candidates.
- **`WishlistEntry` status filter**: COMPLETED rows are kept for history (prevents re-adding recently watched content); REMOVED rows are excluded from the active view. A partial unique index `UNIQUE (series_id, activity_type, tmdb_id) WHERE status != 'COMPLETED'` prevents duplicates on the active list while allowing re-nomination after completion.
- **`EventBallot` is append-only**: revisions create a new row and supersede the previous one (`superseded_at` timestamp). Current ballot = `WHERE superseded_at IS NULL`. Partial unique index `UNIQUE (event_id, user_id, round) WHERE superseded_at IS NULL` enforces exactly one active ballot per member per round.
- **`EventBallot.payload` is a JSONB dict**: structure varies by `VotingSystem` on the parent `EventSeries`. Approval: `{"approved": [...candidate_uuids]}`. Ranked choice: `{"rankings": [...candidate_uuids]}`. Two-round runoff: `{"pick": "candidate_uuid"}` with `round` field incrementing per round.
- **`EventCandidate.added_by` is nullable**: `None` means the system auto-selected the candidate; a UUID means an organiser or co-organiser made the pick manually. The mechanism for auto-selection is a future feature.
- **`VotingSystem` lives on `EventSeries`**: all events in a series share the same voting algorithm. Defaults to `APPROVAL`.

## Authentication & identity

- **Provider**: Firebase Authentication with Google Sign-In. Free to 10k MAU, works on web + Android + iOS. No own registration form for now — add email/password as a second Firebase provider later if needed, zero rework.
- **Backend flow**: frontend exchanges Google credential for a Firebase JWT; every backend request verifies the JWT using Firebase's public keys. Backend then issues its own session token (HttpOnly, Secure, SameSite=Strict cookie).
- **User primary key**: Firebase `uid` — never email. Emails can change and must not be used as identity.
- **Token storage**: access token in JS memory only (never localStorage/sessionStorage). Session token in HttpOnly cookie. Mobile: Android Keystore / iOS Keychain.
- **Security non-negotiables** (pen test targets):
  - Always verify JWT signature server-side; never trust unverified tokens
  - Validate `state` parameter in OAuth flow (prevents OAuth CSRF)
  - Mobile OAuth callback via Universal Links / App Links only (not custom URL schemes)
  - Revoke Firebase token server-side on logout
  - Rate-limit all auth endpoints
  - Log all auth events (login, failure, logout, revocation)
  - Short-lived access tokens (Firebase default 1h — keep it)

## Persistence

- **Dev**: SQLite via SQLAlchemy (zero setup, single file, functionally identical queries to Postgres)
- **Prod (AKS)**: Azure Database for PostgreSQL Flexible Server, Burstable B1ms SKU (~$12–15/month)
- **ORM**: SQLAlchemy — same models for both, connection string is the only change
- **Migrations**: Alembic
- **Encryption at rest**:
  - Transparent disk encryption: Azure PostgreSQL default AES-256 (covers physical data at rest)
  - PII fields (email): application-level encryption, key in Azure Key Vault (prod) / env var (dev). Key never in code or DB.
  - Email lookup: store an HMAC of the email alongside the encrypted value for indexed lookups
- **Privacy by design**: store minimum personal data; `User` must support anonymisation (right to erasure / GDPR)
- **Repository pattern**: `core/interfaces/repositories.py` holds ABCs; `infrastructure/persistence/sqlite/` and `infrastructure/persistence/postgres/` hold concrete implementations. Service layer depends only on interfaces.
- **Preferences**: stored as JSONB on `User` for now. Migration path to normalised table: dual-write via Alembic, cut over, drop column — no service-layer changes needed.

### Schema

```
── Users ──────────────────────────────────────────────────────────────
User
  id                  UUID PK
  firebase_uid        str  unique, immutable
  email               bytes (AES-256 encrypted)
  email_hash          bytes (HMAC, unique index — enables lookup without decrypting)
  nickname            str | None
  avatar_url          str | None  (HTTPS only)
  system_role         SystemRole        MEMBER | ADMIN
  gender              str | None
  pronouns            str | None
  bio                 str | None
  preferences         JSONB | None      (media/game preferences, normalise later if needed)
  created_at          timestamptz
  updated_at          timestamptz
  anonymized_at       timestamptz | None   (GDPR right to erasure — null PII, keep row)

── Preset groups ──────────────────────────────────────────────────────
UserGroup
  id                  UUID PK
  name                str
  description         str | None
  owner_id            UUID → User
  created_at          timestamptz
  updated_at          timestamptz

UserGroupMembership
  id                  UUID PK
  group_id            UUID → UserGroup
  user_id             UUID → User
  added_by            UUID → User
  added_at            timestamptz

── Events ─────────────────────────────────────────────────────────────
EventSeries             ← scheduling/grouping container only, no activity_type
  id                  UUID PK
  title               str              (e.g. "MCU Marathon", "Tuesday Games Night")
  description         str | None
  organiser_id        UUID → User
  recurrence          RecurrenceType   WEEKLY | BIWEEKLY | MONTHLY | CUSTOM
  created_at          timestamptz
  updated_at          timestamptz

Event
  id                  UUID PK
  series_id           UUID → EventSeries | None   (null = one-off event)
  series_sequence     int | None
  title               str
  description         str | None
  activity_type       ActivityType     MOVIE | TV_SERIES | VIDEO_GAME | TABLETOP_GAME
  organiser_id        UUID → User      (immutable after creation)
  privacy             EventPrivacy     PUBLIC | PRIVATE
  status              EventStatus      OPEN | VOTING | COMPLETED | CANCELLED
  scheduled_at        timestamptz | None
  created_at          timestamptz
  updated_at          timestamptz

EventMembership
  id                  UUID PK
  event_id            UUID → Event
  user_id             UUID → User
  role                EventRole        CO_ORGANISER | PARTICIPANT
  status              MembershipStatus INVITED | PENDING_APPROVAL | ACCEPTED | DECLINED
  invited_by          UUID → User
  invited_via_group_id UUID → UserGroup | None    (audit trail for bulk group invites)
  invited_at          timestamptz
  responded_at        timestamptz | None
```

### Key design decisions — persistence

- **`EventSeries` has no `activity_type`**: it is a scheduling/grouping container only. Individual events carry their own type independently — a series can mix movies, series, games (e.g. MCU marathon spanning films and Disney+ shows).
- **Event instances are created ad-hoc**, not pre-generated. Organiser (or app prompt) creates the next session manually. Avoids orphaned future events if a series ends.
- **`organiser_id` lives on `Event`**, not in `EventMembership`. Prevents accidental self-removal. The organiser is not duplicated into `EventMembership`.
- **`invited_via_group_id`** on `EventMembership` preserves the audit trail when a whole group is invited at once. When a group is used to invite, the service fans out one `EventMembership` row per group member, each carrying the group ID.
- **System role vs event role are independent**: `User.system_role` (ADMIN/MEMBER) controls platform-level access; `EventMembership.role` controls per-event access. An ADMIN has no implicit power inside someone else's event.

## API layer

### Endpoints defined

| Method | Path | Auth | Purpose |
|---|---|---|---|
| `GET` | `/health` | none | Liveness probe — always 200 |
| `GET` | `/ready` | none | Readiness probe — checks DB, 503 if down |
| `GET` | `/api/v1/ping` | none | Sanity check — returns `{"message": "pong"}` |

Docs auto-generated at `/api/docs` (Swagger) and `/api/redoc`.

### Key design decisions — API

- **`RequestIDMiddleware`**: injects a `x-request-id` UUID on every request/response for log correlation. If the caller supplies `X-Request-ID`, it is echoed back unchanged.
- **`get_current_user` is a stub** (raises 501): Firebase JWT verification is the next piece to implement. Depends on Firebase Admin SDK. See `app/api/v1/dependencies.py`.
- **`Depends()` in function signatures** is the FastAPI idiom. Ruff B008 is suppressed with `# noqa: B008` on those lines — do not remove those comments.
- **`OTEL_SDK_DISABLED=true` in integration tests**: The SDK `TracerProvider.__init__` caches this flag at construction time. The `otel_exporter` fixture in `tests/unit/telemetry/test_ai_spans.py` therefore removes the env var **before** creating the `TracerProvider` and restores it after the test.

## TV Series and Game — planned

These are coming. When they arrive:
- Follow the same pattern: frozen dataclass entity, `tmdb_id` primary key, `CollectionMembership` for franchise links.
- A `Votable` protocol or `MediaItem` ABC will be introduced to let the voting service remain media-agnostic.

## Local environment notes

- **SSL certificates**: this machine has a corporate/custom cert chain. Fix applied:
  - Git: `git config --global http.sslBackend schannel`
  - pip: use `--trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org`
- **Running the dev server**: `cd backend && uvicorn app.main:app --reload` (requires `DATABASE_URL` and `DATABASE_ENCRYPTION_KEY` env vars)
- **Building docs locally**: `sphinx-apidoc --output-dir docs/api --force --module-first --separate backend/app && sphinx-build -W -b html docs docs/_build/html` (from repo root; install `docs/requirements.txt` first)
- **Docs CI actions (IDE errors)**: the IDE flags `actions/checkout@v4` etc. as unresolvable — corporate SSL issue, same as pip/git. The workflow is correct; the same actions are used in `backend-ci.yml`.
- **Running tests locally**: `cd backend && python -m pytest`
- **Installing dev deps**: `cd backend && pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org pytest pytest-cov`
- **`gh` CLI location**: `C:\Program Files\GitHub CLI\gh.exe` (not on bash PATH by default)
- **Running integration tests**: `cd backend && python -m pytest tests/integration/`
- **Resetting dev DB**: `cd backend && python scripts/reset_dev_db.py`
- **Generating a Fernet key**: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
- **Integration test encryption key**: fixed test value set in `tests/integration/conftest.py` via `os.environ.setdefault`
