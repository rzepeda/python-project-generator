# **ARCHITECTURAL PRINCIPLES - DATA-CENTRIC**

*Quick reference for structure, rules, and decisions in data-centric projects*

---

## **1. Project Structure**

### **Fixed Scaffold (Never Modify)**
```
/
├── .venv/
├── .env
├── .gitignore
├── pyproject.toml
├── alembic.ini
├── agent_tools/        # IMMUTABLE
├── resources/
├── docs/
├── alembic/
└── workspace/
```

### **Core Structure (Architect Designs)**
```
src/{package}/core/
├── entities/           # Pure domain objects (framework-independent)
├── services/           # Business workflows (use cases)
├── repositories/       # Data access (Entity ↔ Model translation)
└── models/             # ORM models (SQLAlchemy only)

src/{package}/
├── cli/                # Terminal interface (adapter)
├── gui/                # Visual interface (adapter)
└── utils/              # Infrastructure (DB, config)

tests/
├── unit/entities/      # No database needed
├── unit/services/      # Mock repositories
├── unit/repositories/  # Test database
└── integration/        # Full workflows
```

---

## **2. Layer Rules**

| Layer | Location | Purpose | Responsibilities | Boundaries |
|-------|----------|---------|------------------|------------|
| **Entities** | `core/entities/` | Business logic | Rules, validations (`@dataclass`) | Framework-free |
| **Services** | `core/services/` | Workflows | Orchestrate entities + repos | Uses repositories for data |
| **Repositories** | `core/repositories/` | Data access | Entity ↔ Model conversion, queries | Returns entities only |
| **Models** | `core/models/` | DB mapping | Table structure, `to_entity()` | ORM definitions only |
| **CLI/GUI** | `cli/`, `gui/` | User interface | Call services, format I/O | Delegates logic to services |
| **Utils** | `utils/` | Infrastructure | DB sessions, config | Generic utilities only |

**Dependencies flow:** `CLI/GUI → Services → Repositories → Models → Utils`  
**Core rule:** Inner layers import only from same or inner layers

---

## **3. Decision Framework**

| Question | Answer |
|----------|--------|
| Business rule/validation? | → `entities/` |
| Workflow using multiple entities? | → `services/` |
| Database query/persistence? | → `repositories/` |
| Table structure/relationships? | → `models/` |
| User input/output? | → `cli/` or `gui/` |
| DB connection/config? | → `utils/` |

---

## **4. Key Distinctions**

**Entity vs Model:**
- **Entity**: Pure Python, business logic, no DB → `entities/customer.py`
- **Model**: SQLAlchemy, DB mapping only → `models/customer_model.py`

**Files:**
```
entities/customer.py              # Singular
services/customer_service.py      # Descriptive
repositories/customer_repository.py
models/customer_model.py
```

**Testing:**
- `unit/entities/` - No DB
- `unit/services/` - Mock repos
- `unit/repositories/` - Test DB
- `integration/` - Full stack

---

## **5. Core Principles**

✓ Business logic lives in entities  
✓ Services use repositories for data access  
✓ Core imports only from inner layers  
✓ Repositories return entities  
✓ Entities have rich behavior and rules
