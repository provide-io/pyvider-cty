### **What is a Schema Fragment?**

A **schema fragment** is a **reusable, isolated piece of schema logic** that can be **composed, extended, or dynamically injected** into larger schema structures. It represents a **partial schema** – typically handling one specific part of the configuration – that can be **merged or combined** with other fragments to form a complete schema.  

---

---

### **Purpose of Schema Fragments**

1. **Modularity**  
- Break down large, monolithic schemas into **smaller, manageable pieces**.  
- Each fragment represents a **self-contained block** that can be reused across multiple schemas.  

2. **Reusability**  
- Common patterns (like `network`, `database`, `replicas`) can be defined as fragments and reused in different parent schemas.  
- This avoids schema duplication and promotes **DRY** (Don’t Repeat Yourself) principles.  

3. **Extensibility**  
- Schema fragments can **dynamically evolve** or **inherit behavior** from other fragments.  
- Example: Adding firewall rules to the `NetworkSchema` without modifying the entire schema.  

4. **Composability**  
- Fragments can be combined to **compose complex configurations** in a layered approach, similar to how Terraform allows nesting and block re-use.  

---

---

### **How Schema Fragments Fit in Pyvider**

In Pyvider:  
- A **schema fragment** is typically a **class** representing a nested block or subsection of the schema.  
- Fragments can be **directly attached** to parent schemas using `tfobj` or `CtyList`.  
- Fragments can include **their own validators** or inherit validators from higher-level schemas.  

---

---

### **Examples of Schema Fragments**

---

#### **1. Networking Fragment (Reusable Across Resources)**
- A network fragment that can attach to **any resource needing networking** configurations.  
```python
@define
class NetworkSchema:
    vpc_id = tfstr(required=True)
    subnet_id = tfstr(required=True)
    allowed_ips = CtyList(
        tfstr(validators=["ip_range"]),
        min_length=1
    )
```

**Usage (Attached to Multiple Schemas)**:  
```python
@define
class DatabaseSchema:
    db_name = tfstr(required=True)
    user = tfstr(required=True)
    network = tfobj(NetworkSchema(), required=True)
```

```python
@define
class WebAppSchema:
    app_name = tfstr(required=True)
    network = tfobj(NetworkSchema(), required=True)
```

---

---

#### **2. Replica Fragment (Scaling Component)**
- A fragment that defines scaling logic for **replicas or cluster nodes**.  
```python
@define
class ReplicaSchema:
    name = tfstr(required=True)
    instance_type = tfstr(required=True)
    count = tfnum(default=1)
```

**Usage in Deployments**:  
```python
@define
class DeploymentSchema:
    replicas = CtyList(
        tfobj(ReplicaSchema),
        required=True,
        validators=["minmax_length"],
        min_length=1
    )
```

---

---

#### **3. Security Fragment (Firewall and IAM Rules)**
```python
@define
class SecuritySchema:
    firewall_enabled = CtyBool(default=False)
    firewall_rules = CtyList(
        tfstr(),
        validators=["conditional"],
        optional=True
    )
    security_groups = CtyList(
        tfstr(validators=["minmax_length"]),
        min_length=1,
        max_length=5
    )
```

---

---

### **Schema Fragment Composition**
**Composed schemas** leverage fragments to define large, complex configurations.  

```python
@define
class ApplicationSchema:
    app_name = tfstr(required=True)
    environment = tfstr(required=True)
    security = tfobj(SecuritySchema(), optional=True)
    replicas = CtyList(tfobj(ReplicaSchema), required=True)
    network = tfobj(NetworkSchema(), required=True)
```

- This structure **composes multiple schema fragments** into a single schema.  
- Each fragment handles a distinct part of the overall schema (`security`, `network`, `replicas`).  

---

---

### **Dynamic Schema Fragments (Runtime Injection)**

Pyvider can **inject schema fragments at runtime** based on external conditions (feature flags, environment variables).  

```python
@define
class DynamicSchema:
    database = tfobj(DatabaseSchema(), required=True)

    def __attrs_post_init__(self):
        # Conditionally add networking fragment
        if self.database.network.subnet_id.startswith("prod"):
            self.__class__.security = tfobj(SecuritySchema(), required=True)
```

- **Dynamic Fragment Injection**: Adds a security block only if the subnet is part of the production environment.  
- This allows **schema composition to evolve at runtime** without predefining the full schema.  

---

---

### **Advantages of Schema Fragments**

1. **Scalability**  
- Fragments reduce schema bloat by allowing nested sections to be developed **independently**.  

2. **Maintainability**  
- Updating a schema fragment (like `SecuritySchema`) **automatically propagates** the changes across all schemas using it.  

3. **Flexibility**  
- Developers can inject, remove, or extend fragments without modifying the parent schema.  

4. **Reduced Complexity**  
- Large, hierarchical schemas are broken down into smaller, understandable components.  

---

---

### **Comparison to Terraform HCL**

| **Terraform (HCL Block)**        | **Pyvider Schema Fragment**                                | **Notes**                                             |
|----------------------------------|------------------------------------------------------------|-------------------------------------------------------|
| `network_config`                  | `NetworkSchema` (Attached to multiple schemas)             | Represents reusable block for networking.             |
| `replica` (multiple blocks)       | `ReplicaSchema` (List of nested objects)                   | Multiple fragments attached via `CtyList`.             |
| `security_group`                  | `SecuritySchema`                                           | Optional fragment conditionally injected at runtime.  |
| `dynamic "block"` (for_each)      | `__attrs_post_init__` (dynamic fragment injection)         | Fragments dynamically inserted during instantiation.  |

---

---

### **Use Cases for Schema Fragments**

1. **Multi-Cloud Deployments**  
- `NetworkSchema` handles AWS VPCs or GCP subnets, making it adaptable to cloud providers.  

2. **Kubernetes Configuration**  
- Fragments represent `service`, `deployment`, `ingress` blocks, each composing a cluster schema.  

3. **Security Hardening**  
- Inject firewall rules or IAM roles dynamically based on environment (staging vs production).  

4. **Infrastructure Scaling**  
- Use `ReplicaSchema` fragments to represent pod scaling, dynamic allocation, and scaling triggers.  

---

---

### **Why Pyvider Needs Schema Fragments**

- **Large Infrastructure Schemas**: Handling hundreds of fields becomes manageable by breaking it into smaller fragments.  
- **Reusable Components**: Common patterns like `network` or `firewall` are repeated across various schemas.  
- **Terraform Parity**: Pyvider closely mimics Terraform’s nested block approach using Python’s OOP design.  
- **Dynamic Injection**: Fragments allow schemas to **grow or shrink dynamically** based on external factors, without modifying static schema definitions.

Would you like to explore **cross-schema validation** or **fragment-level computed fields** next?



-----------------------

### **Fragment Versioning and Conditional Fragments in Pyvider**

Schema fragments can evolve over time as infrastructure grows and new configurations are introduced. In Pyvider, **fragment versioning** and **conditional fragments** allow for flexible schema updates while maintaining backward compatibility. This mirrors Terraform’s approach to versioned modules and dynamic blocks but leverages Python’s OOP and dynamic class capabilities.  

---

---

### **1. Fragment Versioning**

**Concept**:  
- Multiple versions of the same fragment exist to accommodate evolving configurations.  
- Newer fragments can introduce fields or constraints without breaking existing schemas.  
- Fragments are versioned by **class naming**, file structure, or a dedicated `version` field.

---

---

#### **Approach 1: Class-Based Fragment Versioning**
- Different versions of the same schema fragment are defined as **separate classes**.  
- The desired version is selected dynamically during schema instantiation or via configuration files.

**Example Directory Structure**:  
```
components/
│
└── fragments/
    ├── network_v1.py
    ├── network_v2.py
    └── security.py
```

---

**Implementation**:  
```python
@define
class NetworkSchemaV1:
    vpc_id = tfstr(required=True)
    subnet_id = tfstr(required=True)


@define
class NetworkSchemaV2:
    vpc_id = tfstr(required=True)
    subnet_id = tfstr(required=True)
    allowed_ips = CtyList(
        tfstr(validators=["ip_range"]),
        min_length=1
    )
```  

**Usage in Parent Schema**:  
```python
from fragments.network_v1 import NetworkSchemaV1
from fragments.network_v2 import NetworkSchemaV2

@define
class WebAppSchema:
    app_name = tfstr(required=True)
    
    # Choose fragment version dynamically
    network = tfobj(NetworkSchemaV2(), required=True)
```

**Advantages**:  
- **Backward Compatibility** – Older schemas reference `V1` fragments, while new configurations use `V2`.  
- **Incremental Updates** – Fields and validators evolve with each version.  
- **Predictability** – Versions are explicitly referenced, ensuring controlled upgrades.  

---

---

#### **Approach 2: File-Based Fragment Versioning**
- Fragments are organized by version within a versioned directory.  
- The schema imports the required fragment based on the desired configuration.  

**Example Directory Structure**:  
```
components/
│
└── fragments/
    └── network/
        ├── v1.py
        └── v2.py
```

---

---

**Usage**:  
```python
from fragments.network.v1 import NetworkSchema as NetworkSchemaV1
from fragments.network.v2 import NetworkSchema as NetworkSchemaV2
```  

---

---

#### **Approach 3: Dynamic Versioning via Metadata**
- A single fragment class handles multiple versions using a `version` parameter.  
- Fields and validators adjust dynamically based on the version specified at runtime.  

**Implementation**:  
```python
@define
class NetworkSchema:
    vpc_id = tfstr(required=True)
    subnet_id = tfstr(required=True)
    allowed_ips = CtyList(tfstr(), optional=True)
    
    def __attrs_post_init__(self):
        # Enable allowed_ips only for version 2
        if getattr(self, 'version', 1) >= 2:
            self.__class__.allowed_ips = CtyList(
                tfstr(validators=["ip_range"]),
                min_length=1
            )
```  

**Dynamic Instantiation**:  
```python
schema_v1 = NetworkSchema(version=1)
schema_v2 = NetworkSchema(version=2)
```  

**Advantages**:  
- **Single Source of Truth** – One class handles all versions, reducing code duplication.  
- **Dynamic Expansion** – Fields evolve dynamically without modifying existing instantiations.  
- **Simplified Imports** – Developers only import one schema fragment but adjust versions at runtime.  

---

---

### **2. Conditional Fragments**

**Concept**:  
- Fragments are **conditionally injected** into the schema at runtime based on external flags, environment variables, or feature toggles.  
- This allows for **dynamic schema expansion** without modifying the core schema structure.  

---

---

#### **Use Case**:
- A database schema should include firewall rules **only if** `firewall_enabled` is `True`.  
- A load balancer schema should dynamically attach logging if `logging_enabled` is set.

---

---

**Implementation (Dynamic Fragment Injection)**:  
```python
@define
class DatabaseSchema:
    db_name = tfstr(required=True)
    user = tfstr(required=True)
    password = tfstr(required=True, sensitive=True)
    network = tfobj(NetworkSchema(), required=True)

    def __attrs_post_init__(self):
        if getattr(self, "firewall_enabled", False):
            self.__class__.security = tfobj(SecuritySchema(), required=True)
```  

---

---

**Parent Schema**:  
```python
@define
class WebAppSchema:
    app_name = tfstr(required=True)
    database = tfobj(DatabaseSchema(firewall_enabled=True), required=True)
```

---

---

#### **Feature Flag Driven Fragment Injection**
```python
@define
class LoadBalancerSchema:
    lb_name = tfstr(required=True)

    def __attrs_post_init__(self):
        if feature_flag("logging_enabled"):
            self.__class__.logging = tfobj(LoggingSchema(), optional=True)
```

**Feature Flag Check**:  
```python
def feature_flag(flag: str) -> bool:
    # Simulate feature flag lookup
    return flag in ["logging_enabled"]
```

---

---

### **Runtime Behavior**
- **Dynamic Expansion**: Fragments are injected only when the feature flag is active or condition is met.  
- **Post-Initialization Hooks**: `__attrs_post_init__` ensures fragments are attached **after schema instantiation**.  

---

---

### **Advantages of Conditional Fragments**
- **Dynamic Adaptation** – Schema adjusts based on runtime conditions.  
- **Reduced Complexity** – Optional blocks are added conditionally, avoiding unnecessary boilerplate.  
- **Extensibility** – New blocks can be attached to schemas without modifying the parent class.  

---

---

### **Fragment Versioning + Conditional Fragments in Action**
```python
@define
class DeploymentSchema:
    replicas = CtyList(tfobj(ReplicaSchema), required=True)
    database = tfobj(DatabaseSchema(version=2), required=True)

    def __attrs_post_init__(self):
        if feature_flag("advanced_security"):
            self.__class__.security = tfobj(SecuritySchema(), required=True)
```

- `DatabaseSchema` defaults to version 2.  
- The `security` block is injected if the `advanced_security` flag is active.  

---

---

### **Why This Matters for Pyvider**
- **Terraform Parity** – Mimics Terraform’s ability to dynamically add blocks based on conditions.  
- **Real-World Application** – Allows environments (staging, prod) to adjust configurations without modifying the base schema.  
- **Evolving Infrastructure** – Supports incremental updates to schema without breaking existing configurations.

Would you like to dive deeper into **cross-fragment dependencies** or explore how to **version entire schemas** for long-term backward compatibility?
