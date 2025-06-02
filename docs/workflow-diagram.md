# Talisik Short URL - Workflow Diagrams

This document contains visual representations of how the Talisik Short URL system works, showing the complete workflows for URL shortening and expansion operations.

## Overview Workflow

```mermaid
graph TD
    A[User Input] --> B{Operation Type}
    B -->|Shorten URL| C[URL Shortening Flow]
    B -->|Expand Code| D[URL Expansion Flow]
    C --> E[Short URL Response]
    D --> F[Original URL Response]

    style A fill:#e1f5fe
    style E fill:#c8e6c9
    style F fill:#c8e6c9
```

## URL Shortening Workflow

```mermaid
flowchart TD
    Start([User Requests URL Shortening]) --> Input[Input: URL + Optional Custom Code + Optional Expiration]
    Input --> Validate{Validate URL}

    Validate -->|Invalid| Error1[Return: Validation Error]
    Validate -->|Valid| CheckCustom{Custom Code Provided?}

    CheckCustom -->|No| Generate[Generate Random 7-char Code]
    CheckCustom -->|Yes| ValidateCustom{Validate Custom Code Format}

    ValidateCustom -->|Invalid| Error2[Return: Invalid Custom Code Error]
    ValidateCustom -->|Valid| UseCustom[Use Custom Code]

    Generate --> CheckConflict{Code Already Exists?}
    UseCustom --> CheckConflict

    CheckConflict -->|Yes| Error3[Return: Conflict Error]
    CheckConflict -->|No| CreateEntity[Create ShortURL Entity]

    CreateEntity --> SetExpiration{Expiration Hours Set?}
    SetExpiration -->|Yes| CalcExpiry[Calculate Expiration Time]
    SetExpiration -->|No| NoExpiry[Set Expiration = None]

    CalcExpiry --> Store[Store in Backend]
    NoExpiry --> Store

    Store --> BuildResponse[Build Response with Short URL]
    BuildResponse --> Success([Return ShortenResponse])

    Error1 --> End([End])
    Error2 --> End
    Error3 --> End
    Success --> End

    style Start fill:#e3f2fd
    style Success fill:#c8e6c9
    style Error1 fill:#ffcdd2
    style Error2 fill:#ffcdd2
    style Error3 fill:#ffcdd2
    style End fill:#f5f5f5
```

## URL Expansion Workflow

```mermaid
flowchart TD
    Start([User Requests URL Expansion]) --> Input[Input: Short Code]
    Input --> Lookup[Look up Short Code in Storage]

    Lookup --> Found{Short URL Found?}
    Found -->|No| NotFound[Return: None]

    Found -->|Yes| CheckExpiry{Check Expiration}
    CheckExpiry -->|Expired| Expired[Return: None - Expired]
    CheckExpiry -->|Not Expired/No Expiry| CheckActive{Check if Active}

    CheckActive -->|Inactive| Inactive[Return: None - Inactive]
    CheckActive -->|Active| UpdateAnalytics[Increment Click Count]

    UpdateAnalytics --> ReturnURL[Return Original URL]
    ReturnURL --> Success([Successful Expansion])

    NotFound --> End([End])
    Expired --> End
    Inactive --> End
    Success --> End

    style Start fill:#e3f2fd
    style Success fill:#c8e6c9
    style NotFound fill:#fff3e0
    style Expired fill:#fff3e0
    style Inactive fill:#fff3e0
    style End fill:#f5f5f5
```

## Complete System Data Flow

```mermaid
sequenceDiagram
    participant User
    participant URLShortener
    participant Validator
    participant CodeGenerator
    participant Storage
    participant Analytics

    Note over User,Analytics: URL Shortening Process
    User->>URLShortener: shorten(ShortenRequest)
    URLShortener->>Validator: validate_url(url)
    Validator-->>URLShortener: validation_result

    alt URL is invalid
        URLShortener-->>User: ValueError: Invalid URL
    else URL is valid
        alt Custom code provided
            URLShortener->>Validator: validate_custom_code(code)
            Validator-->>URLShortener: validation_result
            alt Custom code invalid
                URLShortener-->>User: ValueError: Invalid custom code
            end
        else No custom code
            URLShortener->>CodeGenerator: generate_random_code()
            CodeGenerator-->>URLShortener: short_code
        end

        URLShortener->>Storage: check_conflict(short_code)
        Storage-->>URLShortener: conflict_status

        alt Conflict exists
            URLShortener-->>User: ValueError: Code already exists
        else No conflict
            URLShortener->>Storage: store(short_code, short_url_obj)
            Storage-->>URLShortener: success
            URLShortener-->>User: ShortenResponse
        end
    end

    Note over User,Analytics: URL Expansion Process
    User->>URLShortener: expand(short_code)
    URLShortener->>Storage: get(short_code)
    Storage-->>URLShortener: short_url_obj

    alt URL not found
        URLShortener-->>User: None
    else URL found
        URLShortener->>URLShortener: check_expiration()
        alt URL expired
            URLShortener-->>User: None
        else URL valid
            URLShortener->>URLShortener: check_active_status()
            alt URL inactive
                URLShortener-->>User: None
            else URL active
                URLShortener->>Analytics: increment_click_count()
                Analytics-->>URLShortener: updated
                URLShortener-->>User: original_url
            end
        end
    end
```

## Storage Backend Architecture Flow

```mermaid
graph TB
    subgraph "Current Implementation"
        A[URLShortener] --> B[In-Memory Dict]
        B --> C[dict[str, ShortURL]]
    end

    subgraph "Planned Architecture"
        D[URLShortener] --> E[AbstractStorage Interface]
        E --> F[MemoryStorage]
        E --> G[SQLiteStorage]
        E --> H[RedisStorage]

        F --> I[dict[str, ShortURL]]
        G --> J[SQLite Database]
        H --> K[Redis Server]
    end

    subgraph "Storage Operations"
        L[get(short_code)] --> M{Storage Type}
        M -->|Memory| N[Dictionary Lookup O(1)]
        M -->|SQLite| O[SQL SELECT Query]
        M -->|Redis| P[Redis GET Command]

        Q[set(short_code, url)] --> R{Storage Type}
        R -->|Memory| S[Dictionary Insert O(1)]
        R -->|SQLite| T[SQL INSERT Query]
        R -->|Redis| U[Redis SET Command]
    end

    style A fill:#e1f5fe
    style D fill:#e1f5fe
    style E fill:#f3e5f5
    style I fill:#c8e6c9
    style J fill:#c8e6c9
    style K fill:#c8e6c9
```

## Error Handling Flow

```mermaid
flowchart TD
    Operation[URL Operation] --> TryBlock{Try Operation}
    TryBlock -->|Success| Success[Return Result]
    TryBlock -->|Exception| CatchBlock{Exception Type}

    CatchBlock -->|ValidationError| Log1[Log Warning: Validation Failed]
    CatchBlock -->|ConflictError| Log2[Log Info: Code Conflict]
    CatchBlock -->|StorageError| Log3[Log Error: Storage Issue]
    CatchBlock -->|Unexpected Error| Log4[Log Error: Unexpected]

    Log1 --> Reraise1[Re-raise ValidationError]
    Log2 --> Reraise2[Re-raise ConflictError]
    Log3 --> Reraise3[Re-raise StorageError]
    Log4 --> Convert[Convert to StorageError]

    Reraise1 --> UserError[Return Error to User]
    Reraise2 --> UserError
    Reraise3 --> UserError
    Convert --> UserError

    Success --> End([End])
    UserError --> End

    style Success fill:#c8e6c9
    style UserError fill:#ffcdd2
    style End fill:#f5f5f5
```

## Performance and Caching Strategy (Planned)

```mermaid
graph TD
    Request[Incoming Request] --> L1{L1 Cache Check}
    L1 -->|Hit| FastResponse[Return from Memory <1ms]
    L1 -->|Miss| L2{L2 Cache Check}

    L2 -->|Hit| MediumResponse[Return from Redis <10ms]
    L2 -->|Miss| Storage[Query Main Storage]

    Storage --> StorageResponse[Return from Storage <100ms]
    StorageResponse --> UpdateL2[Update L2 Cache]
    UpdateL2 --> UpdateL1[Update L1 Cache]

    MediumResponse --> UpdateL1_2[Update L1 Cache]

    UpdateL1 --> Response[Return to User]
    UpdateL1_2 --> Response
    FastResponse --> Response

    subgraph "Cache Layers"
        direction TB
        Memory[L1: In-Memory Cache<br/>Hot URLs]
        Redis[L2: Redis Cache<br/>Warm URLs]
        Database[Storage: SQLite/Postgres<br/>All URLs]
    end

    style FastResponse fill:#c8e6c9
    style MediumResponse fill:#fff3e0
    style StorageResponse fill:#ffecb3
    style Response fill:#e8f5e8
```

## Analytics and Monitoring Flow

```mermaid
sequenceDiagram
    participant User
    participant API
    participant Core
    participant Analytics
    participant Metrics
    participant Logs

    User->>API: HTTP Request
    API->>Metrics: Record Request Start
    API->>Core: Process Request

    Core->>Analytics: Update Click Count
    Analytics->>Metrics: Increment Business Metrics

    Core-->>API: Response
    API->>Logs: Log Operation
    API->>Metrics: Record Response Time
    API-->>User: HTTP Response

    Note over Metrics: Prometheus Metrics
    Note over Logs: Structured JSON Logs
    Note over Analytics: Click Tracking
```

## Future Microservices Architecture

```mermaid
graph TB
    subgraph "API Gateway"
        Gateway[API Gateway<br/>Rate Limiting, Auth, Routing]
    end

    subgraph "Core Services"
        URLService[URL Service<br/>Shortening & Expansion]
        AnalyticsService[Analytics Service<br/>Click Tracking & Reports]
        AdminService[Admin Service<br/>Management & Config]
    end

    subgraph "Data Layer"
        URLStorage[(URL Storage<br/>Redis/Postgres)]
        AnalyticsStorage[(Analytics Storage<br/>ClickHouse/BigQuery)]
        ConfigStorage[(Config Storage<br/>etcd/Consul)]
    end

    subgraph "External Services"
        Monitoring[Monitoring<br/>Prometheus/Grafana]
        Logging[Logging<br/>ELK Stack]
        Notifications[Notifications<br/>Email/Slack]
    end

    Gateway --> URLService
    Gateway --> AnalyticsService
    Gateway --> AdminService

    URLService --> URLStorage
    AnalyticsService --> AnalyticsStorage
    AdminService --> ConfigStorage

    URLService --> Monitoring
    AnalyticsService --> Monitoring
    AdminService --> Monitoring

    URLService --> Logging
    AnalyticsService --> Logging
    AdminService --> Logging

    AdminService --> Notifications

    style Gateway fill:#e3f2fd
    style URLService fill:#e8f5e8
    style AnalyticsService fill:#fff3e0
    style AdminService fill:#f3e5f5
```

## Usage Examples

### Basic Library Usage Flow

```mermaid
sequenceDiagram
    participant App as Your Application
    participant Lib as Talisik Library
    participant Storage as Storage Backend

    App->>Lib: from talisik import URLShortener
    App->>Lib: shortener = URLShortener()
    App->>Lib: request = ShortenRequest(url="https://example.com")
    App->>Lib: response = shortener.shorten(request)
    Lib->>Storage: Store URL mapping
    Storage-->>Lib: Confirmation
    Lib-->>App: ShortenResponse with short URL

    Note over App: Later...
    App->>Lib: original = shortener.expand("abc123")
    Lib->>Storage: Lookup short code
    Storage-->>Lib: Return ShortURL object
    Lib-->>App: Return original URL
```

This comprehensive workflow documentation provides visual representations of all major processes in the Talisik Short URL system, from basic operations to future architectural considerations.
