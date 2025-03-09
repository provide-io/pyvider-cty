In Pyvider, schema fragments, schemas, and meta schemas are fundamental building blocks that enable the framework to define, validate, and evolve infrastructure-as-code (IaC) components dynamically. This mirrors Terraform’s provider schema model but with a Pythonic, composable approach.

---

### **1. Schema Fragments (Building Blocks)**

**Definition**:  
Schema fragments are **modular, reusable schema definitions** that represent portions of a larger schema. These fragments can be composed into complete schemas, allowing for granular control and dynamic expansion of resource and provider configurations.

**Purpose**:  
- Facilitate **schema reusability** across multiple resources.  
- Allow **incremental growth** by appending fragments conditionally (runtime-driven schema evolution).  
- Represent **nested blocks** in Terraform HCL (e.g., `network {}`, `logging {}`).

**Example**:  
```python
from pyvider.cty import tfstr, tfobj

@attrs.define
class NetworkSchema:
    vpc_id = tfstr(required=True)
    subnet_id = tfstr(required=True)
```
In this example, `NetworkSchema` is a fragment that can be embedded into larger schemas like `ComputeInstanceSchema` or `DatabaseSchema` through composition.

---

### **2. Schemas (Complete Definitions)**

**Definition**:  
A schema in Pyvider represents the **full structure of a resource or provider configuration**. It is composed of one or more schema fragments, encapsulating all required attributes, validation logic, and nested objects.

**Purpose**:  
- Describe **Terraform resources** and **data sources**.  
- Enforce **attribute-level constraints** (e.g., required fields, length restrictions).  
- Serve as the basis for **CRUD operations** in Terraform's lifecycle (`Create`, `Read`, `Update`, `Delete`).  
- Directly serialized into Terraform-compatible **protobuf schemas**.

**Example**:  
```python
@attrs.define
class DatabaseSchema:
    db_name = tfstr(required=True)
    user = tfstr(required=True)
    password = tfstr(required=True, sensitive=True)
    network = tfobj(NetworkSchema(), required=True)  # Composed fragment
```
Here, `DatabaseSchema` is a complete schema that embeds `NetworkSchema` as a fragment.

---

### **3. Meta Schema (Schemas for Schemas)**

**Definition**:  
A **meta schema** defines the rules and structure for **how schemas themselves should be constructed**. It acts as the **schema of schemas**, validating the structure of attribute definitions, their types, nesting rules, and constraints.

**Purpose**:  
- Ensure **uniformity** in schema construction across the framework.  
- Enforce **validation rules** for attributes (e.g., cannot have both `required` and `computed` flags simultaneously).  
- Govern **nested block types** (e.g., `SINGLE`, `LIST`, `MAP`).  
- Abstract away low-level schema mechanics, allowing developers to focus on higher-level schema composition.

**Example (Simplified Meta Schema)**:  
```python
@attrs.define
class AttributeMetadata:
    description: str = ""
    required: bool = False
    computed: bool = False
    sensitive: bool = False
    validators: list = attrs.field(factory=list)
```
In this example, `AttributeMetadata` represents a meta schema controlling the structure of individual schema attributes. This metadata layer governs how each `tfstr` or `tfobj` should behave within a schema.

---

---

### **How They Interact**

1. **Fragments** – Define smaller, reusable sections (e.g., `network` or `logging` blocks).  
2. **Schemas** – Assemble fragments to form full resource definitions.  
3. **Meta Schemas** – Validate that schemas are **correctly structured**, ensuring attributes conform to allowed patterns and rules.

---

### **Key Benefits**:
- **Extensibility** – Schema fragments enable nested, conditional expansion based on runtime conditions.  
- **Modularity** – Fragments reduce duplication and promote reusability across multiple schemas.  
- **Validation** – Meta schemas enforce attribute correctness at schema creation time, preventing runtime errors.  
- **Terraform Parity** – This mirrors Terraform’s schema validation lifecycle but leverages Python’s `attrs` for a clean, object-oriented interface.

Would you like examples showing schema fragments dynamically evolving at runtime or handling schema migrations through versioned fragments?
