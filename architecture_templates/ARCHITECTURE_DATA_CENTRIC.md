# **ARCHITECTURE - DATA-CENTRIC**

**Project:** [PROJECT_NAME]  
**Updated:** [YYYY-MM-DD]  
**Architect:** [Name]  
**Status:** [Draft/Active]

---

## **C1: System Context**

**Purpose:**  
[One sentence: What business problem does this solve and for whom?]

**Actors:**
- **[Actor Name]:** [What they do with the system]
- **[Actor Name]:** [What they do with the system]

**External Systems:**
- **[System Name]:** [Integration purpose]
- **[System Name]:** [Integration purpose]

---

## **C2: Container Architecture**

```mermaid
C4Container
    title [PROJECT_NAME] - Container View
    
    %% Example structure - customize for your project:
    %% Person(user, "User", "Description")
    %% Container(core, "Core", "Python", "Business Logic")
    %% ContainerDb(db, "Database", "PostgreSQL", "Data Store")
    %% Rel(user, core, "Uses")
    %% Rel(core, db, "Reads/Writes")
```

**Containers:**

| Container | Technology | Responsibility |
|-----------|------------|----------------|
| [Name]    | [Tech]     | [Purpose]      |
| [Name]    | [Tech]     | [Purpose]      |

---

## **Technology Stack**

**Core:**
- Language: [Python 3.x]
- Database: [PostgreSQL/MySQL/SQLite]
- ORM: [SQLAlchemy/Django ORM]
- Migrations: [Alembic]

**Interfaces:**
- CLI: [Typer/Click]
- GUI: [PyQt/Tkinter/None]
- API: [FastAPI/Flask/None]

**Configuration:**
- Settings: [pydantic-settings]
- Secrets: [.env files]

---

## **Domain Model**

**Core Entities:**

| Entity | Purpose | Key Attributes |
|--------|---------|----------------|
| [Name] | [What it represents] | [Main fields] |
| [Name] | [What it represents] | [Main fields] |

**Relationships:**
```
[Entity1] (1) ──── has many ───→ (N) [Entity2]
[Entity2] (N) ──── belongs to ──→ (1) [Entity1]
```

---

## **Project Structure**

**Core Organization:**
```
src/{package}/core/
├── entities/       [Entity1, Entity2, ...]
├── services/       [Service1, Service2, ...]
├── repositories/   [Repo1, Repo2, ...]
└── models/         [Model1, Model2, ...]
```

**Test Organization:**
```
tests/
├── unit/entities/
├── unit/services/
├── unit/repositories/
├── integration/[workflow_name]/
└── [cli|gui]/
```

---

## **Key Business Rules**

1. **[Rule Name]:** [Brief description - which entities/services]
2. **[Rule Name]:** [Brief description - which entities/services]
3. **[Rule Name]:** [Brief description - which entities/services]

---

## **Critical Decisions (ADRs)**

### **ADR-001: [Title]**
- **Decision:** [What was decided]
- **Rationale:** [Why]
- **Impact:** [Consequences]

### **ADR-002: [Title]**
- **Decision:** [What was decided]
- **Rationale:** [Why]
- **Impact:** [Consequences]

---

## **Constraints**

**Must:**
- [Critical requirement 1]
- [Critical requirement 2]

**Must Not:**
- [Critical restriction 1]
- [Critical restriction 2]

**Performance:**
- [Key metric/requirement]
- [Key metric/requirement]
