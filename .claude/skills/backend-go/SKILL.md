---
name: backend-go
description: Go backend development patterns for the Breeze Airways operations-back-end service. Enforces hexagonal architecture, layered dependency rules, adapter patterns, and project conventions. Use when writing or modifying Go code in the operations backend.
---

# Go Backend Skill — Operations Back End

Patterns and conventions for the Breeze Airways `operations-back-end` Go service. This service provides flight operations data via GraphQL — load sheets, manifests, flight tracking, and crew operations.

## Architecture Overview

Hexagonal architecture (Ports & Adapters) with four layers. **Imports flow downward only.**

```
API Layer (Resolvers) → Service Layer → Adapter Layer → Client Layer → External Systems
```

| Layer | Responsibility | Can Import |
|-------|---------------|------------|
| **API** (Resolvers) | Request handling, DTO mapping, error translation | Services only (via `platform` interfaces) |
| **Services** | Business logic, orchestration | Adapters only |
| **Adapters** | External system translation, model conversion, caching | Clients only |
| **Clients** | Protocol implementation (HTTP, SQL, GraphQL, Redis) | Infrastructure/libraries |

**Key Rule:** No layer may import from a layer above it. Resolvers never import adapters. Services never import clients directly.

## Directory Structure

```
operations-back-end/
├── api/
│   ├── graphql/
│   │   ├── context/              # Request context, auth info
│   │   ├── models/               # GraphQL DTOs (response models)
│   │   ├── resolver/             # Resolvers organized by domain
│   │   │   ├── resolver.go       # Root resolver (composes sub-resolvers)
│   │   │   ├── flight/
│   │   │   ├── flight_line/
│   │   │   ├── load_sheet/
│   │   │   └── manifest/
│   │   └── schema/               # GraphQL type definitions
│   ├── handler/                  # HTTP handlers (GraphQL endpoint setup)
│   └── middleware/               # Auth, CORS, logging
├── cmd/
│   ├── app/                      # Main web server entry point
│   │   ├── main.go               # Bootstrap & wiring
│   │   └── config/               # Viper configuration
│   ├── poller/                   # Flight/manifest pollers
│   └── scripts/                  # One-off scripts
├── internal/
│   ├── clients/                  # External system clients
│   │   ├── aerodata/             # HTTP/REST client
│   │   ├── graphql/
│   │   │   ├── navblue/          # genqlient GraphQL client
│   │   │   └── navitaire/        # genqlient GraphQL client
│   │   ├── operations_db/        # PostgreSQL (sqlx + pgx)
│   │   │   ├── operations_db.go  # Interface + connection setup
│   │   │   ├── flight.go         # Flight queries
│   │   │   ├── models/           # DB row structs
│   │   │   ├── queries/          # Embedded SQL files
│   │   │   ├── migrations/       # Atlas migrations
│   │   │   └── mocks/            # Generated mocks
│   │   ├── redis/
│   │   └── warpstream/           # Event streaming (Kafka-compatible)
│   ├── platform/                 # Service interfaces + registry
│   │   ├── registry.go           # ServiceRegistry (DI container)
│   │   ├── service_load_sheet.go # LoadSheetService interface
│   │   ├── service_manifest.go   # ManifestService interface
│   │   ├── mocks/                # Generated service mocks
│   │   └── load_sheet/models/    # Domain models
│   └── services/                 # Business logic implementations
│       ├── load_sheet/
│       │   ├── service.go        # Service struct + constructor
│       │   ├── adapters/
│       │   │   ├── db/           # DB adapter (port implementation)
│       │   │   ├── navitaire/    # Navitaire adapter
│       │   │   └── aerodata/     # Aerodata adapter
│       │   └── models/           # (alias to platform models)
│       ├── manifest/
│       ├── flight/
│       ├── flight_line/
│       └── ssr/
└── specs/                        # Architecture & design docs
```

## Core Patterns

### 1. Service Pattern

Services own business logic and compose adapters. Define the service interface in `internal/platform/`, implement in `internal/services/<domain>/`.

**Interface definition** (`internal/platform/service_<domain>.go`):

```go
package platform

//go:generate mockgen -destination=mocks/mock_<domain>_service.go -package=mocks operations-back-end/internal/platform <Domain>Service
type <Domain>Service interface {
    ServiceRegistrant
    // Domain-specific method groups (compose smaller interfaces)
    GetSomething(ctx context.Context, id models.SomeID) (*models.Something, error)
}
```

**Implementation** (`internal/services/<domain>/service.go`):

```go
package <domain>

type service struct {
    dbAdapter        db.DB
    navitaireAdapter navitaire.Adapter
    aerodataAdapter  aerodata.Adapter
    registry         platform.ServiceRegistry
    growthBookClient growthbook.Client
}

type ServiceConfig struct {
    DB               operations_db.OperationsDB
    NavitaireClient  navitaireClient.Client
    AerodataClient   aerodataClient.Client
    GrowthBookClient growthbook.Client
}

func NewService(config ServiceConfig) *service {
    dbAdapter := db.NewDB(db.DBConfig{DB: config.DB})
    navitaireAdapter := navitaire.NewAdapter(navitaire.AdapterConfig{
        NavitaireClient: config.NavitaireClient,
    })
    return &service{
        dbAdapter:        dbAdapter,
        navitaireAdapter: navitaireAdapter,
    }
}

func (s *service) Register(registry platform.ServiceRegistry) error {
    s.registry = registry
    return nil
}
```

**Rules:**
- Services depend on **adapter interfaces**, never on clients directly
- The constructor creates adapters internally — callers pass raw clients via `ServiceConfig`
- Services access other services only through `platform.ServiceRegistry`

### 2. Adapter Pattern

Adapters translate between domain models and external schemas. Each adapter defines a port interface with a `//go:generate mockgen` directive.

**Port interface + implementation** (`internal/services/<domain>/adapters/<provider>/adapter.go`):

```go
package <provider>

//go:generate mockgen -package=mocks -destination=mocks/mock_adapter.go operations-back-end/internal/services/<domain>/adapters/<provider> Adapter
type Adapter interface {
    GetSomething(ctx context.Context, id models.SomeID) (*models.Something, error)
}

type adapter struct {
    client <provider_client>.Client
}

type AdapterConfig struct {
    <Provider>Client <provider_client>.Client
}

func NewAdapter(config AdapterConfig) *adapter {
    return &adapter{client: config.<Provider>Client}
}
```

**DB adapter** (`internal/services/<domain>/adapters/db/db.go`):

```go
package db

//go:generate mockgen -package=mocks -destination=mocks/mock_db.go operations-back-end/internal/services/<domain>/adapters/db DB
type DB interface {
    // Compose sub-interfaces by domain concern
    FlightAdapter
    LoadSheetAdapter
}

type db struct {
    db operations_db.OperationsDB
}

type DBConfig struct {
    DB operations_db.OperationsDB
}

func NewDB(config DBConfig) DB {
    return &db{db: config.DB}
}
```

**Adapter methods convert models between layers:**

```go
func (d *db) GetFlights(ctx context.Context, filter models.FlightFilter) ([]models.Flight, error) {
    // Convert service filter → DB filter
    dbFilter := dbModels.FlightFilter{
        Status: filter.Status,
        StartDate: filter.StartDate,
    }
    dbFlights, err := d.db.GetFlights(ctx, dbFilter)
    if err != nil {
        return nil, fmt.Errorf("failed to get flights: %w", err)
    }
    // Convert DB models → service models
    flights := make([]models.Flight, len(dbFlights))
    for i, f := range dbFlights {
        flights[i] = *convertToServiceFlight(&f)
    }
    return flights, nil
}
```

### 3. Database Client Pattern

The PostgreSQL client uses **sqlx + pgx** with embedded SQL queries.

**Client interface** (`internal/clients/operations_db/operations_db.go`):

```go
//go:generate mockgen -package=mocks -destination=mocks/mock_operations_db.go operations-back-end/internal/clients/operations_db OperationsDB
type OperationsDB interface {
    // Compose domain-specific sub-interfaces
    Flight
    LoadSheet
    CargoItemDB
    Close() error
}
```

**Query files** use `//go:embed` for SQL:

```go
//go:embed queries/flight/get_flight_by_id.sql
var getFlightByIDQuery string

func (d *operationsdb) GetFlightByID(ctx context.Context, id int64) (*dbModels.Flight, error) {
    flight := dbModels.Flight{}
    err := d.db.GetContext(ctx, &flight, getFlightByIDQuery, id)
    if err != nil {
        return nil, err
    }
    return &flight, nil
}
```

**Conventions:**
- Use `GetContext`/`SelectContext` (context-aware sqlx methods)
- SQL files live in `queries/<domain>/` subdirectories
- DB models use `db` struct tags for sqlx scanning
- Dynamic queries use query builder functions in the `queries/` package

### 4. GraphQL Resolver Pattern

The root resolver composes domain-specific sub-resolvers via struct embedding.

**Root resolver** (`api/graphql/resolver/resolver.go`):

```go
type Resolver struct {
    *loadSheetResolver.LoadSheetResolver
    *manifestResolver.ManifestResolver
    *flightResolver.FlightResolver
}

type Config struct {
    LoadSheetService  platform.LoadSheetService
    ManifestService   platform.ManifestService
    FlightService     platform.FlightService
}

func NewResolver(config Config) *Resolver {
    return &Resolver{
        LoadSheetResolver: loadSheetResolver.NewResolver(loadSheetResolver.ResolverConfig{
            LoadSheetService: config.LoadSheetService,
        }),
        // ...
    }
}
```

**Domain resolver** (`api/graphql/resolver/<domain>/resolver.go`):

```go
type LoadSheetResolver struct {
    loadSheet platform.LoadSheetService
}
```

**Resolver methods** convert between GraphQL models and service calls:

```go
func (r *LoadSheetResolver) GetFlights(ctx context.Context, status string, date string) ([]graphqlModels.Flight, error) {
    sctx, span := logger.Tracer.Start(ctx, "GetFlights")
    defer span.End()

    // Validate/parse input
    // Call service
    flights, err := r.loadSheet.GetFlights(sctx, filter)
    if err != nil {
        return nil, err
    }
    // Convert service models → GraphQL models
    result := make([]graphqlModels.Flight, len(flights))
    for i, f := range flights {
        result[i] = graphqlModels.ConvertToFlight(f)
    }
    return result, nil
}
```

**Rules:**
- Resolvers only call service interfaces from `platform`
- Every resolver method starts a tracing span
- Input validation and date parsing happens in the resolver
- Model conversion to GraphQL DTOs happens in the resolver

### 5. Service Registry

The registry enables inter-service communication without circular imports.

```go
// internal/platform/registry.go
type ServiceRegistry interface {
    LoadSheetService() LoadSheetService
    ManifestService() ManifestService
    SSRService() SSRService
    FlightLineService() FlightLineService
    FlightService() FlightService
}

type ServiceRegistrant interface {
    Register(registry ServiceRegistry) error
}
```

**Bootstrap in main.go:**

```go
registry := platform.NewServiceRegistry(platform.ServiceRegistryConfig{
    LoadSheetService:  loadSheetService,
    ManifestService:   manifestService,
    SSRService:        ssrService,
})
loadSheetService.Register(registry)
manifestService.Register(registry)
```

Services call each other via `s.registry.ManifestService().GetManifest(...)`.

## Model Layers

Three distinct model types — never pass models across layer boundaries without conversion.

| Layer | Package | Example |
|-------|---------|---------|
| **DB models** | `internal/clients/operations_db/models` | `dbModels.Flight` |
| **Domain/Service models** | `internal/platform/<domain>/models` | `models.Flight` |
| **GraphQL models** | `api/graphql/models` | `graphqlModels.Flight` |

**Import aliases** for clarity:

```go
import (
    dbModels      "operations-back-end/internal/clients/operations_db/models"
    serviceModels "operations-back-end/internal/platform/load_sheet/models"
    graphqlModels "operations-back-end/api/graphql/models"
)
```

**Converter naming:** `ConvertToFlight()`, `convertToServiceFlight()`, `PtrToFlight()`

## Error Handling

Errors flow upward with wrapping at each layer:

| Layer | Pattern |
|-------|---------|
| **Clients** | Return raw errors with context |
| **Adapters** | Wrap with `fmt.Errorf("...: %w", err)`, translate to domain errors |
| **Services** | Handle business logic errors, propagate wrapped errors |
| **Resolvers** | Translate to safe GraphQL error responses |

**Domain errors** (`internal/services/<domain>/adapters/<provider>/errors.go`):

```go
var (
    ErrNotFound              = errors.New("not found")
    ErrInvalidInput          = errors.New("invalid input")
    ErrDuplicateBagTag       = errors.New("duplicate bag tag")
    ErrDependencyUnavailable = errors.New("dependency unavailable")
)
```

## Testing

### Test Pyramid

| Level | Scope | Mocking |
|-------|-------|---------|
| Unit | Services with mocked adapters | GoMock |
| Unit | Adapters with mocked clients | GoMock |
| Unit | Resolvers with mocked services | GoMock |
| Integration | Adapters with real DB | Docker (Postgres) |

### Mock Generation

Place `//go:generate mockgen` directives above interfaces. Run `make generate` to regenerate.

### Test Pattern

```go
func TestSomething(t *testing.T) {
    ctrl := gomock.NewController(t)
    defer ctrl.Finish()

    mockDB := mocks.NewMockOperationsDB(ctrl)
    dbAdapter := db.NewDB(db.DBConfig{DB: mockDB})

    // Set up expectations
    mockDB.EXPECT().
        GetFlightByID(gomock.Any(), int64(123)).
        Return(&dbModels.Flight{ID: 123}, nil)

    // Call the adapter
    result, err := dbAdapter.GetFlightByID(context.Background(), models.FlightID(123))

    // Assert
    assert.NoError(t, err)
    assert.Equal(t, models.FlightID(123), result.ID)
}
```

**Testing libraries:** `testify/assert`, `testify/require`, `go.uber.org/mock/gomock`

Use table-driven tests for multiple scenarios:

```go
tests := []struct {
    name     string
    input    InputType
    expected OutputType
    wantErr  bool
}{
    {"valid case", validInput, expectedOutput, false},
    {"error case", badInput, nil, true},
}
for _, tt := range tests {
    t.Run(tt.name, func(t *testing.T) { ... })
}
```

## Configuration

- Loaded via **Viper** from `.env` (local) or environment variables (production)
- Parsed once at startup into a typed `config.Config` struct
- **No `os.Getenv` calls in packages** — all config injected via constructors

## Naming Conventions

| Thing | Convention | Example |
|-------|-----------|---------|
| Service interfaces | `<Domain>Service` | `LoadSheetService` |
| Adapter interfaces | `Adapter` or `DB` | `navitaire.Adapter`, `db.DB` |
| Client interfaces | `<Provider>DB` or `Client` | `OperationsDB`, `navitaire.Client` |
| Config structs | `<Type>Config` | `ServiceConfig`, `DBConfig`, `AdapterConfig` |
| Constructors | `New<Type>(config)` | `NewService(config)`, `NewAdapter(config)` |
| Domain IDs | `<Entity>ID` type alias | `type FlightID int64` |
| Packages | `snake_case` | `load_sheet`, `flight_line`, `operations_db` |
| Files | `snake_case.go` | `service.go`, `flight_resolver.go` |
| Mock output | `mocks/mock_<name>.go` | `mocks/mock_adapter.go` |

## Observability

- **Tracing:** OpenTelemetry spans in resolvers and key service methods
  ```go
  sctx, span := logger.Tracer.Start(ctx, "MethodName")
  defer span.End()
  ```
- **Logging:** `log/slog` with structured fields
  ```go
  slog.InfoContext(ctx, "message", "key", value)
  slog.ErrorContext(ctx, "failed to do thing", "error", err)
  ```
- **Telemetry:** New Relic integration via `logger.InitializeTelemetry`

## Adding a New Feature Checklist

When adding a new domain feature (e.g., a new query or mutation):

1. **Domain models** — Add/update in `internal/platform/<domain>/models/`
2. **DB layer** (if needed):
   - Add SQL in `internal/clients/operations_db/queries/<domain>/`
   - Add method to client interface + implementation in `internal/clients/operations_db/`
   - Add DB model in `internal/clients/operations_db/models/`
3. **Adapter** — Add method to adapter interface + implementation in `internal/services/<domain>/adapters/`
4. **Service** — Add method to service interface in `internal/platform/service_<domain>.go`, implement in `internal/services/<domain>/`
5. **GraphQL schema** — Add types/queries/mutations in `api/graphql/schema/`
6. **GraphQL models** — Add DTOs + converters in `api/graphql/models/`
7. **Resolver** — Add resolver method in `api/graphql/resolver/<domain>/`
8. **Tests** — Unit tests at adapter and service layers with mocks
9. **Regenerate mocks** — `make generate`

## External Integrations

| System | Protocol | Client Location |
|--------|----------|-----------------|
| PostgreSQL | sqlx + pgx | `internal/clients/operations_db/` |
| Navitaire | GraphQL (genqlient) | `internal/clients/graphql/navitaire/` |
| Navblue | GraphQL (genqlient) | `internal/clients/graphql/navblue/` |
| Aerodata | HTTP/REST | `internal/clients/aerodata/` |
| Redis | go-redis | `internal/clients/redis/` |
| WarpStream | Kafka-compatible | `internal/clients/warpstream/` |
| GrowthBook | Feature flags | `internal/clients/growthbook/` |
| S3 | AWS SDK | `internal/clients/s3/` |
