# **DATA-CENTRIC ARCHITECTURAL PRINCIPLES**

*Reference guide for architects building data-centric applications with Clean Architecture*

---

## **1. What is Data-Centric Architecture?**

**Data-Centric Architecture** focuses on modeling and managing business entities with their associated business rules and persistence.

**Best suited for:**
- Business applications (CRM, ERP, e-commerce)
- Systems with complex domain models
- Applications requiring CRUD operations
- Projects with rich business rules
- Multi-user systems with shared data

**Core philosophy:** The domain model (entities and their relationships) is the heart of the system.

---

## **2. Project Structure Overview**

### **Fixed Scaffold (Never Modify)**
```
[PROJECT_NAME]/
├── .venv/                      # Virtual environment (ignored)
├── .env                        # Environment variables (ignored)
├── .gitignore
├── requirements.txt
├── pyproject.toml
├── alembic.ini                 # Database migrations config
├── README.md
├── agent_tools/                # Agent tooling (IMMUTABLE)
├── resources/                  # Prompts and templates
├── docs/                       # Knowledge base
├── alembic/                    # Database migrations
│   ├── versions/
│   └── env.py
└── workspace/                  # Agent sandbox (ignored)
```

### **Dynamic Areas (Architect Designs)**
```
src/{package_name}/
├── core/                       # Business logic (architect designs this)
│   ├── entities/               # Pure domain objects
│   ├── services/               # Business operations
│   ├── repositories/           # Data access interfaces
│   └── models/                 # ORM models
├── cli/                        # Terminal interface
├── gui/                        # Graphical interface
└── utils/                      # Infrastructure

tests/
├── unit/                       # Unit tests
│   ├── entities/
│   ├── services/
│   └── repositories/
├── integration/                # Integration tests
├── cli/                        # CLI tests
└── gui/                        # GUI tests
```

---

## **3. Clean Architecture Principles**

### **The Dependency Rule**

**Dependencies ALWAYS flow inward:**
```
┌─────────────────────────────────────────┐
│ Adapters (CLI/GUI)                      │  ← Outer layer
│ - User interface                        │
│ - Framework-specific code               │
└──────────────┬──────────────────────────┘
               │ depends on
               ↓
┌─────────────────────────────────────────┐
│ Services                                │  ← Middle layer
│ - Business workflows                    │
│ - Use cases                             │
└──────────────┬──────────────────────────┘
               │ depends on
               ↓
┌─────────────────────────────────────────┐
│ Entities                                │  ← Inner layer (core)
│ - Business rules                        │
│ - Domain logic                          │
│ - Framework-independent                 │
└─────────────────────────────────────────┘
```

**Critical rules:**
- Inner layers NEVER import from outer layers
- Core entities have NO external dependencies
- Services orchestrate, entities contain rules
- Adapters translate between layers

---

## **4. Layer Responsibilities**

### **Entities Layer** (`core/entities/`)

**Purpose:** Pure business objects with business rules

**Characteristics:**
- Framework-independent (use `@dataclass`, `attrs`, or plain classes)
- Contains business validation and rules
- Represents concepts from the business domain
- NO database, NO framework imports

**Example:**
```python
# entities/customer.py
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class CustomerEntity:
    """Pure business object - no framework dependencies"""
    id: Optional[int]
    name: str
    email: str
    credit_limit: float
    member_since: datetime
    
    def can_place_order(self, order_amount: float) -> bool:
        """Business rule: customer can't exceed credit limit"""
        return order_amount <= self.credit_limit
    
    def is_vip(self) -> bool:
        """Business rule: VIP customers have high credit"""
        return self.credit_limit >= 10000
    
    def increase_credit_limit(self, amount: float) -> None:
        """Business operation"""
        if amount <= 0:
            raise ValueError("Increase must be positive")
        self.credit_limit += amount
    
    def validate(self) -> None:
        """Business validation"""
        if not self.name:
            raise ValueError("Name is required")
        if not self.email or '@' not in self.email:
            raise ValueError("Valid email is required")
        if self.credit_limit < 0:
            raise ValueError("Credit limit cannot be negative")
```

**Key points:**
- All business rules live here
- Testable without ANY infrastructure
- Represents what the business cares about
- Rich behavior, not just data containers

---

### **Services Layer** (`core/services/`)

**Purpose:** Orchestrate business workflows and use cases

**Characteristics:**
- Coordinates multiple entities and repositories
- Contains workflow logic (use cases)
- Transaction boundaries
- Works ONLY with entities (not models)

**Example:**
```python
# services/order_service.py
from ..entities.customer import CustomerEntity
from ..entities.order import OrderEntity
from ..repositories.customer_repository import CustomerRepository
from ..repositories.order_repository import OrderRepository
from typing import List

class OrderService:
    """Business operations for orders"""
    
    def __init__(
        self,
        customer_repo: CustomerRepository,
        order_repo: OrderRepository
    ):
        self.customer_repo = customer_repo
        self.order_repo = order_repo
    
    def place_order(
        self,
        customer_id: int,
        items: List[dict],
        total_amount: float
    ) -> OrderEntity:
        """
        Use case: Place a new order
        Orchestrates: validation, business rules, persistence
        """
        # 1. Load entities
        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            raise ValueError("Customer not found")
        
        # 2. Apply business rules (from entity)
        if not customer.can_place_order(total_amount):
            raise ValueError("Order exceeds customer credit limit")
        
        # 3. Create new entity
        order = OrderEntity.create_new(
            customer_id=customer_id,
            items=items,
            total_amount=total_amount
        )
        
        # 4. Validate
        order.validate()
        
        # 5. Persist
        saved_order = self.order_repo.save(order)
        
        # 6. Update customer credit
        customer.credit_limit -= total_amount
        self.customer_repo.save(customer)
        
        return saved_order
    
    def cancel_order(self, order_id: int) -> None:
        """Use case: Cancel an order"""
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise ValueError("Order not found")
        
        # Business rule from entity
        order.cancel()
        
        # Restore customer credit
        customer = self.customer_repo.get_by_id(order.customer_id)
        customer.credit_limit += order.total_amount
        
        self.order_repo.save(order)
        self.customer_repo.save(customer)
```

**Key points:**
- Orchestrates workflows
- Manages transactions
- Coordinates multiple repositories
- No direct database access
- Works with entities, not models

---

### **Repositories Layer** (`core/repositories/`)

**Purpose:** Translate between entities and database models

**Characteristics:**
- Abstracts data access
- Converts Entity ↔ Model
- Encapsulates queries
- Hides database details from services

**Example:**
```python
# repositories/customer_repository.py
from sqlalchemy.orm import Session
from ..models.customer_model import CustomerModel
from ..entities.customer import CustomerEntity
from typing import Optional, List

class CustomerRepository:
    """Data access for customers"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, customer_id: int) -> Optional[CustomerEntity]:
        """Load customer by ID, return entity"""
        model = self.session.query(CustomerModel).filter_by(
            id=customer_id
        ).first()
        
        return model.to_entity() if model else None
    
    def get_by_email(self, email: str) -> Optional[CustomerEntity]:
        """Find customer by email"""
        model = self.session.query(CustomerModel).filter_by(
            email=email
        ).first()
        
        return model.to_entity() if model else None
    
    def get_vip_customers(self) -> List[CustomerEntity]:
        """Domain-specific query: find VIP customers"""
        models = self.session.query(CustomerModel).filter(
            CustomerModel.credit_limit >= 10000
        ).all()
        
        return [m.to_entity() for m in models]
    
    def save(self, entity: CustomerEntity) -> CustomerEntity:
        """Save customer entity to database"""
        if entity.id:
            # Update existing
            model = self.session.query(CustomerModel).filter_by(
                id=entity.id
            ).first()
            
            if not model:
                raise ValueError("Customer not found for update")
            
            # Update fields from entity
            model.name = entity.name
            model.email = entity.email
            model.credit_limit = entity.credit_limit
            model.member_since = entity.member_since
        else:
            # Create new
            model = CustomerModel.from_entity(entity)
            self.session.add(model)
        
        self.session.commit()
        self.session.refresh(model)
        
        return model.to_entity()
    
    def delete(self, customer_id: int) -> None:
        """Delete customer"""
        model = self.session.query(CustomerModel).filter_by(
            id=customer_id
        ).first()
        
        if model:
            self.session.delete(model)
            self.session.commit()
```

**Key points:**
- Always returns/accepts entities (not models)
- Handles all database queries
- Domain-specific query methods
- Conversion happens here

---

### **Models Layer** (`core/models/`)

**Purpose:** ORM models for database mapping ONLY

**Characteristics:**
- SQLAlchemy/Django ORM definitions
- Table structure and relationships
- Conversion methods: `to_entity()` and `from_entity()`
- NO business logic

**Example:**
```python
# models/customer_model.py
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class CustomerModel(Base):
    """
    ORM Model - ONLY responsible for database mapping
    NO business logic here!
    """
    __tablename__ = 'customers'
    
    # Table structure
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False, unique=True)
    credit_limit = Column(Float, default=0.0)
    member_since = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    orders = relationship("OrderModel", back_populates="customer")
    
    def to_entity(self) -> 'CustomerEntity':
        """Convert ORM model to business entity"""
        from ..entities.customer import CustomerEntity
        
        return CustomerEntity(
            id=self.id,
            name=self.name,
            email=self.email,
            credit_limit=self.credit_limit,
            member_since=self.member_since
        )
    
    @staticmethod
    def from_entity(entity: 'CustomerEntity') -> 'CustomerModel':
        """Convert business entity to ORM model"""
        return CustomerModel(
            id=entity.id,
            name=entity.name,
            email=entity.email,
            credit_limit=entity.credit_limit,
            member_since=entity.member_since
        )
```

**Key points:**
- Just data mapping, NO logic
- Provide conversion methods
- Define relationships
- Framework-specific

---

### **Adapters Layer** (`cli/`, `gui/`)

**Purpose:** User interface - translate user actions to service calls

**Characteristics:**
- Handles user input/output
- Calls services (not repositories directly)
- Formats responses for display
- NO business logic

**Example:**
```python
# cli/customer_commands.py
import typer
from ..core.services.customer_service import CustomerService
from ..core.services.order_service import OrderService
from ..utils.database import DatabaseManager

app = typer.Typer()

@app.command()
def create_customer(
    name: str,
    email: str,
    credit_limit: float = 1000.0
):
    """Create a new customer"""
    # Setup infrastructure
    db = DatabaseManager()
    session = db.get_session()
    
    # Create service
    customer_service = CustomerService(
        customer_repo=CustomerRepository(session)
    )
    
    try:
        # Call service (business logic)
        customer = customer_service.create_customer(
            name=name,
            email=email,
            credit_limit=credit_limit
        )
        
        # Format output for user
        typer.echo(f"✓ Customer created: {customer.name} (ID: {customer.id})")
    except ValueError as e:
        typer.echo(f"✗ Error: {e}", err=True)
    finally:
        session.close()

@app.command()
def place_order(
    customer_id: int,
    amount: float
):
    """Place an order for a customer"""
    db = DatabaseManager()
    session = db.get_session()
    
    order_service = OrderService(
        customer_repo=CustomerRepository(session),
        order_repo=OrderRepository(session)
    )
    
    try:
        order = order_service.place_order(
            customer_id=customer_id,
            items=[],  # Simplified
            total_amount=amount
        )
        
        typer.echo(f"✓ Order placed: #{order.id} - ${amount}")
    except ValueError as e:
        typer.echo(f"✗ Error: {e}", err=True)
    finally:
        session.close()
```

**Key points:**
- Parse user input
- Call appropriate service
- Format output
- Handle user-facing errors
- Manage infrastructure (sessions, etc.)

---

### **Infrastructure Layer** (`utils/`)

**Purpose:** Generic, reusable infrastructure tools

**Characteristics:**
- Database connection management
- Configuration loading
- Generic utilities
- NO business logic

**Example:**
```python
# utils/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .config import settings

class DatabaseManager:
    """Generic database infrastructure"""
    
    def __init__(self):
        self.engine = create_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG
        )
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False
        )
    
    def get_session(self) -> Session:
        """Provide a database session"""
        return self.SessionLocal()
    
    def create_tables(self):
        """Create all tables from models"""
        from ..core.models.customer_model import Base
        Base.metadata.create_all(self.engine)
    
    def drop_tables(self):
        """Drop all tables (use with caution!)"""
        from ..core.models.customer_model import Base
        Base.metadata.drop_all(self.engine)

# utils/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application configuration"""
    DATABASE_URL: str
    DEBUG: bool = False
    SECRET_KEY: str
    
    class Config:
        env_file = ".env"

settings = Settings()
```

---

## **5. Key Design Patterns**

### **Entity vs Model Separation**

**Why:** Business logic must be testable without frameworks
```python
# ✅ CORRECT APPROACH

# Entity: Pure business logic
@dataclass
class CustomerEntity:
    credit_limit: float
    
    def can_place_order(self, amount: float) -> bool:
        """Business rule - no framework needed"""
        return amount <= self.credit_limit

# Model: Just database mapping
class CustomerModel(Base):
    __tablename__ = 'customers'
    credit_limit = Column(Float)
    
    def to_entity(self) -> CustomerEntity:
        """Convert to entity"""
        return CustomerEntity(credit_limit=self.credit_limit)
```
```python
# ❌ WRONG APPROACH

# Mixing business logic with ORM
class Customer(Base):
    __tablename__ = 'customers'
    credit_limit = Column(Float)
    
    def can_place_order(self, amount: float) -> bool:
        # Business logic tied to SQLAlchemy!
        # Can't test without database
        return amount <= self.credit_limit
```

---

### **Repository Pattern**

**Why:** Abstract data access, enable testing, make storage swappable
```python
# ✅ CORRECT: Repository abstracts database

class CustomerRepository:
    def get_by_id(self, id: int) -> CustomerEntity:
        # Handles database query
        model = self.session.query(CustomerModel).get(id)
        # Returns entity, not model
        return model.to_entity()

# Service doesn't know about database
class CustomerService:
    def __init__(self, repo: CustomerRepository):
        self.repo = repo  # Works with interface
    
    def get_customer(self, id: int):
        return self.repo.get_by_id(id)  # Database hidden
```
```python
# ❌ WRONG: Service accesses database directly

class CustomerService:
    def __init__(self, session: Session):
        self.session = session  # Tight coupling!
    
    def get_customer(self, id: int):
        # Service knows about ORM
        return self.session.query(CustomerModel).get(id)
```

---

### **Dependency Injection**

**Why:** Loose coupling, testability, flexibility
```python
# ✅ CORRECT: Dependencies injected

class OrderService:
    def __init__(
        self,
        customer_repo: CustomerRepository,
        order_repo: OrderRepository
    ):
        # Dependencies provided from outside
        self.customer_repo = customer_repo
        self.order_repo = order_repo

# Easy to test with mocks
def test_place_order():
    mock_customer_repo = MockCustomerRepository()
    mock_order_repo = MockOrderRepository()
    
    service = OrderService(mock_customer_repo, mock_order_repo)
    # Test without real database!
```
```python
# ❌ WRONG: Creating dependencies inside

class OrderService:
    def __init__(self, session: Session):
        # Hard-coded dependencies
        self.customer_repo = CustomerRepository(session)
        self.order_repo = OrderRepository(session)
        # Can't swap for testing!
```

---

## **6. Testing Strategy**

### **Unit Tests - Entities (No Infrastructure)**
```python
# tests/unit/entities/test_customer.py
from src.core.entities.customer import CustomerEntity
from datetime import datetime

def test_customer_can_place_order():
    """Test business rule without database"""
    customer = CustomerEntity(
        id=1,
        name="John Doe",
        email="john@example.com",
        credit_limit=1000.0,
        member_since=datetime.now()
    )
    
    assert customer.can_place_order(500.0) == True
    assert customer.can_place_order(1500.0) == False

def test_customer_is_vip():
    """Test VIP business rule"""
    regular = CustomerEntity(
        id=1, name="John", email="j@x.com",
        credit_limit=5000.0, member_since=datetime.now()
    )
    vip = CustomerEntity(
        id=2, name="Jane", email="jane@x.com",
        credit_limit=15000.0, member_since=datetime.now()
    )
    
    assert regular.is_vip() == False
    assert vip.is_vip() == True

def test_increase_credit_limit_validation():
    """Test business validation"""
    customer = CustomerEntity(
        id=1, name="John", email="j@x.com",
        credit_limit=1000.0, member_since=datetime.now()
    )
    
    with pytest.raises(ValueError, match="must be positive"):
        customer.increase_credit_limit(-100)
```

---

### **Unit Tests - Services (With Mocked Repositories)**
```python
# tests/unit/services/test_order_service.py
from unittest.mock import Mock
from src.core.services.order_service import OrderService
from src.core.entities.customer import CustomerEntity
from src.core.entities.order import OrderEntity

def test_place_order_success():
    """Test order placement workflow"""
    # Mock repositories
    mock_customer_repo = Mock()
    mock_order_repo = Mock()
    
    # Setup test data
    customer = CustomerEntity(
        id=1, name="John", email="j@x.com",
        credit_limit=1000.0, member_since=datetime.now()
    )
    mock_customer_repo.get_by_id.return_value = customer
    
    # Test
    service = OrderService(mock_customer_repo, mock_order_repo)
    order = service.place_order(
        customer_id=1,
        items=[{"product": "Widget", "qty": 2}],
        total_amount=500.0
    )
    
    # Verify
    assert mock_customer_repo.get_by_id.called
    assert mock_order_repo.save.called
    assert customer.credit_limit == 500.0  # Updated

def test_place_order_exceeds_credit():
    """Test business rule enforcement"""
    mock_customer_repo = Mock()
    mock_order_repo = Mock()
    
    customer = CustomerEntity(
        id=1, name="John", email="j@x.com",
        credit_limit=100.0, member_since=datetime.now()
    )
    mock_customer_repo.get_by_id.return_value = customer
    
    service = OrderService(mock_customer_repo, mock_order_repo)
    
    with pytest.raises(ValueError, match="exceeds.*credit limit"):
        service.place_order(customer_id=1, items=[], total_amount=500.0)
```

---

### **Integration Tests - Repositories (With Test Database)**
```python
# tests/integration/test_customer_repository.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.models.customer_model import Base, CustomerModel
from src.core.repositories.customer_repository import CustomerRepository
from src.core.entities.customer import CustomerEntity
from datetime import datetime

@pytest.fixture
def test_session():
    """Create test database session"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_save_and_get_customer(test_session):
    """Test full persistence cycle"""
    repo = CustomerRepository(test_session)
    
    # Create entity
    customer = CustomerEntity(
        id=None,
        name="John Doe",
        email="john@example.com",
        credit_limit=1000.0,
        member_since=datetime.now()
    )
    
    # Save
    saved = repo.save(customer)
    assert saved.id is not None
    
    # Retrieve
    retrieved = repo.get_by_id(saved.id)
    assert retrieved.name == "John Doe"
    assert retrieved.email == "john@example.com"

def test_get_vip_customers(test_session):
    """Test domain-specific query"""
    repo = CustomerRepository(test_session)
    
    # Create customers
    regular = CustomerEntity(
        id=None, name="Regular", email="reg@x.com",
        credit_limit=5000.0, member_since=datetime.now()
    )
    vip = CustomerEntity(
        id=None, name="VIP", email="vip@x.com",
        credit_limit=15000.0, member_since=datetime.now()
    )
    
    repo.save(regular)
    repo.save(vip)
    
    # Query VIPs
    vips = repo.get_vip_customers()
    assert len(vips) == 1
    assert vips[0].name == "VIP"
```

---

## **7. Common Anti-Patterns to Avoid**

### ❌ **Anti-Pattern 1: Business Logic in Models**
```python
# BAD
class Customer(Base):
    __tablename__ = 'customers'
    credit_limit = Column(Float)
    
    def can_place_order(self, amount):  # Business logic in ORM!
        return amount <= self.credit_limit
```

**Why it's bad:** Can't test business logic without database, tied to framework

**Fix:** Move to entity
```python
# GOOD
@dataclass
class CustomerEntity:
    credit_limit: float
    
    def can_place_order(self, amount):  # Pure business logic
        return amount <= self.credit_limit
```

---

### ❌ **Anti-Pattern 2: Services Accessing Database Directly**
```python
# BAD
class OrderService:
    def __init__(self, session):
        self.session = session
    
    def place_order(self, customer_id, amount):
        customer = self.session.query(Customer).get(customer_id)  # Direct DB access!
```

**Why it's bad:** Service tied to SQLAlchemy, can't swap storage, hard to test

**Fix:** Use repository
```python
# GOOD
class OrderService:
    def __init__(self, customer_repo):
        self.customer_repo = customer_repo
    
    def place_order(self, customer_id, amount):
        customer = self.customer_repo.get_by_id(customer_id)  # Through abstraction
```

---

### ❌ **Anti-Pattern 3: Business Logic in CLI/GUI**
```python
# BAD - in cli/commands.py
@app.command()
def create_order(customer_id: int, amount: float):
    customer = session.query(Customer).get(customer_id)
    
    # Business logic in CLI!
    if amount > customer.credit_limit:
        typer.echo("Error: Exceeds credit limit")
        return
    
    order = Order(customer_id=customer_id, amount=amount)
    session.add(order)
    session.commit()
```

**Why it's bad:** Business logic duplicated in UI, can't reuse in API/GUI

**Fix:** Move to service
```python
# GOOD
@app.command()
def create_order(customer_id: int, amount: float):
    service = OrderService(customer_repo, order_repo)
    
    try:
        order = service.place_order(customer_id, [], amount)  # Service handles logic
        typer.echo(f"Order created: {order.id}")
    except ValueError as e:
        typer.echo(f"Error: {e}")
```

---

### ❌ **Anti-Pattern 4: Core Importing from Outer Layers**
```python
# BAD - in core/services/customer_service.py
from cli.formatters import format_customer_output  # NEVER!

class CustomerService:
    def get_customer(self, id):
        customer = self.repo.get_by_id(id)
        return format_customer_output(customer)  # Core using CLI code!
```

**Why it's bad:** Violates dependency rule, core depends on UI

**Fix:** Keep core pure, format in adapter
```python
# GOOD
# In service - returns entity
class CustomerService:
    def get_customer(self, id):
        return self.repo.get_by_id(id)  # Returns entity

# In CLI - handles formatting
@app.command()
def show_customer(id: int):
    customer = service.get_customer(id)
    output = format_customer_output(customer)  # Format in UI layer
    typer.echo(output)
```

---

### ❌ **Anti-Pattern 5: Anemic Domain Model**
```python
# BAD - Entity is just data, no behavior
@dataclass
class CustomerEntity:
    id: int
    name: str
    credit_limit: float
    # No methods, no business logic!

# All logic ends up in service
class CustomerService:
    def can_place_order(self, customer, amount):  # Should be in entity!
        return amount <= customer.credit_limit
    
    def is_vip(self, customer):  # Should be in entity!
        return customer.credit_limit >= 10000
```

**Why it's bad:** Entities become dumb data containers, logic scattered

**Fix:** Rich domain model
```python
# GOOD - Entity has behavior
@dataclass
class CustomerEntity:
    id: int
    name: str
    credit_limit: float
    
    def can_place_order(self, amount: float) -> bool:
        """Business rule lives in entity"""
        return amount <= self.credit_limit
    
    def is_vip(self) -> bool:
        """Business rule lives in entity"""
        return self.credit_limit >= 10000

# Service orchestrates, entity has rules
class CustomerService:
    def place_order(self, customer_id, amount):
        customer = self.repo.get_by_id(customer_id)
        
        if not customer.can_place_order(amount):  # Entity's rule
            raise ValueError("Exceeds credit")
```

---

## **8. Decision Framework**

### **Where Does This Code Go?**

Use this decision tree:
```
Is it a business rule or domain concept?
├─ YES → Entity
│   └─ Examples: validation, calculations, business constraints
│
└─ NO → Is it orchestrating multiple entities/repos?
    ├─ YES → Service
    │   └─ Examples: workflows, use cases, transactions
    │
    └─ NO → Is it data access?
        ├─ YES → Repository
        │   └─ Examples: queries, persistence, Entity↔Model conversion
        │
        └─ NO → Is it database structure?
            ├─ YES → Model
            │   └─ Examples: tables, columns, relationships
            │
            └─ NO → Is it user interaction?
                ├─ YES → CLI/GUI
                │   └─ Examples: parsing input, formatting output
                │
                └─ NO → Infrastructure (Utils)
                    └─ Examples: database sessions, config, logging
```

### **Specific Examples:**

| Code | Location | Reason |
|------|----------|--------|
| "Customer credit can't be negative" | Entity | Business validation |
| "Calculate total order amount" | Entity | Business calculation |
| "Place order workflow" | Service | Multi-step use case |
| "Find customers by email" | Repository | Data access |
| "customers table definition" | Model | Database structure |
| "Show order confirmation" | CLI/GUI | User interface |
| "Create database session" | Utils | Infrastructure |

---

## **9. Best Practices**

### **Entity Design**

✅ **DO:**
- Make entities rich with behavior
- Keep entities framework-independent
- Put business rules in entities
- Use value objects for complex types
- Validate in entity methods

❌ **DON'T:**
- Make anemic entities (just data)
- Import ORM in entities
- Put infrastructure code in entities
- Leak database concepts into entities

### **Service Design**

✅ **DO:**
- Orchestrate workflows
- Manage transactions
- Coordinate repositories
- Handle cross-cutting concerns
- Work with entities only

❌ **DON'T:**
- Access database directly
- Duplicate business rules
- Put UI logic in services
- Return models from services

### **Repository Design**

✅ **DO:**
- Always return entities
- Encapsulate all queries
- Handle conversions
- Provide domain-specific methods

❌ **DON'T:**
- Expose models to services
- Put business logic in repos
- Return SQLAlchemy queries
- Leak database details

### **Model Design**

✅ **DO:**
- Define table structure
- Provide conversion methods
- Keep it simple

❌ **DON'T:**
- Add business logic
- Make complex methods
- Use outside of repositories

---

## **10. Migration Strategy**

### **Database Migrations with Alembic**
```bash
# Create migration
alembic revision --autogenerate -m "Add customer table"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

### **Data Migration Pattern**
```python
# migrations/scripts/migrate_customer_data.py
def migrate_customer_credit_limits():
    """Example: Migrate old credit system to new"""
    session = get_session()
    repo = CustomerRepository(session)
    
    # Load all customers
    customers = repo.get_all()
    
    for customer in customers:
        # Apply business rule (from entity)
        if customer.legacy_credit_score > 700:
            customer.credit_limit = 10000
        else:
            customer.credit_limit = 5000
        
        # Save updated entity
        repo.save(customer)
    
    session.close()
```

---

## **11. Example Complete Flow**

### **Scenario: User places an order via CLI**
```
1. User types: `app order create --customer-id 123 --amount 500`

2. CLI (cli/commands.py)
   ├─ Parses arguments
   ├─ Creates infrastructure (session, repos)
   └─ Calls OrderService.place_order()

3. Service (services/order_service.py)
   ├─ Loads CustomerEntity via CustomerRepository
   ├─ Calls customer.can_place_order(500) ← BUSINESS RULE
   ├─ Creates OrderEntity
   ├─ Calls order.validate() ← BUSINESS RULE
   ├─ Saves order via OrderRepository
   ├─ Updates customer.credit_limit ← BUSINESS RULE
   └─ Returns OrderEntity

4. Repository (repositories/order_repository.py)
   ├─ Converts OrderEntity → OrderModel
   ├─ Persists to database
   ├─ Converts OrderModel → OrderEntity
   └─ Returns entity

5. CLI (cli/commands.py)
   ├─ Receives OrderEntity from service
   ├─ Formats output for user
   └─ Displays: "✓ Order #456 created for $500"
```

**Key points:**
- Business rules in entities
- Workflow in service
- Data access in repository
- UI logic in CLI
- Each layer has clear responsibility

---

## **12. Summary Checklist**

When building a data-centric application, ensure:

- [ ] Entities are framework-independent
- [ ] All business rules are in entities
- [ ] Services orchestrate, don't duplicate rules
- [ ] Repositories always return/accept entities
- [ ] Models are just ORM, no logic
- [ ] CLI/GUI calls services, not repos
- [ ] Dependencies flow inward
- [ ] Core has no framework imports
- [ ] Tests work without database (for entities/services)
- [ ] Each layer has single responsibility

---