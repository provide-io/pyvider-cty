---
---
### Schema

**Description**: Definition of structure, types, and validation rules for resources and capabilities.  

#### Lifecycle of Schema Construction
Phases of Schema Generation:

* **Definition:** Individual attributes and fragments are defined within classes.
* **Composition:** Fragments are assembled into parent schemas.
* **Validation:** Validators ensure the schema conforms to constraints.
Metaschema Assembly – All fragments and attributes are compiled into the final schema.

--------------------------------------------------------------------------------

### Research

You're right. Let's refine the explanation with the correct distinctions.

### **What is a Metaschema?**
A **metaschema** in the context of Pyvider, Terraform, or other schema-driven systems is the **resulting schema that governs and represents the entire structure** after assembling all **schema fragments** (individual schema definitions, nested objects, etc.). It defines the **global, top-level schema** that applies to the entire provider, resource, or component. 

In simpler terms, a metaschema represents the **compiled, holistic view of the schema** after all pieces have been combined. It enforces **rules, constraints, and relationships** across the entire schema, not just individual blocks or attributes.

---

### **Schema Fragment vs. Metaschema**
- **Schema Fragment**:  
  A **partial schema** representing a specific component or nested object within a larger schema. Examples include fragments for networking, security, or database configurations.  
  - Example:
    ```python
    class NetworkSchema(Schema):
        vpc_id = tfstr(required=True)
        subnet_ids = tflist(tfstr, required=True)
    ```

- **Metaschema**:  
  The **assembled and validated schema** that integrates **all fragments** and forms the complete schema definition for a resource, data source, or provider.  
  - Example (composed from fragments):
    ```python
    class ProviderSchema(Schema):
        network = tfobj(NetworkSchema, required=True)
        tags = tfmap(tfstr, required=False)
    ```

---

### **Metaschema in Terraform**
In Terraform, the **metaschema** refers to the **full schema definition** of a resource or provider, covering:  
- **Attributes** (e.g., `ami`, `region`)  
- **Nested Blocks** (e.g., `lifecycle`, `provisioner`)  
- **Validation Rules**  
- **Computed Fields**  
- **Dynamic Values**  

It ensures that schema blocks follow Terraform’s rules and constraints while dictating how individual fragments interact in the final resource definition.

---

### **How is Metaschema Different from Meta Arguments in Terraform?**
- **Metaschema**:  
  - A structural representation of **the entire schema**.  
  - Represents the **blueprint** for how resources, data sources, and configurations are structured globally.  
  - Affects schema compilation, validation, and enforcement at the provider level.

- **Meta Argument**:  
  - A **special configuration block** that can be used **within resource blocks**.  
  - It modifies **resource behavior** (e.g., `lifecycle`, `depends_on`, `count`, `provider`).  
  - Meta arguments **control execution logic** but do not affect schema definition at the same level as a metaschema.

  **Example (Terraform meta argument):**  
  ```hcl
  resource "aws_instance" "example" {
    ami           = "ami-123456"
    instance_type = "t2.micro"

    lifecycle {
      prevent_destroy = true
    }
  }
  ```

  **Key Difference**:  
  - Meta arguments apply **during runtime** and manage operational behavior.  
  - Metaschemas define **how schemas are composed and validated** at the **schema-definition level**.

---

### **What is a Meta Attribute?**
A **meta attribute** is an attribute **injected into the schema** that serves **special purposes** like:  
- **Tagging**  
- **Field-level validation or flags** (e.g., `computed`, `sensitive`)  
- **Custom behavioral logic**  

**Example in Pyvider (Meta Attribute):**  
```python
from pyvider.schema.attributes import tfstr

class DatabaseSchema(Schema):
    name = tfstr(required=True)
    password = tfstr(sensitive=True)  # 'sensitive' is a meta attribute
```

**Explanation**:  
- `sensitive=True` does not change the schema structure but **marks the attribute as sensitive** for Terraform, masking it in outputs.

---

### **Summary of Key Terms**:
| **Term**               | **Definition**                                                                                  |
|-----------------------|-------------------------------------------------------------------------------------------------|
| **Schema Fragment**    | A **partial schema** representing part of a resource or provider (e.g., networking, tags).       |
| **Metaschema**         | The **final, assembled schema** after combining all fragments, representing the entire resource. |
| **Meta Argument**      | **Operational arguments** (like `lifecycle`, `count`) controlling resource execution logic.      |
| **Meta Attribute**     | **Special attributes** embedded into schemas (e.g., `sensitive`, `computed`, `deprecated`).      |

---

Would you like to dive deeper into building dynamic metaschemas using Pyvider’s schema logic or focus on meta attributes in more detail?

#### Notes

A Capability can define Schema Fragments as well.

* Fragment enforcement can be done through type checking - i.e. whatever that is passed through to a schema must be of a SchemaFragment type. or something like that.

`tfattr(attribute metadata)`

### Possible features.

* Define the schema primary use in tfschema as a sort of type verification. as in fragment, or resource, or whatever.




### the tfschema