# Version History

## 0.1.2 - Configuration Management
**Released:** TBD

### ✨ New Features
- Enhanced `config.py` with improved configuration management
- Added support for YAML configuration files alongside JSON
- Automatic parent directory creation for config files
- Better error handling for unsupported file formats

### 🔧 Improvements
- More robust file path handling using `pathlib.Path`
- Cleaner configuration loading and saving interface

---

## 0.1.1 - Parallel Processing
**Released:** TBD

### ✨ New Features
- Introduced `ParallelAction` class for concurrent execution
- Added support for running multiple actions simultaneously using asyncio
- Configurable result storage with custom result keys
- Automatic result collection and organization by action name

### 🔧 Improvements
- Enhanced workflow performance through parallel processing capabilities
- Better resource utilization for independent tasks

---

## 0.1.0 - Initial Release
**Released:** TBD

### 🎉 First Launch
- Core workflow orchestration framework
- Basic `Action`, `Flow`, `Start`, and `End` classes
- Sequential workflow chaining with `>>` operator
- Conditional branching with `-` operator
- Global state management system
- Mermaid diagram generation for workflow visualization
- Async workflow support with `action_async.py` and `flow_async.py`

### 🏗️ Foundation Features
- Lightweight, readable workflow syntax
- Extensible action system
- Built-in state sharing across workflow steps
- Framework-agnostic design
- Easy debugging and inspection capabilities