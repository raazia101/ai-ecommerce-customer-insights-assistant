\# Week 2 — Warehouse ERD



\## Architecture



The warehouse follows a three-layer architecture:



RAW → STAGING → MART



The MART layer uses a star-schema design for analytical queries.



\## Star Schema



```text

&#x20;                        ┌─────────────────────┐

&#x20;                        │   dim\_customer      │

&#x20;                        │─────────────────────│

&#x20;                        │ PK customer\_key     │

&#x20;                        │    customer\_id      │

&#x20;                        │    first\_name       │

&#x20;                        │    last\_name        │

&#x20;                        │    email            │

&#x20;                        │    country          │

&#x20;                        │    signup\_date      │

&#x20;                        │    status           │

&#x20;                        │    valid\_from       │

&#x20;                        │    valid\_to         │

&#x20;                        │    is\_current       │

&#x20;                        └──────────┬──────────┘

&#x20;                                   │

&#x20;                                   │

┌─────────────────────┐             │             ┌─────────────────────┐

│    dim\_product      │             │             │      dim\_order      │

│─────────────────────│             │             │─────────────────────│

│ PK product\_key      │             │             │ PK order\_key        │

│    product\_id       │             │             │    order\_id         │

│    product\_name     │             │             │    customer\_id      │

│    category         │             │             │    order\_date       │

│    price            │             │             │    status            │

│    stock\_quantity   │             │             │    currency          │

│    status           │             │             │                     │

└──────────┬──────────┘             │             └──────────┬──────────┘

&#x20;          │                        │                        │

&#x20;          │                        │                        │

&#x20;          └────────────────────────┼────────────────────────┘

&#x20;                                   │

&#x20;                                   ▼

&#x20;                        ┌─────────────────────┐

&#x20;                        │ fact\_order\_items    │

&#x20;                        │─────────────────────│

&#x20;                        │ PK order\_item\_key   │

&#x20;                        │ FK order\_key        │

&#x20;                        │ FK customer\_key     │

&#x20;                        │ FK product\_key      │

&#x20;                        │ FK date\_key         │

&#x20;                        │    quantity         │

&#x20;                        │    unit\_price       │

&#x20;                        │    item\_revenue     │

&#x20;                        └──────────┬──────────┘

&#x20;                                   │

&#x20;                                   │

&#x20;                                   ▼

&#x20;                        ┌─────────────────────┐

&#x20;                        │      dim\_date       │

&#x20;                        │─────────────────────│

&#x20;                        │ PK date\_key         │

&#x20;                        │    full\_date        │

&#x20;                        │    year             │

&#x20;                        │    quarter          │

&#x20;                        │    month             │

&#x20;                        │    month\_name       │

&#x20;                        │    week             │

&#x20;                        │    day\_of\_week      │

&#x20;                        └─────────────────────┘

