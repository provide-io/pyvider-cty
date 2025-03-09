Here's an outline for the **Schema** section of the Pyvider language reference, covering schema construction, schema fragments, metaschemas, and associated attributes. This structure aligns with Terraform's schema philosophy but adapts to Pyvider’s Pythonic approach.

---

## **Outline: Pyvider Language Reference – Schema and Metaschema**  

---

### **1. Schema Overview**  
**Description**:  
Schemas define the structure, types, and validation rules for Pyvider resources, data sources, and providers. They dictate the configuration, lifecycle, and metadata of managed entities.

**Purpose**:  
- Ensure **type safety** and **validation**.  
- Provide **structured definitions** for resources and configurations.  
- Enable **dynamic composition** through schema fragments.  

---

### **2. Core Concepts**  
- **Schema**: A class defining the shape and constraints of a resource or provider.  
- **Schema Fragment**: A reusable block representing part of a larger schema.  
- **Metaschema**: The complete schema resulting from the assembly of all fragments and attributes, representing the entire structure of a resource or provider.  
- **Meta Attribute**: Special attributes (e.g., `computed`, `sensitive`) that influence attribute behavior but not schema structure.  

---

### **3. Schema Components**  

#### **3.1 Attributes**  
Attributes represent individual fields within a schema. They can be primitive types (e.g., `string`, `number`) or complex types (e.g., `object`, `list`).  

- **Primitive Attributes**: `tfstr`, `tfnum`, `tfbool`  
- **Collection Attributes**: `tflist`, `tfmap`, `tfset`  
- **Nested Attributes**: `tfobj` (embeds another schema as a sub-block)  

**Example**:  
```python
from pyvider.schema.attributes import tfstr, tfnum

class AppSchema(Schema):
    app_name = tfstr(required=True, description="Application name")
    replicas = tfnum(default=1, description="Number of replicas")
```  

---

#### **3.2 Meta Attributes**  
Meta attributes modify the behavior of attributes but do not define the schema structure. Examples include:  
- **`computed`** – Value is determined at runtime.  
- **`sensitive`** – Masked in logs/output.  
- **`optional`** – Attribute is not required but can be provided.  

**Example**:  
```python
class CredentialSchema(Schema):
    username = tfstr(required=True)
    password = tfstr(sensitive=True)
    token = tfstr(computed=True)
```  

---

### **4. Schema Fragments**  
Schema fragments represent reusable schema components. They can be nested within parent schemas to create hierarchical structures.

**Example**:  
```python
class NetworkConfigSchema(Schema):
    vpc_id = tfstr(required=True)
    subnet_ids = tflist(tfstr)

class AppSchema(Schema):
    app_name = tfstr(required=True)
    network = tfobj(NetworkConfigSchema, required=True)
```  

---

### **5. Metaschema**  
The **metaschema** is the fully assembled schema that results from combining all fragments and attributes. It reflects the complete configuration model for a resource or provider.

**Key Characteristics**:  
- Ensures all **fragments** and **attributes** form a valid, cohesive schema.  
- Provides **global validation** across nested blocks.  
- Dynamically adjusts through feature flags, conditions, or dependencies.  

**Example**:  
```python
class WebServerSchema(Schema):
    server_name = tfstr(required=True)
    secure = tfbool(default=False)

    def __attrs_post_init__(self):
        if self.secure:
            self.__class__.security = tfobj(SecuritySchema)
```  

---

### **6. Lifecycle of Schema Construction**  

**Phases of Schema Generation**:  
1. **Definition** – Individual attributes and fragments are defined within classes.  
2. **Composition** – Fragments are assembled into parent schemas.  
3. **Validation** – Validators ensure the schema conforms to constraints.  
4. **Metaschema Assembly** – All fragments and attributes are compiled into the final schema.  

---

### **7. Validators**  
Validators attach to schema attributes to enforce constraints (e.g., length, regex, value ranges). They ensure input correctness before resource creation or modification.  

**Example**:  
```python
@Validators.register("min_length")
def min_length_validator(value, metadata):
    if len(value) < 3:
        raise ValueError("Value too short.")

class UserSchema(Schema):
    username = tfstr(required=True, validators=["min_length"])
```  

---

### **8. Schema Building Utilities**  

- **tfstr** – Defines string attributes.  
- **tfnum** – Defines numeric attributes.  
- **tfbool** – Defines boolean attributes.  
- **tflist** – Defines list attributes.  
- **tfmap** – Defines map attributes.  
- **tfset** – Defines set attributes.  
- **tfobj** – Embeds nested schema objects.  

---

### **9. Advanced Schema Composition**  

#### **9.1 Conditional Schema Fragments**  
Fragments can be conditionally attached based on feature flags or configuration values.  

**Example**:  
```python
class WebAppSchema(Schema):
    app_name = tfstr(required=True)
    enable_logging = tfbool(default=False)

    def __attrs_post_init__(self):
        if self.enable_logging:
            self.__class__.logging = tfobj(LoggingSchema)
```  

---

### **10. Schema Inheritance and Reuse**  

Schemas can inherit or reuse fragments across multiple definitions, promoting DRY (Don't Repeat Yourself) practices.  

**Example**:  
```python
class BaseResourceSchema(Schema):
    id = tfstr(required=True)
    tags = tfmap(tfstr)

class S3BucketSchema(BaseResourceSchema):
    bucket_name = tfstr(required=True)
    versioning = tfbool(default=False)
```  

---

### **11. Schema Serialization and Export**  

Schemas can be serialized to JSON or Protocol Buffers for interaction with Terraform. This allows for seamless integration with Terraform Plugin Protocol v6.  

**Example**:  
```python
class FileSchema(Schema):
    filename = tfstr(required=True)
    content = tfstr(required=True)

file_schema = FileSchema().to_proto()
```  

---

### **12. Error Handling in Schemas**  

Common schema errors include:  
- **ValidationError** – Raised when schema constraints are violated.  
- **SchemaParseError** – Occurs during schema serialization.  

---

### **13. Example: Full Resource Schema**  

```python
class S3BucketSchema(Schema):
    bucket_name = tfstr(required=True)
    versioning = tfbool(default=False)
    policy = tfobj(S3BucketPolicy, optional=True)

class S3BucketPolicy(Schema):
    policy_document = tfstr(required=True)
```  

---

### **14. Best Practices for Schema Development**  
- Use **schema fragments** for reusable components.  
- Leverage **validators** for early error detection.  
- Dynamically assemble metaschemas using **feature flags** and **post-initialization hooks**.  
- Mark sensitive fields explicitly using `sensitive=True`.  

---

Would you like to expand this into full reference documentation or dive deeper into schema validation patterns?