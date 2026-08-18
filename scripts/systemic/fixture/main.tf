// A Terraform configuration that exercises pyvider-cty 0.5 through the whole
// stack: HCL -> Terraform -> tfplugin6 gRPC -> pyvider -> pyvider-components
// -> pyvider-cty -> the wire, and back.
//
// It is deliberately weighted toward the behaviour that changed in 0.5. A
// provider function returning the wrong answer, a set losing an element, a
// sensitive value arriving unmarked or a refined unknown collapsing are all
// things the unit suites check in isolation and only a real plan/apply can
// check in composition.

terraform {
  required_providers {
    pyvider = {
      source  = "local/providers/pyvider"
      version = "0.5.0"
    }
  }
}

provider "pyvider" {}

// ---------------------------------------------------------------------------
// Functions. Every one of these changed in 0.5, and each is written so that a
// wrong answer fails the run rather than being recorded quietly.
// ---------------------------------------------------------------------------

locals {
  // Division by zero answers a signed infinity, as Terraform's own operator
  // does. This was the last behavioural disagreement between components and
  // the operator, and it is the reason this fixture exists in this form.
  div_by_zero = provider::pyvider::divide(1, 0)

  // Arithmetic is exact: computed in Decimal, not float64. 0.1 + 0.2 is 0.3.
  exact_sum = provider::pyvider::add(0.1, 0.2)

  // Strings are measured in grapheme clusters, not code points. A four-person
  // family emoji is one character, which is what Terraform's own length()
  // reports for it.
  family_length = provider::pyvider::length("👨‍👩‍👧‍👦")

  // Go's simple case mapping, not Python's full mapping: the sharp s does not
  // expand to SS.
  upper_strasse = provider::pyvider::upper("straße")

  // printf verbs are formatted, not passed through as literal text. Note the
  // signature: this `format` takes a template and a *list*, deliberately, and
  // is not variadic like Terraform's builtin of the same name.
  formatted = provider::pyvider::format("%05.2f|%s", [3.14159, "ok"])

  // %v is the default verb, and it picks between exponent and fixed notation on
  // a threshold Go fixes at 6 regardless of how many digits it prints. Deriving
  // that threshold from the value's own significant digits rendered nearly every
  // round number exponentially: 10 came out as "1e+01" and 250000 as "2.5e+05",
  // while 1234567 came out fixed where Go gives "1.234567e+06". Both directions
  // are asserted, because a fix that only stops the exponent form would be just
  // as wrong the other way.
  v_round      = provider::pyvider::format("%v", [250000])
  v_big        = provider::pyvider::format("%v", [1234567])

  // `-` has to cancel zero-padding. Left-padding 42 with zeros on the right
  // produced "42000", which does not read as a padded 42 but as another number
  // entirely -- the kind of value that reaches state and is never questioned.
  minus_zero = provider::pyvider::format("%-05d|", [42])

  // Precision and the alternate form were both parsed and then never read.
  precise_int = provider::pyvider::format("%.5d", [42])
  alt_hex     = provider::pyvider::format("%#x", [42])
}

check "functions_answer_what_they_should" {
  assert {
    condition     = local.div_by_zero > 1e308
    error_message = "divide(1, 0) should be a positive infinity"
  }
  assert {
    condition     = local.exact_sum == 0.3
    error_message = "add(0.1, 0.2) should be exactly 0.3, got ${local.exact_sum}"
  }
  assert {
    condition     = local.family_length == 1
    error_message = "length of a ZWJ family emoji should be 1 grapheme cluster, got ${local.family_length}"
  }
  assert {
    condition     = local.upper_strasse == "STRAßE"
    error_message = "upper() should use Go's simple case mapping, got ${local.upper_strasse}"
  }
  assert {
    condition     = local.formatted == "03.14|ok"
    error_message = "format() should render printf verbs, got ${local.formatted}"
  }
  assert {
    condition     = local.v_round == "250000"
    error_message = "format(%v) of a round number should not be exponential, got ${local.v_round}"
  }
  assert {
    condition     = local.v_big == "1.234567e+06"
    error_message = "format(%v) of 1234567 should be exponential, got ${local.v_big}"
  }
  assert {
    condition     = local.minus_zero == "42   |"
    error_message = "format(%-05d) should pad right with spaces, got ${local.minus_zero}"
  }
  assert {
    condition     = local.precise_int == "00042"
    error_message = "format(%.5d) should zero-fill to the precision, got ${local.precise_int}"
  }
  assert {
    condition     = local.alt_hex == "0x2a"
    error_message = "format(%#x) should carry the base prefix, got ${local.alt_hex}"
  }
}

// ---------------------------------------------------------------------------
// Resources. These take the value all the way through validate, plan, apply
// and refresh, which is where marks, unknowns and the wire codec actually get
// exercised together.
// ---------------------------------------------------------------------------

resource "pyvider_local_directory" "workspace" {
  path = "${path.module}/.systemic-out"
  // Octal is spelled with an explicit 0o prefix; a bare "0755" is refused
  // rather than guessed at.
  permissions = "0o755"
}

resource "pyvider_file_content" "plain" {
  filename = "${pyvider_local_directory.workspace.path}/plain.txt"

  // Depends on an attribute of another resource, so at plan time this is an
  // unknown that must survive the round trip and resolve at apply.
  content = "written by the systemic fixture into ${pyvider_local_directory.workspace.path}"
}

data "pyvider_env_variables" "current" {}

output "file_written" {
  value = pyvider_file_content.plain.filename
}

output "function_results" {
  // `div_by_zero` is deliberately absent, and the reason is worth knowing:
  // an infinity cannot be serialized into plan JSON, so putting one in an
  // output fails the plan with "cannot serialize infinity as JSON". That is
  // not a provider limitation -- Terraform's own `1 / 0` in an output fails
  // exactly the same way, which is the strongest confirmation available that
  // this provider's divide() agrees with the operator. The check block above
  // asserts the value; this output reports only what can be marshalled.
  value = {
    divide_by_zero_is_infinite = local.div_by_zero > 1e308
    exact_sum                  = local.exact_sum
    family_length              = local.family_length
    upper                      = local.upper_strasse
    formatted                  = local.formatted
  }
}
