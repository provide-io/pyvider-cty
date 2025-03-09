After the MetaSchema? has been compiled, everything is added to the appropriate component schemas as optional - so it's pseudo dynamic.

attribute_name = "the-name"
_attribute_name = {
  min_chars = 3, #minmax validator min chars
  max_chars = 8, #minmax validator max chars
  pattern = ".*" #regex validator permitted pattern
}

schema compilation

attribute_name.validators = ["minmax", "regex"]

Validators:
* register
* attach
* execute
--------
research
--------
timestamp: 2024-12-31 13:11
topic: 🏗️🐍 pyvider: maturity evaluation
---

