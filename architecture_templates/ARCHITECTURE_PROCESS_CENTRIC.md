# **PROJECT ARCHITECTURE - PROCESS-CENTRIC**

**META-DATA**
* **Project Name:** [PROJECT_NAME]
* **Last Updated:** [YYYY-MM-DD]
* **Status:** [Draft/Active/Deprecated]
* **Lead Architect:** [Name]

---

## **1. System Context (C1)**

**Goal:**  
[One sentence: What does this library process/transform and for whom?]

**Primary Use Cases:**
* **[Use Case 1]:** [What operation/transformation]
* **[Use Case 2]:** [What operation/transformation]
* **[Use Case 3]:** [What operation/transformation]

**Input/Output:**
* **Input:** [What data format does it accept?]
* **Output:** [What data format does it produce?]

**External Dependencies:**
* **[Library/Service 1]:** [Purpose]
* **[Library/Service 2]:** [Purpose]

---

## **2. Container Architecture (C2)**

**High-level processing view:**
```mermaid
C4Container
    title Container View - [PROJECT_NAME]
    
    %% Define your processing components
    %% Example:
    %% Person(user, "Developer", "Uses the library")
    %% Container(pipeline, "Processing Pipeline", "Python", "Orchestrates processing")
    %% Container(processor, "Processors", "Python", "Individual operations")
    %% Rel(user, pipeline, "Calls")
    %% Rel(pipeline, processor, "Uses")
```

**Component Descriptions:**

| Component | Technology | Responsibility |
|-----------|------------|----------------|
| [Name]    | [Stack]    | [What it processes] |
| [Name]    | [Stack]    | [What it processes] |

---

## **3. Technology Stack**

**Core Technologies:**
* **Language:** [Python 3.x]
* **Interfaces:** [CLI: Typer/Click | Library API | GUI (if applicable)]
* **Processing:** [Libraries for core operations]
* **I/O:** [File formats, protocols]
* **Testing:** [Pytest, unittest]

**Key Libraries:**
* [Library]: [Purpose in processing pipeline]
* [Library]: [Purpose in processing pipeline]

**Configuration:**
* **Settings:** [How processing is configured]
* **Extensibility:** [Plugin system, strategies]

---

## **4. Processing Model**

### **Core Operations**

List the main processing operations:

| Operation | Input | Output | Purpose |
|-----------|-------|--------|---------|
| [Op1]     | [Type] | [Type] | [What it does] |
| [Op2]     | [Type] | [Type] | [What it does] |
| [Op3]     | [Type] | [Type] | [What it does] |

### **Processing Workflows**

Describe typical workflows:
```
[Workflow 1]: [Name]
Input → [Step 1] → [Step 2] → [Step 3] → Output

[Workflow 2]: [Name]
Input → [Step A] → [Step B] → Output
```

---

## **5. Project-Specific Structure**

### **Source Code Organization**
```
src/{package_name}/core/
├── processors/
│   ├── [processor_1].py       # e.g., validator.py
│   ├── [processor_2].py       # e.g., transformer.py
│   ├── [processor_3].py       # e.g., formatter.py
│   └── ...
│
├── pipelines/
│   ├── [pipeline_1].py        # e.g., standard_pipeline.py
│   ├── [pipeline_2].py        # e.g., batch_pipeline.py
│   └── ...
│
├── strategies/
│   ├── [strategy_type_1]/     # e.g., sorting/
│   │   ├── [strategy_a].py
│   │   └── [strategy_b].py
│   ├── [strategy_type_2]/     # e.g., compression/
│   │   ├── [strategy_a].py
│   │   └── [strategy_b].py
│   └── ...
│
├── handlers/
│   ├── [handler_1].py         # e.g., error_handler.py
│   ├── [handler_2].py         # e.g., logging_handler.py
│   └── ...
│
└── interfaces/
    ├── processor.py           # Base processor interface
    ├── pipeline.py            # Base pipeline interface
    ├── strategy.py            # Base strategy interface
    └── ...
```

### **Supporting Modules**
```
src/{package_name}/
├── cli/
│   └── main.py               # CLI interface to pipelines
│
├── gui/
│   └── app.py                # GUI interface (if applicable)
│
└── utils/
    ├── config.py
    ├── io_helpers.py         # File reading/writing
    └── [utility].py
```

### **Test Organization**
```
tests/
├── unit/
│   ├── processors/
│   │   ├── test_[processor_1].py
│   │   └── test_[processor_2].py
│   │
│   ├── strategies/
│   │   └── test_[strategy].py
│   │
│   └── pipelines/
│       └── test_[pipeline].py
│
├── integration/
│   ├── [workflow_1]/
│   └── [workflow_2]/
│
└── performance/
    └── benchmark_[operation].py
```

---

## **6. Key Processing Strategies**

**Document the main algorithm choices:**

### **Strategy 1: [Name - e.g., "Sorting Strategy"]**
* **Purpose:** [What problem does it solve?]
* **Implementations:**
  - **[Option A]:** [Algorithm, when to use]
  - **[Option B]:** [Algorithm, when to use]
* **Selection Criteria:** [How to choose between options]

### **Strategy 2: [Name - e.g., "Compression Strategy"]**
* **Purpose:** [What problem does it solve?]
* **Implementations:**
  - **[Option A]:** [Algorithm, when to use]
  - **[Option B]:** [Algorithm, when to use]
* **Selection Criteria:** [How to choose between options]

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

## **8. Processing Flow**

**Describe typical processing flows:**

### **Example: [Operation Name - e.g., "Image Processing"]**
```
1. User → CLI/Library
2. CLI → Pipeline.execute(input_data)
3. Pipeline → Processor1.process(data)
4. Processor1 → Validates input
5. Pipeline → Processor2.process(data)
6. Processor2 → Transforms data
7. Pipeline → Strategy.apply(data)
8. Strategy → Selected algorithm processes data
9. Pipeline → Handler.log(result)
10. Pipeline → Returns processed output
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

**Performance Considerations:**
* [Memory constraints]
* [Processing time targets]
* [Scalability requirements]

---

## **10. Extension Points**

**How to extend this library:**

### **Custom Processors**
[How users can add custom processing steps]

### **Custom Strategies**
[How users can implement alternative algorithms]

### **Custom Pipelines**
[How users can compose new workflows]

---