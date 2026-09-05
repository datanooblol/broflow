# Version History

## 0.2.0 - Register Pattern Rewrite
**Released:** TBD

### 💥 Breaking Changes
- Replaced the `Action` / `Flow` / `>>` / `-` chaining model entirely with the register
  pattern: `BaseTask`, `TaskRegistry`, `Flow`. This is a full rewrite of the public API,
  not an incremental change.
- Removed `Action`, `Start`, `End`, `ParallelAction`, `state` (the global `GlobalState`
  singleton), `load_config`/`save_config`, and both async modules (`action_async.py`,
  `flow_async.py`). None of these exist in 0.2.0 — there is no compatibility shim.
- Workflow steps are no longer wired together ahead of time with `>>`/`-`. Each step is a
  `BaseTask` subclass registered into a `TaskRegistry` under an identifier (an enum,
  string, or any hashable value), and decides its own next step live, at runtime, by
  calling `self.set_next(...)` inside `__call__`.

### ✨ New Features
- **`BaseTask`** — the entire step contract: receive input, do the work, call
  `set_next(...)` to say what comes next.
- **`TaskRegistry`** — a flat identifier → task lookup. Tasks never hold references to
  each other, so nothing needs to exist yet at the point a task names where it's going.
- **`Flow`** — runs a registered flow from a `start` identifier to an `end` value,
  following whatever each task decides live. Because there's no static graph to keep
  consistent, this naturally supports loops and multi-turn flows (a step can route back
  to an earlier step) that the old chained model could not express safely.
- **`Flow.trace`** — every run records the real `(task_name, next)` sequence actually
  taken (controlled by `show_trace`, default `True`), reset at the start of each `run()`
  call. No separate tracing setup needed to see what a specific run actually did.
- **`broflow.visualize`: `to_edges`, `to_tree`, `to_mermaid`** — three ways to inspect
  the *possible* shape of a flow, built from each task's optional `possible_next`
  metadata: a flat, sorted, git-diffable edge list; a plain indented text tree with no
  rendering dependency; and a Mermaid flowchart. `to_mermaid` draws a dashed edge
  (`-.->`) out of any task with more than one `possible_next`, to mark real branch
  points apart from a task with exactly one path forward (solid `-->`).

### 🪶 Lightweight by Design
- Zero third-party dependencies — `dependencies = []` in `pyproject.toml`. Everything is
  built on the Python standard library (`abc`, `typing`, `enum`, `dataclasses`).
- No server, no scheduler, no external state store. A flow is plain Python objects,
  run in-process, start to finish.

### 🎯 Why
- The old chained-successor model declares its whole set of possible edges up front,
  which can't represent a step choosing its next step from live, runtime-only
  information (an agent router picking a tool, a retry loop, a multi-turn conversation)
  without deadlocking on its own bookkeeping. The register pattern removes that
  limitation by not tracking predecessors at all — at the cost of the old model's
  fan-out/join capability, traded away deliberately in favor of one smaller, more
  focused core.

---

## 0.1.5 - Minor Fix
**Released:** TBD

### 🐛 Bug Fixes
- Minor bug fixes and improvements

---

## 0.1.4 - Mermaid Diagram Fix
**Released:** TBD

### 🐛 Bug Fixes
- **Fixed Mermaid diagram generation for conditional branching**: Resolved AttributeError when generating Mermaid diagrams for workflows with actions that have only alternative branches (no default successors)
- Enhanced `Flow.to_mermaid()` method to properly handle all successor scenarios:
  - Actions with only default successors
  - Actions with only alternative successors (e.g., `action - "branch_name" >> next_action`)
  - Actions with both default and alternative successors
  - Actions with no successors

### 🔧 Technical Details
- Added proper validation for `successors` attribute existence before iteration
- Improved error handling for `Relation` objects in workflow traversal
- Enhanced robustness of visual workflow documentation generation

---

## 0.1.3 - Enhanced Type Flexibility
**Released:** TBD

### 🔧 Breaking Changes
- **Shared Object Type Enhancement**: The shared object parameter in action methods is no longer restricted to `Dict[str, Any]`. Users can now utilize any data type that best suits their workflow requirements, providing greater flexibility in state management and data passing between actions.

### 🎯 Benefits
- Improved developer experience with more flexible data structures
- Enhanced type safety when using custom objects
- Better alignment with diverse workflow patterns and use cases

---

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