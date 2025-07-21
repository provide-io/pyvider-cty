package main

import (
	"log"
	"math/big"
	"os"

	"github.com/zclconf/go-cty/cty"
	"github.com/zclconf/go-cty/cty/msgpack"
)

// A struct to hold a test case's value and its corresponding type.
type TestCase struct {
	Value cty.Value
	Type  cty.Type
}

// Helper to create a refined unknown string.
func refinedUnknownString() cty.Value {
	val, _ := cty.UnknownVal(cty.String).Refine().SetStringPrefix("start-").Apply()
	return val
}

// Helper to create a refined unknown number.
func refinedUnknownNumber() cty.Value {
	val, _ := cty.UnknownVal(cty.Number).Refine().SetLowerBound(cty.NumberIntVal(100), true).SetUpperBound(cty.NumberIntVal(200), false).Apply()
	return val
}

func main() {
	// Define all canonical test cases.
	testCases := map[string]TestCase{
		// Primitives
		"string_simple":      {Value: cty.StringVal("hello world"), Type: cty.String},
		"number_simple":      {Value: cty.NumberIntVal(42), Type: cty.Number},
		"number_float":       {Value: cty.NumberFloatVal(123.45), Type: cty.Number},
		"bool_true":          {Value: cty.True, Type: cty.Bool},
		"large_number":       {Value: cty.NumberVal(new(big.Float).SetInt(new(big.Int).Exp(big.NewInt(2), big.NewInt(100), nil))), Type: cty.Number},

		// Special Values
		"null_string":        {Value: cty.NullVal(cty.String), Type: cty.String},
		"unknown_unrefined":  {Value: cty.UnknownVal(cty.String), Type: cty.String},
		"unknown_refined_str":{Value: refinedUnknownString(), Type: cty.String},
		"unknown_refined_num":{Value: refinedUnknownNumber(), Type: cty.Number},

		// Collections
		"list_of_strings":    {Value: cty.ListVal([]cty.Value{cty.StringVal("a"), cty.StringVal("b")}), Type: cty.List(cty.String)},
		"set_of_numbers":     {Value: cty.SetVal([]cty.Value{cty.NumberIntVal(1), cty.NumberIntVal(2)}), Type: cty.Set(cty.Number)},
		"map_simple":         {Value: cty.MapVal(map[string]cty.Value{"a": cty.True, "b": cty.False}), Type: cty.Map(cty.Bool)},
		"empty_list":         {Value: cty.ListValEmpty(cty.String), Type: cty.List(cty.String)},

		// Nested & Complex Structures
		"object_simple": {
			Value: cty.ObjectVal(map[string]cty.Value{"name": cty.StringVal("test"), "enabled": cty.True}),
			Type:  cty.Object(map[string]cty.Type{"name": cty.String, "enabled": cty.Bool}),
		},
		"tuple_simple": {
			Value: cty.TupleVal([]cty.Value{cty.StringVal("a"), cty.NumberIntVal(1)}),
			Type:  cty.Tuple([]cty.Type{cty.String, cty.Number}),
		},
		"object_nested": {
			Value: cty.ObjectVal(map[string]cty.Value{
				"id": cty.StringVal("obj1"),
				"config": cty.ObjectVal(map[string]cty.Value{
					"retries": cty.NumberIntVal(3),
				}),
				"tags": cty.ListVal([]cty.Value{cty.StringVal("tag1")}),
			}),
			Type: cty.Object(map[string]cty.Type{
				"id": cty.String,
				"config": cty.Object(map[string]cty.Type{"retries": cty.Number}),
				"tags":   cty.List(cty.String),
			}),
		},

		// Dynamic & Capsule Types
		"dynamic_wrapped_string": {
			Value: cty.CapsuleVal(cty.DynamicPseudoType, &cty.StringVal("dynamic")),
			Type:  cty.DynamicPseudoType,
		},
		"dynamic_wrapped_object": {
			Value: cty.CapsuleVal(cty.DynamicPseudoType, &cty.ObjectVal(map[string]cty.Value{"key": cty.StringVal("value")})),
			Type:  cty.DynamicPseudoType,
		},
		"capsule_null": {
			Value: cty.NullVal(cty.Capsule("MyCapsule", nil)),
			Type:  cty.Capsule("MyCapsule", nil),
		},
	}

	outputDir := "../../tests/fixtures/go-cty"
	if err := os.MkdirAll(outputDir, 0755); err != nil {
		log.Fatalf("Failed to create fixture directory: %v", err)
	}

	for name, tc := range testCases {
		// Marshal using the value's specific type.
		bytes, err := msgpack.Marshal(tc.Value, tc.Type)
		if err != nil {
			log.Fatalf("Failed to marshal %s: %v", name, err)
		}

		filename := outputDir + "/" + name + ".msgpack"
		if err := os.WriteFile(filename, bytes, 0644); err != nil {
			log.Fatalf("Failed to write fixture %s: %v", name, err)
		}
		log.Printf("Wrote %s", filename)
	}
}
