# WrapConfig

WrapConfig is a lightweight and flexible Python configuration management library that simplifies the handling of configuration data. It provides a consistent API to manage settings in various formats, including JSON, YAML, and TOML, as well as in-memory configurations.

> **Note:** YAML and TOML support are optional. Install the extras if you need them.

---

## Features

- **Simple API:** Easily set, get, update, fill, and clear configuration values.
- **Multiple Formats:** Built-in support for JSON file-based configurations with optional YAML and TOML.
- **Nested Configurations:** Manage complex, nested configuration structures effortlessly.
- **In-Memory Configurations:** Use configurations without persisting data to disk.
- **Sub-Configurations:** Access and manipulate subsections of your configuration data via a dedicated `SubConfig` class.

---

## Installation

You can install WrapConfig using pip:

```bash
pip install WrapConfig
```

For optional YAML or TOML support, install with the corresponding extras:

```bash
pip install WrapConfig[yaml]
pip install WrapConfig[toml]
```

To install all optional features:

```bash
pip install WrapConfig[all]
```

## Usage

### Basic Example with JSON Configuration

Below is an example of how to use WrapConfig with a JSON configuration file:

```python
from wrapconfig import JSONWrapConfig

# Initialize the configuration manager with a JSON file path
config = JSONWrapConfig("config.json")

# Set configuration values using nested keys
config.set("database", "host", value="localhost")
config.set("database", "port", value=5432)

# Retrieve configuration values
db_host = config.get("database", "host")
db_port = config.get("database", "port")
print(f"Database Host: {db_host}, Port: {db_port}")

# Update configuration with multiple values at once
config.update({
    "logging": {
        "level": "DEBUG",
        "file": "app.log"
    }
})

# Save changes (if auto-save is disabled, you can manually call save)
config.save()
```

### In-Memory Configuration

If you prefer not to persist configuration data to a file, you can use the in-memory configuration:

```python
from wrapconfig import InMemoryConfig

# Create an in-memory configuration instance
config = InMemoryConfig()

# Set and save configuration values
config.set("feature_flag", value=True)
config.save()

# Clear current configuration and restore from backup
config.clear()
config.load()
print("Feature Flag:", config.get("feature_flag"))
```

### Using YAML and TOML Configurations

After installing the optional dependencies, you can work with YAML or TOML configuration files.

#### YAML Example

```python
from wrapconfig import YAMLWrapConfig

# Initialize the YAML configuration manager

config = YAMLWrapConfig("config.yaml")

# Set values and save to the YAML file

config.set("app", "name", value="MyApp")
config.save()
```

#### TOML Example

```python

from wrapconfig import TOMLWrapConfig

# Initialize the TOML configuration manager

config = TOMLWrapConfig("config.toml")

# Set values and save to the TOML file

config.set("server", "host", value="127.0.0.1")
config.save()
```

## API Overview

### Core Class: `WrapConfig`

WrapConfig is the abstract base class providing the core functionality:

- `set(*keys, value, save=True)`\
  Sets a configuration value using nested keys.
  Example: config.set("section", "subsection", value="my_value")
  If no value is provided as a keyword, the last key is assumed to be the value. In any case at least 2 arguments have to be passed.

- `get(*keys, default=None)`\
  Retrieves a configuration value using a nested key path. Returns default if the key does not exist.
  Example: value = config.get("section", "subsection", default="default_value")

* `update(data, save=True)`\
  Deeply updates the configuration with new data, adding new keys or updating existing ones.

* `fill(data, save=True)`\
  Fills in missing configuration values without overwriting existing ones.

* `clear(*keys)`\
  Clears configuration values. Without keys, it clears the entire configuration.

`data` **property**\
Returns a deep copy of the current configuration data.

### Sub-Configuration: `SubConfig`

SubConfig represents a subsection of a parent configuration. It allows you to work with nested configuration sections without having to access the full path. It works as a view to the parents data, so changing values is also manipulating the parent data structure. Note that SubConfig delegates persistence to its parent and does not support direct loading.

## Contributing

Contributions to WrapConfig are welcome! If you have suggestions, bug reports, or improvements, please follow these steps:

1. Fork the repository.
2. Create a feature branch:

   ```bash
   git checkout -b feature/my-feature
   ```

3. Commit your changes:
   ```bash
   git commit -am 'Add some feature'
   ```
4. Push to the branch:

   ```bash
   git push origin feature/my-feature
   ```

5. Open a Pull Request explaining your changes.

## License

WrapConfig is distributed under the MIT License. See the [LICENSE](./LICENSE) file for details.
