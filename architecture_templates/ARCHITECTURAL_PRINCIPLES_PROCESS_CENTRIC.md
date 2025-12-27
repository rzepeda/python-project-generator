# **PROCESS-CENTRIC ARCHITECTURAL PRINCIPLES**

*Reference guide for architects building process-oriented libraries and tools*

---

## **1. What is Process-Centric Architecture?**

**Process-Centric Architecture** focuses on transforming data through a series of operations and workflows.

**Best suited for:**
- Data processing libraries
- Transformation tools
- Parsers and compilers
- Image/audio/video processing
- Scientific computing
- ETL (Extract, Transform, Load) systems
- Command-line tools

**Core philosophy:** The workflow (how data flows and transforms) is the heart of the system.

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
├── README.md
├── agent_tools/                # Agent tooling (IMMUTABLE)
├── resources/                  # Prompts and templates
├── docs/                       # Knowledge base
└── workspace/                  # Agent sandbox (ignored)
```

### **Dynamic Areas (Architect Designs)**
```
src/{package_name}/
├── core/                       # Processing logic
│   ├── processors/             # Individual operations
│   ├── pipelines/              # Workflow orchestration
│   ├── strategies/             # Algorithm choices
│   ├── handlers/               # Cross-cutting concerns
│   └── interfaces/             # Contracts/protocols
├── cli/                        # Terminal interface
├── gui/                        # Graphical interface (optional)
└── utils/                      # Infrastructure

tests/
├── unit/                       # Unit tests
│   ├── processors/
│   ├── strategies/
│   └── pipelines/
├── integration/                # Integration tests
└── performance/                # Benchmarks
```

---

## **3. Architectural Principles**

### **The Composition Rule**

**Components should be composable:**
```
┌──────────────────────────────────────────┐
│ Pipeline (Orchestration)                 │  ← High level
│ - Defines workflow                       │
│ - Composes processors                    │
└───────────────┬──────────────────────────┘
                │ uses
                ↓
┌──────────────────────────────────────────┐
│ Processors (Operations)                  │  ← Middle level
│ - Individual transformations             │
│ - Stateless operations                   │
└───────────────┬──────────────────────────┘
                │ uses
                ↓
┌──────────────────────────────────────────┐
│ Strategies (Algorithms)                  │  ← Low level
│ - Swappable implementations              │
│ - Algorithm choices                      │
└──────────────────────────────────────────┘
```

**Critical principles:**
- Small, focused components
- Each does one thing well
- Easy to compose into pipelines
- Easy to test in isolation

---

## **4. Component Responsibilities**

### **Interfaces Layer** (`core/interfaces/`)

**Purpose:** Define contracts for all components

**Characteristics:**
- Abstract base classes or protocols
- Define method signatures
- Enable polymorphism
- Make testing easier

**Example:**
```python
# interfaces/processor.py
from abc import ABC, abstractmethod
from typing import Any

class Processor(ABC):
    """Base interface for all processors"""
    
    @abstractmethod
    def process(self, data: Any) -> Any:
        """
        Process input data and return result.
        
        Args:
            data: Input to process
            
        Returns:
            Processed output
        """
        pass
    
    @abstractmethod
    def validate_input(self, data: Any) -> bool:
        """
        Validate that input is acceptable for this processor.
        
        Args:
            data: Input to validate
            
        Returns:
            True if valid, False otherwise
        """
        pass
```
```python
# interfaces/strategy.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar('T')

class Strategy(ABC, Generic[T]):
    """Base interface for all strategies"""
    
    @abstractmethod
    def execute(self, data: T) -> T:
        """Execute the strategy on data"""
        pass
    
    @abstractmethod
    def name(self) -> str:
        """Return strategy name"""
        pass
```

**Key points:**
- All components implement interfaces
- Enables dependency injection
- Makes mocking easy
- Documents expected behavior

---

### **Processors Layer** (`core/processors/`)

**Purpose:** Individual, focused operations

**Characteristics:**
- Single responsibility
- Stateless (when possible)
- Input → Process → Output
- Composable

**Example - Data Processing:**
```python
# processors/validator.py
from ..interfaces.processor import Processor
from typing import Dict, Any

class DataValidator(Processor):
    """Validates data structure and types"""
    
    def __init__(self, schema: Dict[str, type]):
        self.schema = schema
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data against schema"""
        if not self.validate_input(data):
            raise ValueError("Invalid data structure")
        
        for field, expected_type in self.schema.items():
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
            
            if not isinstance(data[field], expected_type):
                raise TypeError(
                    f"Field {field} should be {expected_type}, "
                    f"got {type(data[field])}"
                )
        
        return data
    
    def validate_input(self, data: Any) -> bool:
        return isinstance(data, dict)
```
```python
# processors/transformer.py
from ..interfaces.processor import Processor
from typing import Dict, Any, Callable

class DataTransformer(Processor):
    """Transforms data fields"""
    
    def __init__(self, transformations: Dict[str, Callable]):
        """
        Args:
            transformations: Map of field names to transformation functions
        """
        self.transformations = transformations
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply transformations to specified fields"""
        result = data.copy()
        
        for field, transform_func in self.transformations.items():
            if field in result:
                result[field] = transform_func(result[field])
        
        return result
    
    def validate_input(self, data: Any) -> bool:
        return isinstance(data, dict)
```
```python
# processors/filter.py
from ..interfaces.processor import Processor
from typing import List, Dict, Any, Callable

class DataFilter(Processor):
    """Filters data based on predicate"""
    
    def __init__(self, predicate: Callable[[Dict[str, Any]], bool]):
        self.predicate = predicate
    
    def process(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter items that match predicate"""
        return [item for item in data if self.predicate(item)]
    
    def validate_input(self, data: Any) -> bool:
        return isinstance(data, list)
```

**Example - Image Processing:**
```python
# processors/resize.py
from ..interfaces.processor import Processor
from PIL import Image

class ResizeProcessor(Processor):
    """Resizes images"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
    
    def process(self, image: Image.Image) -> Image.Image:
        """Resize image to specified dimensions"""
        return image.resize((self.width, self.height))
    
    def validate_input(self, data: Any) -> bool:
        return isinstance(data, Image.Image)
```
```python
# processors/grayscale.py
from ..interfaces.processor import Processor
from PIL import Image

class GrayscaleProcessor(Processor):
    """Converts images to grayscale"""
    
    def process(self, image: Image.Image) -> Image.Image:
        """Convert to grayscale"""
        return image.convert('L')
    
    def validate_input(self, data: Any) -> bool:
        return isinstance(data, Image.Image)
```

**Key points:**
- One clear responsibility
- Minimal dependencies
- Easy to test
- Reusable across pipelines

---

### **Strategies Layer** (`core/strategies/`)

**Purpose:** Interchangeable algorithms for the same problem

**Characteristics:**
- Same interface, different implementations
- Swappable at runtime
- Encapsulate algorithm details
- User chooses based on needs

**Example - Sorting Strategies:**
```python
# strategies/sorting/base.py
from ...interfaces.strategy import Strategy
from typing import List, TypeVar

T = TypeVar('T')

class SortStrategy(Strategy[List[T]]):
    """Base for all sorting strategies"""
    
    @abstractmethod
    def execute(self, data: List[T]) -> List[T]:
        """Sort the data"""
        pass
```
```python
# strategies/sorting/quick_sort.py
from .base import SortStrategy
from typing import List, TypeVar

T = TypeVar('T')

class QuickSortStrategy(SortStrategy[T]):
    """Quick sort - fast for large datasets"""
    
    def execute(self, data: List[T]) -> List[T]:
        """Quick sort implementation"""
        if len(data) <= 1:
            return data
        
        pivot = data[len(data) // 2]
        left = [x for x in data if x < pivot]
        middle = [x for x in data if x == pivot]
        right = [x for x in data if x > pivot]
        
        return self.execute(left) + middle + self.execute(right)
    
    def name(self) -> str:
        return "QuickSort"
```
```python
# strategies/sorting/merge_sort.py
from .base import SortStrategy
from typing import List, TypeVar

T = TypeVar('T')

class MergeSortStrategy(SortStrategy[T]):
    """Merge sort - stable, good for partially sorted data"""
    
    def execute(self, data: List[T]) -> List[T]:
        """Merge sort implementation"""
        if len(data) <= 1:
            return data
        
        mid = len(data) // 2
        left = self.execute(data[:mid])
        right = self.execute(data[mid:])
        
        return self._merge(left, right)
    
    def _merge(self, left: List[T], right: List[T]) -> List[T]:
        result = []
        i = j = 0
        
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        
        result.extend(left[i:])
        result.extend(right[j:])
        return result
    
    def name(self) -> str:
        return "MergeSort"
```

**Example - Compression Strategies:**
```python
# strategies/compression/base.py
from ...interfaces.strategy import Strategy

class CompressionStrategy(Strategy[bytes]):
    """Base for compression strategies"""
    
    @abstractmethod
    def execute(self, data: bytes) -> bytes:
        """Compress the data"""
        pass
```
```python
# strategies/compression/gzip.py
import gzip
from .base import CompressionStrategy

class GzipCompression(CompressionStrategy):
    """Gzip compression - good compression ratio"""
    
    def __init__(self, level: int = 9):
        self.level = level
    
    def execute(self, data: bytes) -> bytes:
        return gzip.compress(data, compresslevel=self.level)
    
    def name(self) -> str:
        return f"Gzip(level={self.level})"
```
```python
# strategies/compression/lz4.py
import lz4.frame
from .base import CompressionStrategy

class LZ4Compression(CompressionStrategy):
    """LZ4 compression - very fast"""
    
    def execute(self, data: bytes) -> bytes:
        return lz4.frame.compress(data)
    
    def name(self) -> str:
        return "LZ4"
```

**Key points:**
- Implement same interface
- User chooses algorithm
- Easy to add new strategies
- Testable independently

---

### **Pipelines Layer** (`core/pipelines/`)

**Purpose:** Orchestrate processing workflows

**Characteristics:**
- Chains processors together
- Defines execution order
- Manages data flow
- Can be linear, branching, or conditional

**Example - Simple Sequential Pipeline:**
```python
# pipelines/sequential_pipeline.py
from ..interfaces.processor import Processor
from ..interfaces.pipeline import Pipeline
from typing import List, Any

class SequentialPipeline(Pipeline):
    """Execute processors in sequence"""
    
    def __init__(self, processors: List[Processor]):
        self.processors = processors
    
    def execute(self, data: Any) -> Any:
        """Run data through all processors"""
        result = data
        
        for processor in self.processors:
            if not processor.validate_input(result):
                raise ValueError(
                    f"{processor.__class__.__name__} received invalid input"
                )
            result = processor.process(result)
        
        return result
    
    def add_processor(self, processor: Processor) -> None:
        """Add processor to end of pipeline"""
        self.processors.append(processor)
```

**Example - Pipeline with Strategies:**
```python
# pipelines/configurable_pipeline.py
from ..interfaces.processor import Processor
from ..interfaces.strategy import Strategy
from ..interfaces.pipeline import Pipeline
from typing import Any

class ConfigurablePipeline(Pipeline):
    """Pipeline with injected strategies"""
    
    def __init__(
        self,
        preprocessors: List[Processor],
        strategy: Strategy,
        postprocessors: List[Processor]
    ):
        self.preprocessors = preprocessors
        self.strategy = strategy
        self.postprocessors = postprocessors
    
    def execute(self, data: Any) -> Any:
        """Execute pipeline with strategy"""
        # Preprocessing
        result = data
        for processor in self.preprocessors:
            result = processor.process(result)
        
        # Apply strategy
        result = self.strategy.execute(result)
        
        # Postprocessing
        for processor in self.postprocessors:
            result = processor.process(result)
        
        return result
```

**Example - Parallel Processing Pipeline:**
```python
# pipelines/parallel_pipeline.py
from ..interfaces.processor import Processor
from ..interfaces.pipeline import Pipeline
from concurrent.futures import ThreadPoolExecutor
from typing import List, Any

class ParallelPipeline(Pipeline):
    """Execute processors in parallel"""
    
    def __init__(self, processors: List[Processor], max_workers: int = 4):
        self.processors = processors
        self.max_workers = max_workers
    
    def execute(self, data: List[Any]) -> List[Any]:
        """Process data items in parallel"""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Each processor processes all data
            for processor in self.processors:
                data = list(executor.map(processor.process, data))
        
        return data
```

**Example - Conditional Pipeline:**
```python
# pipelines/conditional_pipeline.py
from ..interfaces.processor import Processor
from ..interfaces.pipeline import Pipeline
from typing import Callable, Any

class ConditionalPipeline(Pipeline):
    """Execute processors based on conditions"""
    
    def __init__(self):
        self.branches = []
    
    def add_branch(
        self,
        condition: Callable[[Any], bool],
        processors: List[Processor]
    ):
        """Add conditional branch"""
        self.branches.append((condition, processors))
    
    def execute(self, data: Any) -> Any:
        """Execute matching branch"""
        result = data
        
        for condition, processors in self.branches:
            if condition(data):
                for processor in processors:
                    result = processor.process(result)
                break
        
        return result
```

**Key points:**
- Orchestrates workflow
- Manages execution order
- Can inject strategies
- Handles error propagation

---

### **Handlers Layer** (`core/handlers/`)

**Purpose:** Handle cross-cutting concerns

**Characteristics:**
- Error handling
- Logging
- Retries
- Events
- Monitoring

**Example - Error Handler:**
```python
# handlers/error_handler.py
import logging
from typing import Callable, Any, Type
from functools import wraps

class ErrorHandler:
    """Handles errors during processing"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def handle(
        self,
        error: Exception,
        context: dict,
        reraise: bool = True
    ) -> None:
        """Handle an error"""
        self.logger.error(
            f"Error during processing: {error}",
            extra=context
        )
        
        # Could send notifications, save to file, etc.
        
        if reraise:
            raise
    
    def wrap(
        self,
        operation: Callable,
        error_types: tuple = (Exception,)
    ) -> Callable:
        """Wrap operation with error handling"""
        @wraps(operation)
        def wrapper(*args, **kwargs):
            try:
                return operation(*args, **kwargs)
            except error_types as e:
                self.handle(
                    e,
                    {
                        "operation": operation.__name__,
                        "args": args,
                        "kwargs": kwargs
                    }
                )
        return wrapper
```

**Example - Retry Handler:**
```python
# handlers/retry_handler.py
import time
import logging
from typing import Callable, Type, Tuple

class RetryHandler:
    """Handles retrying failed operations"""
    
    def __init__(
        self,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        logger: logging.Logger = None
    ):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.logger = logger or logging.getLogger(__name__)
    
    def execute_with_retry(
        self,
        operation: Callable,
        *args,
        retryable_errors: Tuple[Type[Exception], ...] = (Exception,),
        **kwargs
    ):
        """Execute operation with retry logic"""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return operation(*args, **kwargs)
            except retryable_errors as e:
                last_exception = e
                
                if attempt < self.max_retries - 1:
                    wait_time = self.backoff_factor ** attempt
                    self.logger.warning(
                        f"Attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
                else:
                    self.logger.error(
                        f"All {self.max_retries} attempts failed"
                    )
        
        raise last_exception
```

**Example - Progress Handler:**
```python
# handlers/progress_handler.py
from typing import Callable, Any
from tqdm import tqdm

class ProgressHandler:
    """Handles progress tracking"""
    
    def __init__(self, show_progress: bool = True):
        self.show_progress = show_progress
    
    def track(
        self,
        items: list,
        description: str = "Processing"
    ) -> tqdm:
        """Create progress bar for items"""
        if self.show_progress:
            return tqdm(items, desc=description)
        return items
    
    def wrap_pipeline(
        self,
        pipeline: 'Pipeline',
        description: str = "Pipeline"
    ) -> Callable:
        """Wrap pipeline with progress tracking"""
        def tracked_execute(data):
            with tqdm(
                total=len(pipeline.processors),
                desc=description
            ) as pbar:
                result = data
                for processor in pipeline.processors:
                    result = processor.process(result)
                    pbar.update(1)
                return result
        
        return tracked_execute
```

**Key points:**
- Handle cross-cutting concerns
- Don't duplicate in each processor
- Can wrap operations
- Improve observability

---

## **5. Design Patterns**

### **Pipeline Pattern**

**Problem:** Need to chain operations in sequence

**Solution:** Pipeline orchestrates processors
```python
# Create pipeline
pipeline = SequentialPipeline([
    DataValidator(schema),
    DataTransformer(transformations),
    DataFilter(predicate),
    DataExporter(format="json")
])

# Execute
result = pipeline.execute(input_data)
```

---

### **Strategy Pattern**

**Problem:** Need different algorithms for same problem

**Solution:** Define strategy interface, provide implementations
```python
# User chooses strategy
if dataset_size > 10000:
    strategy = QuickSortStrategy()
else:
    strategy = MergeSortStrategy()

# Use in pipeline
pipeline = ConfigurablePipeline(
    preprocessors=[validator, normalizer],
    strategy=strategy,
    postprocessors=[formatter]
)
```

---

### **Chain of Responsibility**

**Problem:** Multiple handlers might process data

**Solution:** Chain handlers, each decides if it handles
```python
class Handler(ABC):
    def __init__(self):
        self.next_handler = None
    
    def set_next(self, handler: 'Handler'):
        self.next_handler = handler
        return handler
    
    @abstractmethod
    def handle(self, data):
        if self.next_handler:
            return self.next_handler.handle(data)
        return data

# Chain
handler1.set_next(handler2).set_next(handler3)
result = handler1.handle(data)
```

---

### **Builder Pattern**

**Problem:** Complex pipeline configuration

**Solution:** Fluent builder interface
```python
class PipelineBuilder:
    def __init__(self):
        self.processors = []
        self.strategy = None
        self.handlers = []
    
    def add_processor(self, processor):
        self.processors.append(processor)
        return self
    
    def with_strategy(self, strategy):
        self.strategy = strategy
        return self
    
    def add_handler(self, handler):
        self.handlers.append(handler)
        return self
    
    def build(self):
        return ConfigurablePipeline(
            processors=self.processors,
            strategy=self.strategy,
            handlers=self.handlers
        )

# Usage
pipeline = (PipelineBuilder()
    .add_processor(DataValidator(schema))
    .add_processor(DataTransformer(transforms))
    .with_strategy(QuickSortStrategy())
    .add_handler(ErrorHandler(logger))
    .build())
```

---

## **6. Testing Strategy**

### **Unit Tests - Processors (Isolated)**
```python
# tests/unit/processors/test_validator.py
from src.core.processors.validator import DataValidator

def test_validator_valid_data():
    """Test processor with valid data"""
    schema = {"name": str, "age": int}
    validator = DataValidator(schema)
    
    data = {"name": "John", "age": 30}
    result = validator.process(data)
    
    assert result == data

def test_validator_missing_field():
    """Test processor with invalid data"""
    schema = {"name": str, "age": int}
    validator = DataValidator(schema)
    
    data = {"name": "John"}  # Missing age
    
    with pytest.raises(ValueError, match="Missing required field"):
        validator.process(data)

def test_validator_wrong_type():
    """Test type validation"""
    schema = {"name": str, "age": int}
    validator = DataValidator(schema)
    
    data = {"name": "John", "age": "thirty"}  # Wrong type
    
    with pytest.raises(TypeError):
        validator.process(data)
```

---

### **Unit Tests - Strategies (Isolated)**
```python
# tests/unit/strategies/test_sorting.py
from src.core.strategies.sorting.quick_sort import QuickSortStrategy
from src.core.strategies.sorting.merge_sort import MergeSortStrategy

def test_quick_sort():
    """Test quick sort strategy"""
    strategy = QuickSortStrategy()
    data = [3, 1, 4, 1, 5, 9, 2, 6]
    
    result = strategy.execute(data)
    
    assert result == [1, 1, 2, 3, 4, 5, 6, 9]

def test_merge_sort():
    """Test merge sort strategy"""
    strategy = MergeSortStrategy()
    data = [3, 1, 4, 1, 5, 9, 2, 6]
    
    result = strategy.execute(data)
    
    assert result == [1, 1, 2, 3, 4, 5, 6, 9]

def test_strategies_equivalent():
    """Test all strategies produce same result"""
    data = [3, 1, 4, 1, 5, 9, 2, 6]
    expected = [1, 1, 2, 3, 4, 5, 6, 9]
    
    strategies = [QuickSortStrategy(), MergeSortStrategy()]
    
    for strategy in strategies:
        result = strategy.execute(data.copy())
        assert result == expected
```

---

### **Integration Tests - Pipelines**
```python
# tests/integration/test_data_pipeline.py
from src.core.pipelines.sequential_pipeline import SequentialPipeline
from src.core.processors.validator import DataValidator
from src.core.processors.transformer import DataTransformer
from src.core.processors.filter import DataFilter

def test_complete_pipeline():
    """Test full pipeline workflow"""
    # Setup
    schema = {"name": str, "age": int, "score": float}
    
    transformations = {
        "name": str.upper,
        "score": lambda x: round(x, 2)
    }
    
    predicate = lambda item: item["age"] >= 18
    
    # Build pipeline
    pipeline = SequentialPipeline([
        DataValidator(schema),
        DataTransformer(transformations),
        DataFilter(predicate)
    ])
    
    # Test data
    data = [
        {"name": "john", "age": 25, "score": 85.678},
        {"name": "jane", "age": 17, "score": 92.345},
        {"name": "bob", "age": 30, "score": 78.901}
    ]
    
    # Execute
    result = pipeline.execute(data)
    
    # Verify
    assert len(result) == 2  # Filtered out age < 18
    assert result[0]["name"] == "JOHN"  # Transformed
    assert result[0]["score"] == 85.68  # Rounded
    assert result[1]["name"] == "BOB"
```

---

### **Performance Tests - Benchmarks**
```python
# tests/performance/benchmark_sorting.py
import pytest
from src.core.strategies.sorting.quick_sort import QuickSortStrategy
from src.core.strategies.sorting.merge_sort import MergeSortStrategy
import random
import time

@pytest.mark.parametrize("size", [100, 1000, 10000])
def test_sorting_performance(size, benchmark):
    """Benchmark sorting strategies"""
    data = [random.randint(0, 1000) for _ in range(size)]
    
    quick_sort = QuickSortStrategy()
    merge_sort = MergeSortStrategy()
    
    # Benchmark QuickSort
    start = time.time()
    quick_sort.execute(data.copy())
    quick_time = time.time() - start
    
    # Benchmark MergeSort
    start = time.time()
    merge_sort.execute(data.copy())
    merge_time = time.time() - start
    
    print(f"\nSize {size}:")
    print(f"  QuickSort: {quick_time:.4f}s")
    print(f"  MergeSort: {merge_time:.4f}s")
```

---

## **7. Common Anti-Patterns to Avoid**

### ❌ **Anti-Pattern 1: Processors with Side Effects**
```python
# BAD - Processor modifies global state
class BadProcessor(Processor):
    results = []  # Class variable!
    
    def process(self, data):
        self.results.append(data)  # Side effect!
        return data
```

**Fix:** Keep processors pure
```python
# GOOD - Pure function
class GoodProcessor(Processor):
    def process(self, data):
        # No side effects, just transformation
        return transform(data)
```

---

### ❌ **Anti-Pattern 2: Pipeline with Hardcoded Processors**
```python
# BAD - Can't customize
class BadPipeline:
    def execute(self, data):
        data = ValidatorProcessor().process(data)
        data = TransformerProcessor().process(data)
        return data
```

**Fix:** Inject processors
```python
# GOOD - Configurable
class GoodPipeline:
    def __init__(self, processors):
        self.processors = processors
    
    def execute(self, data):
        result = data
        for processor in self.processors:
            result = processor.process(result)
        return result
```

---

### ❌ **Anti-Pattern 3: Strategy Without Interface**
```python
# BAD - No common interface
class QuickSort:
    def quick_sort(self, data):  # Different method name!
        pass

class MergeSort:
    def merge_sort(self, data):  # Different method name!
        pass
```

**Fix:** Use common interface
```python
# GOOD - Same interface
class QuickSort(SortStrategy):
    def execute(self, data):  # Same method
        pass

class MergeSort(SortStrategy):
    def execute(self, data):  # Same method
        pass
```

---

### ❌ **Anti-Pattern 4: Complex Processor Logic**
```python
# BAD - Doing too much
class BadProcessor(Processor):
    def process(self, data):
        # Validate
        if not self.validate(data):
            raise ValueError()
        
        # Transform
        data = self.transform(data)
        
        # Filter
        data = self.filter(data)
        
        # Export
        self.export(data)
        
        return data
```

**Fix:** Split into focused processors
```python
# GOOD - Single responsibility
class ValidateProcessor(Processor):
    def process(self, data):
        if not self.validate(data):
            raise ValueError()
        return data

class TransformProcessor(Processor):
    def process(self, data):
        return self.transform(data)

# Compose in pipeline
pipeline = SequentialPipeline([
    ValidateProcessor(),
    TransformProcessor(),
    FilterProcessor(),
    ExportProcessor()
])
```

---

## **8. Decision Framework**

### **Where Does This Code Go?**
```
Is it a contract/interface?
├─ YES → interfaces/
│
└─ NO → Is it a single operation?
    ├─ YES → processors/
    │
    └─ NO → Is it an alternative algorithm?
        ├─ YES → strategies/
        │
        └─ NO → Is it workflow orchestration?
            ├─ YES → pipelines/
            │
            └─ NO → Is it cross-cutting concern?
                ├─ YES → handlers/
                │
                └─ NO → Infrastructure (utils/)
```

### **Specific Examples:**

| Code | Location | Reason |
|------|----------|--------|
| "Validate data structure" | Processor | Single operation |
| "QuickSort vs MergeSort" | Strategy | Algorithm choice |
| "Validate → Transform → Export" | Pipeline | Workflow |
| "Retry failed operations" | Handler | Cross-cutting |
| "Processor interface" | Interface | Contract |
| "Read file" | Utils | Infrastructure |

---

## **9. Best Practices**

### **Processor Design**

✅ **DO:**
- Keep processors small and focused
- Make them stateless when possible
- Validate input
- Return new data (don't mutate)
- Follow single responsibility

❌ **DON'T:**
- Mix multiple concerns
- Store state in instance
- Access global variables
- Perform I/O in core logic

---

### **Strategy Design**

✅ **DO:**
- Implement common interface
- Document when to use each
- Make them swappable
- Include algorithm name

❌ **DON'T:**
- Use different method names
- Hardcode in pipelines
- Mix unrelated algorithms

---

### **Pipeline Design**

✅ **DO:**
- Accept processors as arguments
- Validate between steps
- Handle errors gracefully
- Support composition

❌ **DON'T:**
- Hardcode processors
- Ignore validation errors
- Make assumptions about data
- Tightly couple steps

---

### **Handler Design**

✅ **DO:**
- Keep orthogonal to business logic
- Make optional/configurable
- Chain when appropriate
- Log important events

❌ **DON'T:**
- Mix with processing logic
- Make mandatory
- Swallow errors silently
- Duplicate across processors

---

## **10. Extension Patterns**

### **Adding Custom Processors**
```python
# User creates custom processor
from library.interfaces.processor import Processor

class MyCustomProcessor(Processor):
    def process(self, data):
        # Custom logic
        return modified_data
    
    def validate_input(self, data):
        return isinstance(data, dict)

# Use in pipeline
pipeline = SequentialPipeline([
    StandardProcessor(),
    MyCustomProcessor(),  # User's processor
    AnotherProcessor()
])
```

---

### **Adding Custom Strategies**
```python
# User implements custom strategy
from library.interfaces.strategy import SortStrategy

class MyCustomSort(SortStrategy):
    def execute(self, data):
        # Custom sorting algorithm
        return sorted_data
    
    def name(self):
        return "MyCustomSort"

# Use in configurable pipeline
pipeline = ConfigurablePipeline(
    preprocessors=[...],
    strategy=MyCustomSort(),  # User's strategy
    postprocessors=[...]
)
```

---

### **Plugin System**
```python
# core/plugin_manager.py
class PluginManager:
    def __init__(self):
        self.processors = {}
        self.strategies = {}
    
    def register_processor(self, name: str, processor_class):
        self.processors[name] = processor_class
    
    def register_strategy(self, name: str, strategy_class):
        self.strategies[name] = strategy_class
    
    def create_processor(self, name: str, **kwargs):
        if name not in self.processors:
            raise ValueError(f"Unknown processor: {name}")
        return self.processors[name](**kwargs)
    
    def create_strategy(self, name: str, **kwargs):
        if name not in self.strategies:
            raise ValueError(f"Unknown strategy: {name}")
        return self.strategies[name](**kwargs)

# Usage
manager = PluginManager()
manager.register_processor("custom", MyCustomProcessor)

processor = manager.create_processor("custom", param=value)
```

---

## **11. Example Complete Flow**

### **Scenario: Process CSV data**
```
1. User calls library with CSV file

2. CLI/Library Entry Point
   ├─ Reads file
   ├─ Creates pipeline with user config
   └─ Calls pipeline.execute(data)

3. Pipeline (Data Processing)
   ├─ Step 1: ValidateProcessor
   │   └─ Checks schema, types
   │
   ├─ Step 2: TransformProcessor
   │   └─ Applies user transformations
   │
   ├─ Step 3: SortStrategy (injected)
   │   └─ Sorts using chosen algorithm
   │
   ├─ Step 4: FilterProcessor
   │   └─ Removes unwanted rows
   │
   └─ Step 5: ExportProcessor
       └─ Converts to output format

4. Handlers (Throughout)
   ├─ ErrorHandler: Catches exceptions
   ├─ ProgressHandler: Shows progress bar
   └─ LogHandler: Logs each step

5. Returns processed data to user
```

**Key points:**
- Each processor focused
- Strategy injected by user
- Handlers add observability
- Pipeline orchestrates all

---

## **12. Summary Checklist**

When building a process-centric library, ensure:

- [ ] Processors are small and focused
- [ ] Each processor does one thing well
- [ ] Strategies provide algorithm choices
- [ ] Pipelines orchestrate workflows
- [ ] Handlers manage cross-cutting concerns
- [ ] All components implement interfaces
- [ ] Components are composable
- [ ] Easy to test in isolation
- [ ] Users can extend with custom components
- [ ] No hardcoded workflows

---