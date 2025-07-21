package main

import (
	"flag"
	"fmt"
	"math/big"
	"os"
	"reflect"

	"github.com/hashicorp/go-hclog"
	"github.com/zclconf/go-cty/cty"
	"github.com/zclconf/go-cty/cty/msgpack"
)

// TestCase holds a value and its corresponding type for marshaling.
type TestCase struct {
	Value cty.Value
	Type  cty.Type
}

// CustomData is a struct for our advanced capsule type.
type CustomData struct {
	ID   int
	Name string
}

// --- Helper functions to create complex values ---

func refinedUnknownString() cty.Value {
	return cty.UnknownVal(cty.String).Refine().StringPrefix("start-").NewValue()
}

func refinedUnknownNumber() cty.Value {
	return cty.UnknownVal(cty.Number).Refine().
		NumberRangeLowerBound(cty.NumberIntVal(100), true).
		NumberRangeUpperBound(cty.NumberIntVal(200), false).
		NewValue()
}

func refinedUnknownList() cty.Value {
	return cty.UnknownVal(cty.List(cty.String)).Refine().CollectionLength(3).NewValue()
}

func main() {
	// Define and parse the command-line flag for the output directory.
	outputDir := flag.String("directory", "../tests/fixtures/go-cty", "The directory to write fixture files to.")
	flag.Parse()

	logger := hclog.New(&hclog.LoggerOptions{
		Name:  "fixture-generator",
		Level: hclog.Info,
	})

	// --- Advanced Capsule Type Definition ---
	customDataType := reflect.TypeOf(CustomData{})
	advancedCapsuleType := cty.CapsuleWithOps("CustomData", customDataType, &cty.CapsuleOps{
		RawEquals: func(a, b interface{}) bool {
			return a.(CustomData) == b.(CustomData)
		},
		HashKey: func(v interface{}) string {
			data := v.(CustomData)
			return fmt.Sprintf("%d-%s", data.ID, data.Name)
		},
	})

	// Define all canonical test cases.
	testCases := map[string]TestCase{
		"string_simple": {Value: cty.StringVal("hello world"), Type: cty.String},
		"number_simple": {Value: cty.NumberIntVal(42), Type: cty.Number},
		"bool_true":     {Value: cty.True, Type: cty.Bool},
		"large_number":  {Value: cty.NumberVal(new(big.Float).SetInt(new(big.Int).Exp(big.NewInt(2), big.NewInt(100), nil))), Type: cty.Number},
		"null_string":         {Value: cty.NullVal(cty.String), Type: cty.String},
		"unknown_unrefined":   {Value: cty.UnknownVal(cty.String), Type: cty.String},
		"unknown_refined_str": {Value: refinedUnknownString(), Type: cty.String},
		"unknown_refined_num": {Value: refinedUnknownNumber(), Type: cty.Number},
		"unknown_refined_list":{Value: refinedUnknownList(), Type: cty.List(cty.String)},
		"list_of_strings": {Value: cty.ListVal([]cty.Value{cty.StringVal("a"), cty.StringVal("b")}), Type: cty.List(cty.String)},
		"set_of_numbers":  {Value: cty.SetVal([]cty.Value{cty.NumberIntVal(1), cty.NumberIntVal(2)}), Type: cty.Set(cty.Number)},
		"map_simple":      {Value: cty.MapVal(map[string]cty.Value{"a": cty.True, "b": cty.False}), Type: cty.Map(cty.Bool)},
		"set_of_tuples": {
			Value: cty.SetVal([]cty.Value{
				cty.TupleVal([]cty.Value{cty.StringVal("a"), cty.NumberIntVal(1)}),
				cty.TupleVal([]cty.Value{cty.StringVal("b"), cty.NumberIntVal(2)}),
			}),
			Type: cty.Set(cty.Tuple([]cty.Type{cty.String, cty.Number})),
		},
		"deeply_nested_object": {
			Value: cty.ObjectVal(map[string]cty.Value{
				"id":      cty.StringVal("obj1"), "enabled": cty.True, "ports":   cty.ListVal([]cty.Value{cty.NumberIntVal(80), cty.NumberIntVal(443)}),
				"config": cty.ObjectVal(map[string]cty.Value{ "retries": cty.NumberIntVal(3), "params":  cty.MapVal(map[string]cty.Value{"timeout": cty.StringVal("5s")}), }),
				"metadata": cty.NullVal(cty.Map(cty.String)), "extra":    cty.UnknownVal(cty.String),
			}),
			Type: cty.Object(map[string]cty.Type{
				"id":      cty.String, // DEFINITIVE FIX: Replaced "string" with cty.String
				"enabled": cty.Bool, "ports": cty.List(cty.Number),
				"config": cty.Object(map[string]cty.Type{ "retries": cty.Number, "params":  cty.Map(cty.String), }),
				"metadata": cty.Map(cty.String), "extra": cty.String,
			}),
		},
		"dynamic_wrapped_string": { Value: cty.StringVal("dynamic"), Type:  cty.DynamicPseudoType, },
		"dynamic_wrapped_object": { Value: cty.ObjectVal(map[string]cty.Value{"key": cty.StringVal("value")}), Type:  cty.DynamicPseudoType, },
		"advanced_capsule": { Value: cty.NullVal(advancedCapsuleType), Type:  advancedCapsuleType, },
	}

	if err := os.MkdirAll(*outputDir, 0755); err != nil {
		logger.Error("Failed to create fixture directory", "error", err)
		os.Exit(1)
	}

	for name, tc := range testCases {
		bytes, err := msgpack.Marshal(tc.Value, tc.Type)
		if err != nil {
			logger.Error("Failed to marshal", "case", name, "error", err)
			os.Exit(1)
		}
		filename := *outputDir + "/" + name + ".msgpack"
		if err := os.WriteFile(filename, bytes, 0644); err != nil {
			logger.Error("Failed to write fixture", "file", filename, "error", err)
			os.Exit(1)
		}
		logger.Info("Wrote fixture", "file", filename)
	}
}
