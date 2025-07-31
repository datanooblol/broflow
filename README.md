# broflow

A workflow-agnostic library for building readable pipelines and workflows. Inspired by pocketflow, broflow provides a simple yet powerful framework for orchestrating complex data processing, ML pipelines, web scraping, and more.

**Learn once, use everywhere** - from data science to web automation, broflow adapts to your workflow needs.

## Key Features

- 🔄 **Sequential Workflows**: Chain actions with simple `>>` operator
- ⚡ **Parallel Execution**: Run independent actions simultaneously with `ParallelAction`
- 🔀 **Conditional Branching**: Route workflows based on action results
- 🌐 **Global State Management**: Share data across actions with built-in state
- 🛠️ **Tool Integration**: Built-in utilities for parameter validation and extraction
- 📊 **Visual Flow Charts**: Generate Mermaid diagrams of your workflows

## Quick Start

```python
from broflow import Action, Flow, Start, End

# Define your actions
class ProcessData(Action):
    def run(self, shared):
        shared['processed'] = shared['input'] * 2
        return shared

class SaveResult(Action):
    def run(self, shared):
        print(f"Saved: {shared['processed']}")
        return shared

# Build your workflow
start = Start("Processing pipeline")
process = ProcessData()
save = SaveResult()
end = End("Pipeline complete")

# Chain actions
start >> process >> save >> end

# Execute
flow = Flow(start)
flow.run({'input': 10})
```

## Parallel Processing

```python
from broflow.parallel_action import ParallelAction

# Run multiple actions simultaneously
parallel = ParallelAction(
    FeatureScaler(),
    TextVectorizer(),
    CategoryEncoder()
)

# Perfect for: ML feature engineering, data fetching, web scraping
start >> data_prep >> parallel >> merge_results >> end
```

## Use Cases

broflow excels in various domains:

### 🤖 Machine Learning
- Feature engineering pipelines
- Model training workflows
- Data preprocessing chains
- Hyperparameter optimization

### 🌐 Web Automation
- Multi-site web scraping
- API data aggregation
- Content processing pipelines
- Notification systems

### 📊 Data Processing
- ETL pipelines
- Data validation workflows
- Report generation
- Multi-source data integration

### 🔧 DevOps & Automation
- Deployment pipelines
- Testing workflows
- Monitoring systems
- Batch processing jobs

## Advanced Features

### Conditional Workflows
```python
class CheckData(Action):
    def run(self, shared):
        if shared['data_quality'] > 0.8:
            self.next_action = 'high_quality'
        else:
            self.next_action = 'needs_cleaning'
        return shared

checker = CheckData()
checker - 'high_quality' >> process_directly
checker - 'needs_cleaning' >> clean_data >> process_directly
```

### Global State & Configuration
```python
from broflow import state, load_config

# Load configuration
load_config('config.yaml')

# Access global state
debug_mode = state.get('debug', False)
state.set('api_key', 'your-key')
```

### Visual Workflow Documentation
```python
# Generate Mermaid flowchart
flow.save_mermaid('workflow.md')

# Creates visual documentation of your pipeline
```

## Installation

```bash
pip install broflow
```

## Documentation

- [Future Use Cases](FUTURE.md) - Comprehensive examples and patterns
- [API Reference](docs/) - Detailed API documentation
- [Examples](examples/) - Real-world workflow examples

## Why broflow?

**Readable**: Workflows read like natural language
```python
start >> load_data >> clean_data >> ParallelAction(feature1, feature2, feature3) >> train_model >> save_model >> end
```

**Flexible**: Adapts to any workflow pattern
- Sequential processing
- Parallel execution
- Conditional branching
- Mixed sync/async operations

**Debuggable**: Built-in state management and visual flow generation

**Scalable**: From simple scripts to complex production pipelines

## Contributing

Pending...

## License

MIT License - see [LICENSE](LICENSE) for details.
