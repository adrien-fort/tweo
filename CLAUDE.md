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
- **Frontend**: TBD — React is the leading candidate
- **CI**: GitHub Actions (`.github/workflows/backend-ci.yml`)
- **Repo**: https://github.com/adrien-fort/tweo

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
├── .github/workflows/backend-ci.yml  ← lint, typecheck, pytest (runs from backend/)
├── backend/
│   ├── pyproject.toml                ← setuptools.build_meta, dev deps, pytest/ruff/mypy config
│   ├── app/
│   │   └── core/
│   │       └── domain/
│   │           ├── validators.py         ← shared validate_country_code / validate_language_code
│   │           ├── value_objects/        ← Certification, MediaLinks, CollectionMembership, Ratings, CastMember
│   │           └── entities/             ← Person, Studio, Collection, Movie
│   └── tests/
│       └── unit/domain/
│           ├── test_validators.py
│           ├── value_objects/
│           └── entities/
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

### Entities (identity-based equality by ID, `frozen=True, eq=False`)

| Class | Primary key | Notable fields |
|---|---|---|
| `Person` | `tmdb_id` | `name`, `nationalities`, `mother_tongue \| None`, `spoken_languages` |
| `Studio` | `tmdb_id` | `name`, `country \| None` |
| `Collection` | `collection_id` | `name` |
| `Movie` | `tmdb_id` | `title`, `synopsis`, `release_year`, `director: Person`, `cast`, `studios`, `media_links`, `ratings`, `original_language`, `collection_membership \| None` |

## Key design decisions

- **`tmdb_id` is the strict primary key** for all TMDB-sourced entities. No fallback to title+year. Fix ID issues at the source.
- **Immutable domain objects**: movies are loaded from TMDB and stored as-is; the app never mutates them.
- **`Person` is universal**: directors and actors are the same class. A director acting in their own film appears as the same `Person` instance in both `Movie.director` and a `CastMember` in `Movie.cast`.
- **`CollectionMembership` pattern**: a movie carries a lightweight value object describing its place in a collection, rather than holding a reference to a full `Collection` aggregate. Avoids circular dependencies. The same pattern will apply to TV Series and Game.
- **`Collection` is media-agnostic**: designed to group movies, TV series, and games within the same franchise. Cross-media franchises use internally managed IDs; TMDB movie collections map to `belongs_to_collection.id`.
- **`Ratings` holds both**: TMDB community score (`vote_average` + `vote_count`) and age certifications per country. `vote_count` requires `community_score` (they are always set together in TMDB data).
- **`mother_tongue` ≠ `spoken_languages`**: native language is a single optional field; additional languages spoken are a separate tuple.
- **Validators module**: shared helpers for ISO code validation to avoid duplicating logic across domain classes. Every class that stores a country or language code delegates to these.

## TV Series and Game — planned

These are coming. When they arrive:
- Follow the same pattern: frozen dataclass entity, `tmdb_id` primary key, `CollectionMembership` for franchise links.
- A `Votable` protocol or `MediaItem` ABC will be introduced to let the voting service remain media-agnostic.

## Local environment notes

- **SSL certificates**: this machine has a corporate/custom cert chain. Fix applied:
  - Git: `git config --global http.sslBackend schannel`
  - pip: use `--trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org`
- **Running tests locally**: `cd backend && python -m pytest`
- **Installing dev deps**: `cd backend && pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org pytest pytest-cov`
- **`gh` CLI location**: `C:\Program Files\GitHub CLI\gh.exe` (not on bash PATH by default)
