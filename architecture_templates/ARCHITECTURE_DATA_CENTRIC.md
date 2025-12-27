# **PROJECT ARCHITECTURE - DATA-CENTRIC**

**META-DATA**
* **Project Name:** [PROJECT_NAME]
* **Last Updated:** [YYYY-MM-DD]
* **Status:** [Draft/Active/Deprecated]
* **Lead Architect:** [Name]

---

## **1. System Context (C1)**

**Goal:**  
[One sentence: What business problem does this system solve and for whom?]

**Primary Actors:**
* **[Actor 1]:** [Role and interaction with the system]
* **[Actor 2]:** [Role and interaction with the system]
* **[Actor 3]:** [Role and interaction with the system]

**External Systems:**
* **[System 1]:** [Integration point and purpose]
* **[System 2]:** [Integration point and purpose]

---

## **2. Container Architecture (C2)**

**High-level component view:**
```mermaid
C4Container
    title Container View - [PROJECT_NAME]
    
    %% Define your actors, containers, and relationships here
    %% Example:
    %% Person(user, "User", "End user of the system")
    %% Container(core, "Core Library", "Python", "Business Logic")
    %% ContainerDb(db, "Database", "PostgreSQL", "Stores business data")
    %% Rel(user, core, "Uses")
    %% Rel(core, db, "Reads/Writes")
```

**Container Descriptions:**

| Container | Technology | Responsibility |
|-----------|------------|----------------|
| [Name]    | [Stack]    | [What it does] |
| [Name]    | [Stack]    | [What it does] |

---

## **3. Technology Stack**

**Core Technologies:**
* **Language:** [Python 3.x]
* **Interfaces:** [CLI: Typer/Click | GUI: PyQt/Tkinter | API: FastAPI/Flask]
* **Data Layer:** [Database: PostgreSQL/MySQL/SQLite | ORM: SQLAlchemy/Django ORM]
* **Migrations:** [Alembic/Django Migrations]
* **Testing:** [Pytest, unittest]
* **Validation:** [Pydantic, marshmallow]

**Key Libraries:**
* [Library]: [Purpose]
* [Library]: [Purpose]

**Configuration:**
* **Environment:** [How configuration is loaded - e.g., pydantic-settings, python-decouple]
* **Secrets:** [How secrets are managed - e.g., .env files, vault]

---

## **4. Domain Model**

### **Core Business Entities**

List the main business entities in your domain:

| Entity | Description | Key Attributes |
|--------|-------------|----------------|
| [Entity1] | [What it represents] | [Main fields] |
| [Entity2] | [What it represents] | [Main fields] |
| [Entity3] | [What it represents] | [Main fields] |

### **Entity Relationships**
```
[Describe key relationships]
Example:
- Customer (1) ─── has many ──→ (N) Orders
- Order (N) ───── belongs to ──→ (1) Customer
- Order (N) ───── contains ──→ (N) Products (many-to-many)
```

---

## **5. Project-Specific Structure**

### **Source Code Organization**
```
src/{package_name}/core/
├── entities/
│   ├── [entity_1].py          # e.g., customer.py
│   ├── [entity_2].py          # e.g., order.py
│   ├── [entity_3].py          # e.g., product.py
│   └── ...
│
├── services/
│   ├── [service_1].py         # e.g., customer_service.py
│   ├── [service_2].py         # e.g., order_service.py
│   ├── [service_3].py         # e.g., billing_service.py
│   └── ...
│
├── repositories/
│   ├── [repository_1].py      # e.g., customer_repository.py
│   ├── [repository_2].py      # e.g., order_repository.py
│   ├── [repository_3].py      # e.g., product_repository.py
│   └── ...
│
└── models/
    ├── [model_1].py           # e.g., customer_model.py
    ├── [model_2].py           # e.g., order_model.py
    ├── [model_3].py           # e.g., product_model.py
    └── ...
```

### **Supporting Modules**
```
src/{package_name}/
├── cli/
│   ├── [command_group_1].py   # e.g., customer_commands.py
│   ├── [command_group_2].py   # e.g., order_commands.py
│   └── main.py
│
├── gui/
│   ├── [view_1].py            # e.g., customer_view.py
│   ├── [view_2].py            # e.g., order_view.py
│   └── app.py
│
└── utils/
    ├── config.py
    ├── database.py
    └── [utility].py
```

### **Test Organization**
```
tests/
├── unit/
│   ├── entities/
│   │   ├── test_[entity_1].py
│   │   └── test_[entity_2].py
│   │
│   ├── services/
│   │   ├── test_[service_1].py
│   │   └── test_[service_2].py
│   │
│   └── repositories/
│       ├── test_[repository_1].py
│       └── test_[repository_2].py
│
├── integration/
│   ├── [workflow_1]/
│   └── [workflow_2]/
│
├── cli/
│   └── test_[commands].py
│
└── gui/
    └── test_[views].py
```

---

## **6. Key Business Rules**

**Document critical business rules that govern the domain:**

### **Rule 1: [Rule Name]**
* **Description:** [What is the rule?]
* **Entities Affected:** [Which entities?]
* **Implementation:** [Where in code - entity/service?]

### **Rule 2: [Rule Name]**
* **Description:** [What is the rule?]
* **Entities Affected:** [Which entities?]
* **Implementation:** [Where in code - entity/service?]

---

## **7. Key Architectural Decisions**

### **ADR-001: [Decision Title]**
* **Status:** [Accepted/Proposed/Deprecated]
* **Context:** [Why this decision was needed]
* **Decision:** [What was decided]
* **Consequences:** [Trade-offs and implications]

### **ADR-002: [Decision Title]**
* **Status:** [Accepted/Proposed/Deprecated]
* **Context:** [Why this decision was needed]
* **Decision:** [What was decided]
* **Consequences:** [Trade-offs and implications]

---

## **8. Data Flow**

**Describe typical data flows for key operations:**

### **Example: [Operation Name - e.g., "Create Order"]**
```
1. User → CLI/GUI
2. CLI/GUI → OrderService.create_order()
3. OrderService → CustomerRepository.get_by_id()
4. Repository → CustomerModel (database query)
5. Repository → CustomerEntity (conversion)
6. OrderService → CustomerEntity.can_place_order() (business rule)
7. OrderService → OrderRepository.save()
8. Repository → OrderEntity → OrderModel (conversion)
9. Repository → Database (persist)
10. Service → CLI/GUI (success response)
```

---

## **9. Project Constraints & Guidelines**

**Must Follow:**
* [Project-specific rule 1]
* [Project-specific rule 2]
* [Project-specific rule 3]

**Must Avoid:**
* [Project-specific restriction 1]
* [Project-specific restriction 2]
* [Project-specific restriction 3]

**Database Conventions:**
* [Migration strategy]
* [Naming conventions]
* [Index strategy]

---