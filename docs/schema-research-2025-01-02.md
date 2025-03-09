* Collects all the schema fragments and adds to list of Validators in the Hub.
* Executes the  alidator initialization logic
* Initialization can set the "static" parts of the schema. runtime conditional logic can not modify the static logic - i.e. it can't change a Provider Schema in flight (but that might be an interesting thing to hack in)


You use "Schema Fragments" to build a "Component Schema"



---
Meta Schema – Control Layer for Schema Behavior

Definition:
A meta schema defines the behavior and rules governing attributes within the schema. This includes constraints like length, pattern matching, and type-specific rules, applied via validators.
---

"Schema Definition"


Attribute

Attribute Metadata = optional/required/ _attr_name
* does the attribute have the meta schema?

Validator


---

Conceptual Analysis (How Pyvider Views This):
Schema Definition – The primary schema (file_content) defines the basic resource structure and attribute types.

Schema Fragmentation – The _content and _file blocks are schema fragments attached to specific attributes (content and file). They augment the core schema, providing fine-grained control over each attribute’s constraints.

Meta Schema – This term now represents the combination of:

Base Schema – The file_content resource schema.
Attribute Constraints – _content and _file as meta blocks enriching the resource.
Validation Layer – Defines how attribute-specific rules are evaluated alongside the resource.
