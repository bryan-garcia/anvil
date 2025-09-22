# Anvil

Anvil is a lightweight framework built on Haystack for experimenting with Retrieval-Augmented Generation (RAG) pipelines.  
It emphasizes registration, config-driven execution, and modularity, making it easy to build, share, and extend pipelines.

---

## Features

- Config-Driven Execution  
  Run pipelines from YAML/JSON config files — no hardcoding required.

- Serialization  
  Serialize built-in pipelines to editable configs, so you can quickly tweak component parameters.

- Pipeline Registration  
  Define and register pipelines in a central registry for easy discovery and execution by users/devs.

- CLI Interface  
  Use the `anvil` command to run pipelines, show registered ones, and inspect configs.

---