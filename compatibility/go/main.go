package main

import (
	"encoding/json"
	"fmt"
	"math/big"
	"os"
	"path/filepath"
	"strings"

	"github.com/hashicorp/go-hclog"
	"github.com/spf13/cobra"
	"github.com/zclconf/go-cty/cty"
	ctyjson "github.com/zclconf/go-cty/cty/json"
	"github.com/zclconf/go-cty/cty/msgpack"
)

// Emojilogger provides structured, emoji-prefixed logging.
type Emojilogger struct {
	logger hclog.Logger
}

// Log emits a log message with a 3-emoji prefix.
func (l *Emojilogger) Log(level hclog.Level, domain, action, status, msg string, args ...interface{}) {
	prefix := fmt.Sprintf("%s %s %s", domain, action, status)
	l.logger.Log(level, fmt.Sprintf("%s %s", prefix, msg), args...)
}

var (
	logger    *Emojilogger
	logLevel  string
	logFile   string
	directory string
)

// rootCmd represents the base command when called without any subcommands
var rootCmd = &cobra.Command{
	Use:   "compat-tool",
	Short: "A tool to generate and verify cty compatibility fixtures.",
	PersistentPreRun: func(cmd *cobra.Command, args []string) {
		level := hclog.LevelFromString(logLevel)
		if level == hclog.NoLevel {
			level = hclog.Debug // Default to debug if parsing fails
		}

		opts := &hclog.LoggerOptions{Name: "compat-suite", Level: level}
		if logFile != "" {
			f, err := os.OpenFile(logFile, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0666)
			if err != nil {
				fmt.Printf("Failed to open log file %s: %v\n", logFile, err)
				os.Exit(1)
			}
			opts.Output = f
			opts.JSONFormat = true
		}
		hcl := hclog.New(opts)
		logger = &Emojilogger{logger: hcl}
	},
}

var generateCmd = &cobra.Command{
	Use:   "generate",
	Short: "Generate Go-based cty fixtures for Python to consume.",
	Run: func(cmd *cobra.Command, args []string) {
		if directory == "" {
			logger.Log(hclog.Error, "📦", "📝", "❌", "--directory flag is required.")
			os.Exit(1)
		}
		generateFixtures(directory)
	},
}

var verifyCmd = &cobra.Command{
	Use:   "verify",
	Short: "Verify Python-generated cty fixtures using Go's implementation.",
	Run: func(cmd *cobra.Command, args []string) {
		if directory == "" {
			logger.Log(hclog.Error, "🔍", "🔎", "❌", "--directory flag is required.")
			os.Exit(1)
		}
		verifyFixtures(directory)
	},
}

func init() {
	// Added 'trace' to help text
	rootCmd.PersistentFlags().StringVarP(&logLevel, "log-level", "l", "debug", "Set the logging level (e.g., 'trace', 'debug', 'info', 'warn', 'error')")
	rootCmd.PersistentFlags().StringVar(&logFile, "log-file", "", "Path to a file to write logs to.")
	generateCmd.Flags().StringVar(&directory, "directory", "", "The directory for fixture files.")
	verifyCmd.Flags().StringVar(&directory, "directory", "", "The directory for fixture files.")
	rootCmd.AddCommand(generateCmd)
	rootCmd.AddCommand(verifyCmd)
}

type TestCase struct {
	Value cty.Value
	Type  cty.Type
}

// --- GENERATE LOGIC ---
func getTestCasesForGeneration() map[string]TestCase {
	refinedUnknownString := func() cty.Value {
		return cty.UnknownVal(cty.String).Refine().StringPrefix("start-").NewValue()
	}
	refinedUnknownNumber := func() cty.Value {
		return cty.UnknownVal(cty.Number).Refine().
			NumberRangeLowerBound(cty.NumberIntVal(100), true).
			NumberRangeUpperBound(cty.NumberIntVal(200), false).
			NewValue()
	}
	refinedUnknownList := func() cty.Value {
		return cty.UnknownVal(cty.List(cty.String)).Refine().CollectionLength(3).NewValue()
	}

	return map[string]TestCase{
		"string_simple":      {Value: cty.StringVal("hello world"), Type: cty.String},
		"number_simple":      {Value: cty.NumberIntVal(42), Type: cty.Number},
		"bool_true":          {Value: cty.True, Type: cty.Bool},
		"large_number":       {Value: cty.NumberVal(new(big.Float).SetInt(new(big.Int).Exp(big.NewInt(2), big.NewInt(100), nil))), Type: cty.Number},
		"null_string":        {Value: cty.NullVal(cty.String), Type: cty.String},
		"unknown_unrefined":  {Value: cty.UnknownVal(cty.String), Type: cty.String},
		"unknown_refined_str":{Value: refinedUnknownString(), Type: cty.String},
		"unknown_refined_num":{Value: refinedUnknownNumber(), Type: cty.Number},
		"unknown_refined_list":{Value: refinedUnknownList(), Type: cty.List(cty.String)},
		"list_of_strings":    {Value: cty.ListVal([]cty.Value{cty.StringVal("a"), cty.StringVal("b")}), Type: cty.List(cty.String)},
		"set_of_numbers":     {Value: cty.SetVal([]cty.Value{cty.NumberIntVal(1), cty.NumberIntVal(2)}), Type: cty.Set(cty.Number)},
		"map_simple":         {Value: cty.MapVal(map[string]cty.Value{"a": cty.True, "b": cty.False}), Type: cty.Map(cty.Bool)},
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
			Type: cty.ObjectWithOptionalAttrs(map[string]cty.Type{
				"id": cty.String, "enabled": cty.Bool, "ports": cty.List(cty.Number),
				"config": cty.Object(map[string]cty.Type{ "retries": cty.Number, "params":  cty.Map(cty.String), }),
				"metadata": cty.Map(cty.String), "extra": cty.String,
			}, []string{"metadata"}),
		},
		"dynamic_wrapped_string": {Value: cty.StringVal("dynamic"), Type: cty.DynamicPseudoType},
		"dynamic_wrapped_object": {Value: cty.ObjectVal(map[string]cty.Value{"key": cty.StringVal("value")}), Type: cty.DynamicPseudoType},
	}
}

func generateFixtures(outputDir string) {
	logger.Log(hclog.Info, "📦", "📝", "⏳", "Starting Go fixture generation...")
	testCases := getTestCasesForGeneration()
	if err := os.MkdirAll(outputDir, 0755); err != nil {
		logger.Log(hclog.Error, "📦", "📝", "❌", "Failed to create fixture directory", "error", err)
		os.Exit(1)
	}

	for name, tc := range testCases {
		logger.Log(hclog.Debug, "📦", "📝", "⚙️", "Processing case", "name", name, "type", tc.Type.FriendlyName(), "value", tc.Value.GoString())
		bytes, err := msgpack.Marshal(tc.Value, tc.Type)
		if err != nil {
			logger.Log(hclog.Error, "📦", "📝", "❌", "Failed to marshal", "case", name, "error", err)
			os.Exit(1)
		}

		filename := filepath.Join(outputDir, name+".msgpack")
		if err := os.WriteFile(filename, bytes, 0644); err != nil {
			logger.Log(hclog.Error, "📦", "📝", "❌", "Failed to write fixture", "file", filename, "error", err)
			os.Exit(1)
		}
		logger.Log(hclog.Debug, "📦", "📝", "✅", "Wrote fixture", "file", filename)
	}
	logger.Log(hclog.Info, "📦", "📝", "✅", "Go fixture generation complete.")
}

// --- VERIFY LOGIC ---
type ManifestEntry struct {
	Type      json.RawMessage `json:"type"`
	Value     json.RawMessage `json:"value"`
	IsUnknown bool            `json:"isUnknown"`
	IsNull    bool            `json:"isNull"`
}

func parseCtyType(data json.RawMessage) (cty.Type, error) {
	var typeStr string
	if err := json.Unmarshal(data, &typeStr); err == nil {
		switch typeStr {
		case "string": return cty.String, nil
		case "number": return cty.Number, nil
		case "bool": return cty.Bool, nil
		case "dynamic": return cty.DynamicPseudoType, nil
		default: return cty.NilType, fmt.Errorf("unknown primitive type string: %s", typeStr)
		}
	}

	var typeList []json.RawMessage
	if err := json.Unmarshal(data, &typeList); err == nil {
		if len(typeList) < 2 { return cty.NilType, fmt.Errorf("type array must have at least 2 elements") }
		var typeKind string
		if err := json.Unmarshal(typeList[0], &typeKind); err != nil { return cty.NilType, err }

		switch typeKind {
		case "list", "set", "map":
			elemType, err := parseCtyType(typeList[1])
			if err != nil { return cty.NilType, err }
			if typeKind == "list" { return cty.List(elemType), nil }
			if typeKind == "set" { return cty.Set(elemType), nil }
			return cty.Map(elemType), nil
		case "object":
			var attrTypesRaw map[string]json.RawMessage
			if err := json.Unmarshal(typeList[1], &attrTypesRaw); err != nil { return cty.NilType, err }
			attrTypes := make(map[string]cty.Type)
			for name, rawType := range attrTypesRaw {
				attrType, err := parseCtyType(rawType)
				if err != nil { return cty.NilType, err }
				attrTypes[name] = attrType
			}
			if len(typeList) > 2 {
				var optionals []string
				if err := json.Unmarshal(typeList[2], &optionals); err != nil { return cty.NilType, err }
				return cty.ObjectWithOptionalAttrs(attrTypes, optionals), nil
			}
			return cty.Object(attrTypes), nil
		case "tuple":
			var elemTypesRaw []json.RawMessage
			if err := json.Unmarshal(typeList[1], &elemTypesRaw); err != nil { return cty.NilType, err }
			elemTypes := make([]cty.Type, len(elemTypesRaw))
			for i, rawType := range elemTypesRaw {
				elemType, err := parseCtyType(rawType)
				if err != nil { return cty.NilType, err }
				elemTypes[i] = elemType
			}
			return cty.Tuple(elemTypes), nil
		default: return cty.NilType, fmt.Errorf("unknown complex type kind: %s", typeKind)
		}
	}
	return cty.NilType, fmt.Errorf("invalid type specification format")
}

func buildExpectedValue(ty cty.Type, valData json.RawMessage, path []string) (cty.Value, error) {
	if string(valData) == "null" {
		return cty.NullVal(ty), nil
	}

	var sentinel map[string]interface{}
	if err := json.Unmarshal(valData, &sentinel); err == nil {
		if val, ok := sentinel["$pyvider-cty-special-value"].(string); ok && val == "unknown" {
			// If there are no refinements, it's an unrefined unknown.
			if _, hasRefinements := sentinel["refinements"]; !hasRefinements {
				return cty.UnknownVal(ty), nil
			}

			// Otherwise, build a refined unknown value.
			builder := cty.UnknownVal(ty).Refine()
			refinementsData, _ := sentinel["refinements"]
			refinementsMap, ok := refinementsData.(map[string]interface{})
			if !ok { return cty.NilVal, fmt.Errorf("refinements must be an object") }

			if isNull, ok := refinementsMap["is_known_null"].(bool); ok {
				if isNull { builder = builder.Null() } else { builder = builder.NotNull() }
			}
			if prefix, ok := refinementsMap["string_prefix"].(string); ok {
				builder = builder.StringPrefix(prefix)
			}
			if lowerBound, ok := refinementsMap["number_lower_bound"].([]interface{}); ok {
				numStr, _ := lowerBound[0].(string)
				inclusive, _ := lowerBound[1].(bool)
				bf := new(big.Float); bf.SetString(numStr)
				builder = builder.NumberRangeLowerBound(cty.NumberVal(bf), inclusive)
			}
			if upperBound, ok := refinementsMap["number_upper_bound"].([]interface{}); ok {
				numStr, _ := upperBound[0].(string)
				inclusive, _ := upperBound[1].(bool)
				bf := new(big.Float); bf.SetString(numStr)
				builder = builder.NumberRangeUpperBound(cty.NumberVal(bf), inclusive)
			}
			if lower, ok := refinementsMap["collection_length_lower_bound"].(float64); ok {
				builder = builder.CollectionLengthLowerBound(int(lower))
			}
			if upper, ok := refinementsMap["collection_length_upper_bound"].(float64); ok {
				builder = builder.CollectionLengthUpperBound(int(upper))
			}
			return builder.NewValue(), nil
		}
	}

	if ty == cty.DynamicPseudoType {
		inferredType, err := ctyjson.ImpliedType(valData)
		if err != nil {
			return cty.NilVal, err
		}
		return ctyjson.Unmarshal(valData, inferredType)
	}

	if ty.IsPrimitiveType() {
		switch ty {
		case cty.String:
			var s string; if err := json.Unmarshal(valData, &s); err != nil { return cty.NilVal, err }; return cty.StringVal(s), nil
		case cty.Number:
			var s string; if err := json.Unmarshal(valData, &s); err != nil { return cty.NilVal, err }; bf := new(big.Float); _, ok := bf.SetString(s); if !ok { return cty.NilVal, fmt.Errorf("invalid number string") }; return cty.NumberVal(bf), nil
		case cty.Bool:
			var b bool; if err := json.Unmarshal(valData, &b); err != nil { return cty.NilVal, err }; return cty.BoolVal(b), nil
		}
	}
	if ty.IsListType() || ty.IsSetType() || ty.IsTupleType() {
		var rawElems []json.RawMessage; if err := json.Unmarshal(valData, &rawElems); err != nil { return cty.NilVal, err }
		if len(rawElems) == 0 {
			if ty.IsListType() { return cty.ListValEmpty(ty.ElementType()), nil }
			if ty.IsSetType() { return cty.SetValEmpty(ty.ElementType()), nil }
			return cty.TupleVal(make([]cty.Value, 0)), nil
		}
		vals := make([]cty.Value, len(rawElems))
		for i, rawElem := range rawElems {
			var elemTy cty.Type
			if ty.IsTupleType() {
				elemTy = ty.TupleElementType(i)
			} else {
				elemTy = ty.ElementType()
			}
			val, err := buildExpectedValue(elemTy, rawElem, append(path, fmt.Sprintf("[%d]", i))); if err != nil { return cty.NilVal, err }; vals[i] = val
		}
		if ty.IsListType() { return cty.ListVal(vals), nil }
		if ty.IsSetType() { return cty.SetVal(vals), nil }
		return cty.TupleVal(vals), nil
	}
	if ty.IsMapType() || ty.IsObjectType() {
		var rawMap map[string]json.RawMessage; if err := json.Unmarshal(valData, &rawMap); err != nil { return cty.NilVal, err }
		if len(rawMap) == 0 {
			if ty.IsObjectType() { return cty.ObjectVal(map[string]cty.Value{}), nil }
			return cty.MapValEmpty(ty.ElementType()), nil
		}
		vals := make(map[string]cty.Value)
		for k, rawVal := range rawMap {
			var elemTy cty.Type
			if ty.IsObjectType() {
				elemTy = ty.AttributeType(k)
			} else {
				elemTy = ty.ElementType()
			}
			val, err := buildExpectedValue(elemTy, rawVal, append(path, fmt.Sprintf(".%s", k))); if err != nil { return cty.NilVal, err }; vals[k] = val
		}
		if ty.IsMapType() { return cty.MapVal(vals), nil }
		return cty.ObjectVal(vals), nil
	}
	return cty.NilVal, fmt.Errorf("cannot build expected value for type %s at path %s", ty.FriendlyName(), strings.Join(path, ""))
}

func verifyFixtures(fixtureDir string) {
	logger.Log(hclog.Info, "🔍", "🔎", "⏳", "Starting verification of Python-generated fixtures...")
	manifestPath := filepath.Join(fixtureDir, "manifest.json")
	manifestBytes, err := os.ReadFile(manifestPath)
	if err != nil {
		logger.Log(hclog.Error, "🔍", "💾", "❌", "Failed to read manifest.json", "error", err)
		os.Exit(1)
	}

	var manifest map[string]ManifestEntry
	if err := json.Unmarshal(manifestBytes, &manifest); err != nil {
		logger.Log(hclog.Error, "🔍", "📄", "❌", "Failed to parse manifest.json", "error", err)
		os.Exit(1)
	}

	failures := 0
	for name, entry := range manifest {
		path := []string{name}
		logger.Log(hclog.Trace, "🔍", "📄", "⚙️", "Processing manifest entry", "case", name, "entry_type", string(entry.Type), "entry_value", string(entry.Value))
		ty, err := parseCtyType(entry.Type)
		if err != nil {
			logger.Log(hclog.Error, "🔍", "🔧", "❌", "Failed to parse type from manifest", "case", name, "error", err)
			failures++
			continue
		}
		logger.Log(hclog.Trace, "🔍", "🔧", "✅", "Parsed type", "case", name, "type", ty.GoString())

		fixturePath := filepath.Join(fixtureDir, name+".msgpack")
		fixtureBytes, err := os.ReadFile(fixturePath)
		if err != nil {
			logger.Log(hclog.Error, "🔍", "💾", "❌", "Failed to read fixture file", "case", name, "error", err)
			failures++
			continue
		}
		logger.Log(hclog.Trace, "🔍", "💾", "✅", "Read fixture bytes", "case", name, "byte_count", len(fixtureBytes))

		deserializedVal, err := msgpack.Unmarshal(fixtureBytes, ty)
		if err != nil {
			logger.Log(hclog.Error, "🔍", "🔧", "❌", "Failed to deserialize fixture", "case", name, "error", err)
			failures++
			continue
		}
		logger.Log(hclog.Trace, "🔍", "🔧", "✅", "Deserialized value from fixture", "case", name, "value", deserializedVal.GoString())

		expectedVal, err := buildExpectedValue(ty, entry.Value, path)
		if err != nil {
			logger.Log(hclog.Error, "🔍", "🔧", "❌", "Failed to build expected value", "path", strings.Join(path, ""), "error", err)
			failures++
			continue
		}
		logger.Log(hclog.Trace, "🔍", "🔧", "✅", "Built expected value from manifest", "case", name, "value", expectedVal.GoString())

		if entry.IsUnknown {
			if deserializedVal.IsKnown() {
				logger.Log(hclog.Error, "🔍", "📊", "❌", "Value should be Unknown, but is Known", "path", strings.Join(path, ""))
				failures++
			}
		} else if entry.IsNull {
			if !deserializedVal.IsNull() {
				logger.Log(hclog.Error, "🔍", "📊", "❌", "Value should be Null, but is not", "path", strings.Join(path, ""))
				failures++
			}
		} else {
			if !deserializedVal.IsKnown() {
				logger.Log(hclog.Error, "🔍", "📊", "❌", "Value should be Known, but is Unknown", "path", strings.Join(path, ""))
				failures++
				continue
			}
			eqResult := deserializedVal.Equals(expectedVal)
			if !(eqResult.IsKnown() && eqResult.True()) {
				logger.Log(hclog.Error, "🔍", "📊", "❌", "Deserialized value does not equal expected value", "path", strings.Join(path, ""))
				logger.Log(hclog.Error, "🔍", "📊", "➡️", "Expected", "value", expectedVal.GoString())
				logger.Log(hclog.Error, "🔍", "📊", "⬅️", "Got", "value", deserializedVal.GoString())
				failures++
			}
		}
		if failures == 0 {
			logger.Log(hclog.Debug, "🔍", "🔎", "✅", "Verified fixture", "case", name)
		}
	}

	if failures > 0 {
		logger.Log(hclog.Error, "🔍", "🏁", "❌", fmt.Sprintf("%d verification(s) failed.", failures))
		os.Exit(1)
	}
	logger.Log(hclog.Info, "🔍", "🏁", "✅", "All Python-generated fixtures verified successfully.")
}

func main() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}
