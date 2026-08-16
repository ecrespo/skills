# Mermaid diagram templates

Copy the block for the architecture, then rename nodes to the user's domain (services, modules,
events, tables). Keep labels in the user's language. All render in Obsidian, GitHub and most
docs tools.

## 1. Layered monolith
```mermaid
flowchart TB
    subgraph Monolith["Monolith (one process, one deployment)"]
        P["Presentation<br/>(FastAPI routers / Reflex pages)"] --> S["Service / Application"] --> D["Domain"] --> R["Persistence"]
    end
    U["Client"] --> P
    R --> DB[("Database")]
```

## 2. Modular monolith
```mermaid
flowchart LR
    subgraph Deploy["One deployment"]
        subgraph M1["Module A"]
            A1[api] --> D1[domain] --> R1[repo]
        end
        subgraph M2["Module B"]
            A2[api] --> D2[domain] --> R2[repo]
        end
        Bus{{"In-process event bus"}}
        A2 -. "EventX" .-> Bus
        Bus -. subscribes .-> A1
        A1 -- "public API" --> A2
    end
    R1 & R2 --> DB[("DB - schema per module")]
```

## 3. Client-server
```mermaid
flowchart LR
    C1["Web client (Reflex/React)"] -->|HTTPS/WS| API
    C2["Mobile app"] -->|HTTPS| API
    subgraph Tier2["Application"]
        API["FastAPI / Reflex backend"]
    end
    API --> Cache[("Redis")]
    API --> DB[("MongoDB / PostgreSQL")]
```

## 4. Microservices
```mermaid
flowchart TB
    U["Clients"] --> GW["API Gateway"]
    GW --> S1["Service A"] & S2["Service B"] & S3["Service C"]
    S1 --> D1[("DB A")]
    S2 --> D2[("DB B")]
    S3 --> D3[("DB C")]
    S2 -- "event" --> MQ[["Broker"]]
    MQ --> S1 & S3
    subgraph Platform
        OBS["Observability"]
        SD["Discovery / mesh"]
        CI["CI/CD per service"]
    end
```

## 5. SOA
```mermaid
flowchart TB
    App1["Portal"] & App2["Mobile"] & App3["Call Center"] --> ESB{{"Enterprise Service Bus<br/>routing - transformation - orchestration"}}
    ESB --> S1["Customer service (canonical)"] & S2["Policy service"] & L1["Legacy (adapter)"]
    S1 & S2 --> DB[("Canonical DB")]
```

## 6. Event-driven (broker + mediator)
```mermaid
flowchart LR
    P["Producer"] -->|EventA| T1[("topic A")]
    T1 --> C1["Consumer 1"] -->|EventB| T2[("topic B")]
    T1 --> C2["Consumer 2"]
    T2 --> C3["Consumer 3"] & C4["Analytics"]
```
```mermaid
sequenceDiagram
    participant U as Client
    participant M as Mediator
    participant A as Service A
    participant B as Service B
    U->>M: Request
    M->>A: step 1
    A-->>M: EventA
    M->>B: step 2
    B-->>M: EventB
    M-->>U: Completed
```

## 7. Serverless
```mermaid
flowchart LR
    U["Client"] --> AGW["API Gateway"] --> F1["fn receive (FastAPI+Mangum)"] --> S3[("Object Storage")]
    S3 -- "ObjectCreated" --> F2["fn process"] --> Q[["Queue"]] --> F3["fn validate"] --> DB[("Managed DB")]
    CRON["Scheduler"] --> F4["fn daily job"] --> DB
```

## 8. Hexagonal
```mermaid
flowchart LR
    subgraph Driving["Primary adapters"]
        A1["FastAPI REST"]; A2["CLI"]; A3["Reflex UI"]; A4["MQ consumer"]
    end
    subgraph Hex["Application + Domain"]
        PI(("Input port<br/>UseCase")) --> DOM["Domain"] --> PO1(("Output port<br/>Repository")) & PO2(("Output port<br/>EventPublisher"))
    end
    subgraph Driven["Secondary adapters"]
        B1["MongoRepo"]; B2["InMemoryRepo (tests)"]; B3["RabbitPublisher"]
    end
    A1 & A2 & A3 & A4 --> PI
    PO1 --> B1 & B2
    PO2 --> B3
```

## 9. Clean / Onion
```mermaid
flowchart TB
    subgraph L4["Frameworks & Drivers"]
        subgraph L3["Interface Adapters"]
            subgraph L2["Use Cases"]
                subgraph L1["Entities"]
                    E["Entities - VOs - Domain Services"]
                end
                UC["Use cases - in/out DTOs"]
            end
            IA["Controllers - Presenters - Repos - Gateways"]
        end
        FD["FastAPI - Reflex - PyMongo - RabbitMQ"]
    end
    FD -.-> IA -.-> UC -.-> E
```

## 10. CQRS + Event Sourcing
```mermaid
flowchart LR
    U["Client"] -->|Command| CH["Command Handler"] --> AGG["Aggregate<br/>load -> apply -> decide"]
    AGG -->|append event| ES[("Event Store")]
    ES --> PR["Projectors"] --> RM1[("Read model 1")] & RM2[("Analytics read model")]
    U -->|Query| QH["Query Handler"] --> RM1
    ES -. snapshots .-> SNAP[("Snapshots")]
```

## 11. Microkernel
```mermaid
flowchart TB
    subgraph Kernel["Core"]
        REG["Plugin registry"] --> PIPE["Execution engine"]
        CT["Contract / Interface"] --- REG
    end
    P1["Plugin 1"] & P2["Plugin 2"] & P3["Third-party plugin"] -.implements.-> CT
    IN["Input"] --> PIPE --> OUT["Output"]
```

## 12. Pipes & Filters
```mermaid
flowchart LR
    SRC["Source"] --> F1["Filter 1"] -->|contract A| F2["Filter 2"] -->|contract B| F3["Filter 3"] --> SINK["Sink"]
    F2 -. branch .-> F4["Alternate filter"] -.-> F3
```

## 13. Space-Based
```mermaid
flowchart TB
    U["Clients (peak)"] --> MG["Messaging Grid"] --> PU1["PU 1"] & PU2["PU 2"] & PU3["PU n"]
    DG["Data Grid (replicated memory)"] <--> PU1 & PU2 & PU3
    PU1 & PU2 & PU3 -->|write-behind| DP[["Data Pumps"]] --> DW["Data Writers"] --> DB[("DB")]
    DB --> DR["Data Readers"] -->|preload| DG
```

## 14. Service-Based
```mermaid
flowchart TB
    UI["UI"] --> GW["Gateway / BFF"] --> S1["Domain service 1"] & S2["Domain service 2"] & S3["Domain service 3"]
    S1 & S2 & S3 --> DB[("Shared DB - ownership per collection")]
    S2 -. events .-> S1
```

## 15. Micro-frontends
```mermaid
flowchart TB
    subgraph Shell["App Shell (routing, auth, layout)"]
        MF1["MF A (team A)"]; MF2["MF B (team B)"]; MF3["MF C (team C)"]
    end
    MF1 --> B1["API A"]; MF2 --> B2["API B"]; MF3 --> B3["API C"]
    DS["Design System"] -.-> MF1 & MF2 & MF3
```

## 16. Peer-to-Peer
```mermaid
flowchart LR
    N1((A)) <--> N2((B)) <--> N3((C)) <--> N4((D)) <--> N1
    N1 <--> N3
    N2 <--> N4
    BS["Bootstrap / DHT"] -.-> N1 & N2 & N3 & N4
```

## 17. Cell-Based
```mermaid
flowchart TB
    U["Clients"] --> CR["Cell Router (tenant/hash/region)"]
    subgraph C1["Cell 1"]; A1["Services"] --> D1[("Data")]; end
    subgraph C2["Cell 2"]; A2["Services"] --> D2[("Data")]; end
    subgraph C3["Cell 3 (canary)"]; A3["Services v2"] --> D3[("Data")]; end
    CR --> C1 & C2 & C3
    CP["Control Plane"] -.-> C1 & C2 & C3
```

## 18. Agentic
```mermaid
flowchart LR
    U["User / Event"] --> ORQ["Orchestrator (LangGraph)"] --> A1["Router agent"]
    A1 --> A2["Agent A"] & A3["Agent B"]
    A2 & A3 --> T{{"Tools / MCP"}}
    A2 & A3 --> HITL["Human-in-the-loop"]
    ORQ --> MEM[("Memory / Checkpointer")] & OBS["Evals - Traces - Guardrails"]
```

## 19. DOMA
```mermaid
flowchart TB
    subgraph L5["Edge"]; E["Edge Gateway"]; end
    subgraph L4["Presentation"]; P1["App domain"]; end
    subgraph L3["Product"]; PR["Product domain"]; end
    subgraph L2["Business"]
        subgraph DOM["Domain X"]
            GW["Gateway X (single entry point)"] --> S1["svc-1"] & S2["svc-2"]
            S1 -. plugin .-> X1["Logic extension"]
            S1 -. carries .-> X2["Data extension"]
        end
    end
    subgraph L1["Infrastructure"]; I1["Storage"]; I2["Messaging"]; end
    E --> P1 --> PR --> GW
    S1 --> I1
    S2 --> I2
```

## Combined reference system
```mermaid
flowchart TB
    MF["Micro-frontends / Reflex apps"] --> GW["API Gateway / BFF"]
    subgraph Core["Services (Service-Based -> Microservices -> DOMA)"]
        S1["Domain A<br/>Hexagonal + Clean"]; S2["Domain B<br/>Hexagonal + CQRS/ES"]; S3["Domain C<br/>Pipes & Filters + Microkernel"]
    end
    GW --> S1 & S2 & S3
    S1 & S2 & S3 <--> BUS[["Event Bus (EDA)"]]
    BUS --> FN["Serverless (notifications, ETL)"] & AG["LLM agents"]
```

## Decision tree
```mermaid
flowchart TD
    Q1{"How many teams?"} -->|1-2| Q2{"Complex domain / long lifespan?"}
    Q1 -->|3+| Q3{"DevOps maturity?"}
    Q2 -->|No| MONO["Layered monolith"]
    Q2 -->|Yes| MM["Modular monolith + Hexagonal/Clean"]
    Q3 -->|Low| SB["Service-Based"]
    Q3 -->|High| MS["Microservices"] -->|hundreds of services| DOMA["DOMA"]
    MM & SB & MS --> Q4{"Async / peaks?"} -->|Yes| EDA["+ EDA"]
    Q4 -->|No| FIN["Done"]
    EDA --> Q5{"Audit / contention?"} -->|Yes| CQRS["+ CQRS (+- ES)"]
    Q5 -->|No| Q6{"Sporadic workloads?"} -->|Yes| SLS["+ Serverless"]
    CQRS --> Q6
    Q6 -->|No| FIN
```
