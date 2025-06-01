
package main

import (
	"encoding/json" // Keep one
	"flag"
	"fmt" // Keep one
	"io/ioutil"
	"log"
	// "math/big" // Removed
	"os"
	"path/filepath"
	"reflect"
	"strings"

	"github.com/vmihailenco/msgpack/v5" // Added for Msgpack support
	"github.com/zclconf/go-cty/cty"
	"gopkg.in/yaml.v2"
)

// --- Logging Setup ---

// Define Emoji Mappings for cty context
const (
	// Domains
	domTypeSystem = "🏗️ "
	domValue      = "🧱"
	domValidation = "🛡️"
	domPath       = "🗺️" // If path logic were added
	domEncoding   = "📦" // If specific encoding logic were added
	domTooling    = "⚙️ "
	domError      = "❗"

	// Actions
	actDefine   = "🔧"
	actValidate = "🔍"
	actConvert  = "🔄"
	actAccess   = "🔩"
	actNavigate = "➡️" // If path logic were added
	actMarshal  = "✏️"
	actWrite    = "📄"
	actRead     = "📥" // Added for reading files
	actInfo     = "ℹ️ "

	// Statuses
	statOK    = "✅"
	statError = "❌"
	statWarn  = "⚠️"
	statStart = "⏳" // Using pending for start
	statEmpty = "⭕"
)

// LogPrefix generates the 3-emoji prefix
func LogPrefix(domain, action, status string) string {
	return fmt.Sprintf("%s%s%s", domain, action, status)
}

// logf formats and prints a log message with prefix
func logf(prefix string, format string, v ...interface{}) {
	log.Printf("%s "+format, append([]interface{}{prefix}, v...)...)
}

func init() {
	// Configure logger for detailed output (timestamp is useful)
	log.SetFlags(log.LstdFlags | log.Lshortfile) // Keep timestamp and file/line
	// Optional: Display emoji matrix on startup
	if os.Getenv("CTY_SHOW_EMOJI_MATRIX") == "true" {
		printEmojiMatrix()
	}
}

func printEmojiMatrix() {
	fmt.Println("\n--- CTY Tool Emoji Matrix ---")
	fmt.Println(" Structure: [Domain][Action][Status]")
	fmt.Println("\n Domains (Component):")
	fmt.Printf("  %s : TypeSystem (Types)\n", domTypeSystem)
	fmt.Printf("  %s : Value (Values)\n", domValue)
	fmt.Printf("  %s : Validation\n", domValidation)
	fmt.Printf("  %s : Path\n", domPath)
	fmt.Printf("  %s : Encoding\n", domEncoding)
	fmt.Printf("  %s : Tooling (Helpers, I/O)\n", domTooling)
	fmt.Printf("  %s : Error/Exception\n", domError)
	fmt.Println("\n Actions (Operation):")
	fmt.Printf("  %s : Define/Create\n", actDefine)
	fmt.Printf("  %s : Validate/Check\n", actValidate)
	fmt.Printf("  %s : Convert/Coerce\n", actConvert)
	fmt.Printf("  %s : Access/Get\n", actAccess)
	fmt.Printf("  %s : Navigate\n", actNavigate)
	fmt.Printf("  %s : Serialize/Marshal\n", actMarshal)
	fmt.Printf("  %s : Write/Output\n", actWrite)
	fmt.Printf("  %s : Info/Log Step\n", actInfo)
	fmt.Println("\n Status (Outcome):")
	fmt.Printf("  %s : Success/OK\n", statOK)
	fmt.Printf("  %s : Error/Fail\n", statError)
	fmt.Printf("  %s : Warning/Caveat\n", statWarn)
	fmt.Printf("  %s : Pending/Start\n", statStart)
	fmt.Printf("  %s : Empty/Null/None\n", statEmpty)
	fmt.Println("-----------------------------")
}

// --- Helper Functions ---

// TestCaseData struct to hold data from YAML files
type TestCaseData struct {
	Name           string      `yaml:"name"`
	Description    string      `yaml:"description"`
	TypeDefinition string      `yaml:"type_definition"`
	RawInput       interface{} `yaml:"raw_input"`
}

// JSONComparableValue struct for serializing cty.Value to JSON
type JSONComparableValue struct {
	TypeName  string        `json:"type_name"`
	Value     interface{}   `json:"value"`
	IsUnknown bool          `json:"is_unknown"`
	IsNull    bool          `json:"is_null"`
	Marks     []string      `json:"marks"`
}

func parseTypeDefinition(typeStr string) (cty.Type, error) {
	logf(LogPrefix(domTypeSystem, actConvert, statStart), "Parsing type definition string: '%s'", typeStr)
	if typeStr == "string" {
		logf(LogPrefix(domTypeSystem, actConvert, statOK), "Parsed to cty.String")
		return cty.String, nil
	} else if typeStr == "number" {
		logf(LogPrefix(domTypeSystem, actConvert, statOK), "Parsed to cty.Number")
		return cty.Number, nil
	} else if typeStr == "bool" {
		logf(LogPrefix(domTypeSystem, actConvert, statOK), "Parsed to cty.Bool")
		return cty.Bool, nil
	} else if strings.HasPrefix(typeStr, "list(") && strings.HasSuffix(typeStr, ")") {
		innerTypeStr := typeStr[len("list(") : len(typeStr)-1]
		innerType, err := parseTypeDefinition(innerTypeStr)
		if err != nil {
			logf(LogPrefix(domTypeSystem, actConvert, statError), "Error parsing inner type for list: %v", err)
			return cty.NilType, err
		}
		logf(LogPrefix(domTypeSystem, actConvert, statOK), "Parsed to cty.List(%s)", innerType.FriendlyName())
		return cty.List(innerType), nil
	} else if strings.HasPrefix(typeStr, "map(") && strings.HasSuffix(typeStr, ")") {
		valueTypeStr := typeStr[len("map(") : len(typeStr)-1]
		valueType, err := parseTypeDefinition(valueTypeStr)
		if err != nil {
			logf(LogPrefix(domTypeSystem, actConvert, statError), "Error parsing value type for map: %v", err)
			return cty.NilType, err
		}
		logf(LogPrefix(domTypeSystem, actConvert, statOK), "Parsed to cty.Map(cty.String, %s)", valueType.FriendlyName())
		return cty.Map(valueType), nil // cty maps always have string keys
	} else if strings.HasPrefix(typeStr, "tuple([") && strings.HasSuffix(typeStr, "])") {
		elementTypesStr := typeStr[len("tuple([") : len(typeStr)-2]
		if elementTypesStr == "" { // Empty tuple
			logf(LogPrefix(domTypeSystem, actConvert, statOK), "Parsed to empty cty.Tuple")
			return cty.EmptyTuple, nil
		}
		elemStrs := strings.Split(elementTypesStr, ",")
		elemTypes := make([]cty.Type, len(elemStrs))
		for i, s := range elemStrs {
			ty, err := parseTypeDefinition(strings.TrimSpace(s))
			if err != nil {
				logf(LogPrefix(domTypeSystem, actConvert, statError), "Error parsing element type for tuple: %v", err)
				return cty.NilType, err
			}
			elemTypes[i] = ty
		}
		logf(LogPrefix(domTypeSystem, actConvert, statOK), "Parsed to cty.Tuple with %d elements", len(elemTypes))
		return cty.Tuple(elemTypes), nil
	} else if strings.HasPrefix(typeStr, "object({") && strings.HasSuffix(typeStr, "})") {
		attrsStr := typeStr[len("object({") : len(typeStr)-2]
		if attrsStr == "" { // Empty object
			logf(LogPrefix(domTypeSystem, actConvert, statOK), "Parsed to empty cty.Object")
			return cty.EmptyObject, nil
		}
		attrPairs := strings.Split(attrsStr, ",")
		attrTypes := make(map[string]cty.Type)
		for _, pair := range attrPairs {
			parts := strings.SplitN(pair, "=", 2)
			if len(parts) != 2 {
				return cty.NilType, fmt.Errorf("invalid attribute format '%s' in object type string: %s", pair, typeStr)
			}
			name := strings.TrimSpace(parts[0])
			typeDef := strings.TrimSpace(parts[1])
			attrT, err := parseTypeDefinition(typeDef)
			if err != nil {
				return cty.NilType, fmt.Errorf("error parsing attribute type for '%s': %w", name, err)
			}
			attrTypes[name] = attrT
		}
		logf(LogPrefix(domTypeSystem, actConvert, statOK), "Parsed to cty.Object with attributes: %v", attrTypes)
		return cty.Object(attrTypes), nil
	}

	err := fmt.Errorf("unsupported type definition string: %s", typeStr)
	logf(LogPrefix(domTypeSystem, actConvert, statError), "%v", err)
	return cty.NilType, err
}

func formatCtyTypeFriendlyName(ty cty.Type) string {
	if ty.IsListType() {
		return fmt.Sprintf("list(%s)", formatCtyTypeFriendlyName(ty.ElementType()))
	} else if ty.IsSetType() {
		return fmt.Sprintf("set(%s)", formatCtyTypeFriendlyName(ty.ElementType()))
	} else if ty.IsMapType() {
		// Assuming string keys for simplicity in POC, matching Python's simplified map type name
		return fmt.Sprintf("map(%s)", formatCtyTypeFriendlyName(ty.ElementType()))
	} else if ty.IsObjectType() {
		attrs := []string{}
		for name, attrTy := range ty.AttributeTypes() {
			attrs = append(attrs, fmt.Sprintf("%s=%s", name, formatCtyTypeFriendlyName(attrTy)))
		}
		// Sort attributes for consistent naming if order matters, not done here for POC simplicity
		return fmt.Sprintf("object({%s})", strings.Join(attrs, ","))
	} else if ty.IsTupleType() {
		els := []string{}
		for _, elTy := range ty.TupleElementTypes() {
			els = append(els, formatCtyTypeFriendlyName(elTy))
		}
		return fmt.Sprintf("tuple([%s])", strings.Join(els, ","))
	}
	return ty.FriendlyName() // Default for primitives and others
}


func ctyValueToJSONComparable(val cty.Value) (JSONComparableValue, error) {
	typeName := formatCtyTypeFriendlyName(val.Type())

	var processedValue interface{}
	if !val.IsKnown() || val.IsNull() {
		processedValue = nil
	} else {
		switch {
		case val.Type().IsPrimitiveType():
			if val.Type() == cty.String {
				processedValue = val.AsString()
			} else if val.Type() == cty.Number {
				// Ensure numbers are strings for JSON
				// Assuming val.AsBigFloat() is still the way to get the number,
				// even if math/big is not directly used elsewhere.
				// If AsBigFloat() is removed or changed in cty, this needs adjustment.
				// For POC, assuming AsBigFloat() is available.
				processedValue = val.AsBigFloat().Text('f', -1)
			} else if val.Type() == cty.Bool {
				processedValue = val.True() // AsBool not available, use True()
			} else {
				// Fallback for other potential primitives
				return JSONComparableValue{}, fmt.Errorf("unhandled primitive type for JSON conversion: %s", val.Type().FriendlyName())
			}
		case val.Type().IsListType() || val.Type().IsTupleType():
			var elements []JSONComparableValue
			it := val.ElementIterator()
			for it.Next() {
				_, elemVal := it.Element()
				elemJSON, err := ctyValueToJSONComparable(elemVal)
				if err != nil {
					return JSONComparableValue{}, fmt.Errorf("failed to convert list/tuple element: %w", err)
				}
				elements = append(elements, elemJSON)
			}
			processedValue = elements
		case val.Type().IsMapType():
			elements := make(map[string]JSONComparableValue)
			it := val.ElementIterator()
			for it.Next() {
				keyVal, elemVal := it.Element()
				elemJSON, err := ctyValueToJSONComparable(elemVal)
				if err != nil {
					return JSONComparableValue{}, fmt.Errorf("failed to convert map element: %w", err)
				}
				elements[keyVal.AsString()] = elemJSON
			}
			processedValue = elements
		case val.Type().IsSetType():
			var elements []JSONComparableValue
			it := val.ElementIterator()
			for it.Next() {
				_, elemVal := it.Element()
				elemJSON, err := ctyValueToJSONComparable(elemVal)
				if err != nil {
					return JSONComparableValue{}, fmt.Errorf("failed to convert set element: %w", err)
				}
				elements = append(elements, elemJSON)
			}
			// TODO: Sort elements for consistent output if needed, complex for JSON structs
			processedValue = elements
		default:
			return JSONComparableValue{}, fmt.Errorf("unhandled cty type for JSON conversion: %s", val.Type().FriendlyName())
		}
	}

	jsonComparable := JSONComparableValue{
		TypeName:  typeName,
		Value:     processedValue,
		IsUnknown: !val.IsKnown(),
		IsNull:    val.IsNull(),
		Marks:     []string{}, // Initialize as empty slice
	}

	if val.IsKnown() { // Marks only make sense for known values
		valMarks := val.Marks()
		if valMarks != nil && len(valMarks) > 0 {
			for mark := range valMarks {
				// Using fmt.Sprintf as a general way to get string representation of mark
				// For cty.Value marks, mark.GoString() might be more specific if available and desired
				jsonComparable.Marks = append(jsonComparable.Marks, fmt.Sprintf("%v", mark))
			}
			// Optional: Sort marks for consistent JSON output if order isn't guaranteed
			// sort.Strings(jsonComparable.Marks) // Requires "sort" import
		}
	}
	// If val is unknown, jsonComparable.Marks will remain []string{}

	return jsonComparable, nil
}


func goToCtyValue(v interface{}, targetType cty.Type) (cty.Value, error) {
	pfx := LogPrefix(domValue, actConvert, statStart)
	logf(pfx, "Converting Go value of type %T to cty.Value (target: %s)", v, targetType.FriendlyName())

	if strVal, ok := v.(string); ok && strVal == "__unknown__" {
		logf(LogPrefix(domValue, actDefine, statOK), "Input is '__unknown__', creating unknown value")
		return cty.UnknownVal(targetType), nil
	}
	if v == nil {
		logf(LogPrefix(domValue, actDefine, statOK), "Input is nil, creating null value")
		return cty.NullVal(targetType), nil
	}

	switch targetType {
	case cty.String:
		if strVal, ok := v.(string); ok {
			return cty.StringVal(strVal), nil
		}
		return cty.NilVal, fmt.Errorf("expected string, got %T", v)
	case cty.Number:
		// YAML unmarshals numbers as int or float64 typically
		if intVal, ok := v.(int); ok {
			return cty.NumberIntVal(int64(intVal)), nil
		}
		if floatVal, ok := v.(float64); ok {
			return cty.NumberFloatVal(floatVal), nil
		}
		// Attempt to convert string to number if that's a desired feature
		// For now, strict type matching from YAML parsed types
		return cty.NilVal, fmt.Errorf("expected number (int/float64), got %T", v)
	case cty.Bool:
		if boolVal, ok := v.(bool); ok {
			return cty.BoolVal(boolVal), nil
		}
		return cty.NilVal, fmt.Errorf("expected bool, got %T", v)
	default:
		if targetType.IsListType() {
			if sliceVal, ok := v.([]interface{}); ok {
				return sliceToCtyList(sliceVal, targetType.ElementType())
			}
			return cty.NilVal, fmt.Errorf("expected slice for list type, got %T for target %s", v, targetType.FriendlyName())
		} else if targetType.IsMapType() {
			if mapVal, ok := v.(map[interface{}]interface{}); ok { // YAML gives map[interface{}]interface{}
				return mapToCtyMap(mapVal, targetType.ElementType())
			} else if mapStringVal, ok := v.(map[string]interface{}); ok { // Handle if already string keys
				return mapStringToCtyMap(mapStringVal, targetType.ElementType())
			}
			return cty.NilVal, fmt.Errorf("expected map for map type, got %T for target %s", v, targetType.FriendlyName())
		} else if targetType.IsTupleType() {
			if sliceVal, ok := v.([]interface{}); ok {
				return sliceToCtyTuple(sliceVal, targetType.TupleElementTypes())
			}
			return cty.NilVal, fmt.Errorf("expected slice for tuple type, got %T for target %s", v, targetType.FriendlyName())
		} else if targetType.IsObjectType() {
			if mapVal, ok := v.(map[interface{}]interface{}); ok {
				return mapToCtyObject(mapVal, targetType.AttributeTypes())
			} else if mapStringVal, ok := v.(map[string]interface{}); ok {
                 return mapStringToCtyObject(mapStringVal, targetType.AttributeTypes())
            }
			return cty.NilVal, fmt.Errorf("expected map for object type, got %T for target %s", v, targetType.FriendlyName())
		}
		return cty.NilVal, fmt.Errorf("unhandled target cty.Type in goToCtyValue: %s", targetType.FriendlyName())
	}
}


func sliceToCtyList(data []interface{}, elementType cty.Type) (cty.Value, error) {
	pfx := LogPrefix(domValue, actConvert, statStart)
	logf(pfx, "Converting slice with %d elements to cty.ListVal (element type: %s)", len(data), elementType.FriendlyName())
	if len(data) == 0 {
		logf(LogPrefix(domValue, actConvert, statEmpty), "Slice is empty, creating empty ListVal of type %s", elementType.FriendlyName())
		return cty.ListValEmpty(elementType), nil
	}
	vals := make([]cty.Value, len(data))
	for i, item := range data {
		val, err := goToCtyValue(item, elementType)
		if err != nil {
			logf(LogPrefix(domError, actConvert, statError), "Failed converting slice element %d for list: %v", i, err)
			return cty.NilVal, fmt.Errorf("error converting slice element %d for list: %w", i, err)
		}
		vals[i] = val
	}
	logf(LogPrefix(domValue, actConvert, statOK), "Creating ListVal with element type: %s", elementType.FriendlyName())
	return cty.ListVal(vals), nil
}

func mapToCtyMap(data map[interface{}]interface{}, valueType cty.Type) (cty.Value, error) {
	pfx := LogPrefix(domValue, actConvert, statStart)
	logf(pfx, "Converting map[interface{}]interface{} with %d elements to cty.MapVal (value type: %s)", len(data), valueType.FriendlyName())
	if len(data) == 0 {
		return cty.MapValEmpty(valueType), nil
	}
	mapValues := make(map[string]cty.Value)
	for k, v := range data {
		keyStr, ok := k.(string)
		if !ok {
			return cty.NilVal, fmt.Errorf("map key is not a string: %T", k)
		}
		val, err := goToCtyValue(v, valueType)
		if err != nil {
			return cty.NilVal, fmt.Errorf("error converting map value for key '%s': %w", keyStr, err)
		}
		mapValues[keyStr] = val
	}
	return cty.MapVal(mapValues), nil
}
func mapStringToCtyMap(data map[string]interface{}, valueType cty.Type) (cty.Value, error) {
    pfx := LogPrefix(domValue, actConvert, statStart)
    logf(pfx, "Converting map[string]interface{} with %d elements to cty.MapVal (value type: %s)", len(data), valueType.FriendlyName())
    if len(data) == 0 {
        return cty.MapValEmpty(valueType), nil
    }
    mapValues := make(map[string]cty.Value)
    for k, v := range data {
        val, err := goToCtyValue(v, valueType)
        if err != nil {
            return cty.NilVal, fmt.Errorf("error converting map value for key '%s': %w", k, err)
        }
        mapValues[k] = val
    }
    return cty.MapVal(mapValues), nil
}


func sliceToCtyTuple(data []interface{}, elementTypes []cty.Type) (cty.Value, error) {
	if len(data) != len(elementTypes) {
		return cty.NilVal, fmt.Errorf("tuple data length %d does not match element types length %d", len(data), len(elementTypes))
	}
	if len(data) == 0 {
		return cty.EmptyTupleVal, nil
	}
	vals := make([]cty.Value, len(data))
	for i, item := range data {
		val, err := goToCtyValue(item, elementTypes[i])
		if err != nil {
			return cty.NilVal, fmt.Errorf("error converting tuple element %d: %w", i, err)
		}
		vals[i] = val
	}
	return cty.TupleVal(vals), nil
}

func mapToCtyObject(data map[interface{}]interface{}, attrTypes map[string]cty.Type) (cty.Value, error) {
    mapValues := make(map[string]cty.Value)
    for k, v := range data {
        keyStr, ok := k.(string)
        if !ok {
            return cty.NilVal, fmt.Errorf("object attribute key is not a string: %T", k)
        }
        attrType, exists := attrTypes[keyStr]
        if !exists { // Should ideally be handled by schema validation if strict
            logf(LogPrefix(domValue, actConvert, statWarn), "Attribute '%s' not in object schema, attempting dynamic conversion", keyStr)
            attrType = cty.DynamicPseudoType // Or skip/error based on strictness
        }
        val, err := goToCtyValue(v, attrType)
        if err != nil {
            return cty.NilVal, fmt.Errorf("error converting object attribute '%s': %w", keyStr, err)
        }
        mapValues[keyStr] = val
    }
     // Check for missing attributes that are not optional (not implemented here, cty.ObjectVal handles this)
    return cty.ObjectVal(mapValues), nil
}
func mapStringToCtyObject(data map[string]interface{}, attrTypes map[string]cty.Type) (cty.Value, error) {
    mapValues := make(map[string]cty.Value)
    for k, v := range data {
        attrType, exists := attrTypes[k]
        if !exists {
             logf(LogPrefix(domValue, actConvert, statWarn), "Attribute '%s' not in object schema, attempting dynamic conversion", k)
            attrType = cty.DynamicPseudoType
        }
        val, err := goToCtyValue(v, attrType)
        if err != nil {
            return cty.NilVal, fmt.Errorf("error converting object attribute '%s': %w", k, err)
        }
        mapValues[k] = val
    }
    return cty.ObjectVal(mapValues), nil
}


func describeType(ty cty.Type) interface{} {
	pfx := LogPrefix(domTypeSystem, actConvert, statStart) // Use Convert action for description
	logf(pfx, "Describing type: %s", ty.FriendlyName())
	result := make(map[string]interface{}) // Use map for consistent structure

	if ty.IsPrimitiveType() {
		result["type"] = ty.FriendlyName()
	} else if ty.IsListType() {
		result["type"] = "list"
		result["elementType"] = describeType(ty.ElementType())
	} else if ty.IsSetType() {
		result["type"] = "set"
		result["elementType"] = describeType(ty.ElementType())
	} else if ty.IsMapType() {
		result["type"] = "map"
		result["elementType"] = describeType(ty.ElementType()) // In cty, map keys are strings, this is value type
	} else if ty.IsObjectType() {
		attrs := make(map[string]interface{})
		for name, attrTy := range ty.AttributeTypes() {
			attrs[name] = describeType(attrTy)
		}
		result["type"] = "object"
		result["attributes"] = attrs
	} else if ty.IsTupleType() {
		elements := make([]interface{}, len(ty.TupleElementTypes()))
		for i, elemTy := range ty.TupleElementTypes() {
			elements[i] = describeType(elemTy)
		}
		result["type"] = "tuple"
		result["elements"] = elements
	} else if ty == cty.DynamicPseudoType {
		result["type"] = "dynamic"
	} else {
		logf(LogPrefix(domTypeSystem, actConvert, statWarn), "Unknown type encountered during description: %s (%s)", ty.FriendlyName(), reflect.TypeOf(ty).String())
		result["type"] = "unknown"
		result["details"] = ty.FriendlyName()
	}
	logf(LogPrefix(domTypeSystem, actConvert, statOK), "Finished describing type: %s", ty.FriendlyName())
	return result
}


// --- Main Function ---
func main() {
	logf(LogPrefix(domTooling, actInfo, statStart), "Starting Go cty generator script")

	var outputToStdout bool
	var formatFlag string
	var inputFileFlag string
	var inputFileFormatFlag string
	var targetTypeStringFlag string

	flag.BoolVar(&outputToStdout, "stdout", false, "Output value to stdout instead of file (behavior depends on format)")
	flag.StringVar(&formatFlag, "format", "json", "Output format: json or msgpack")
	flag.StringVar(&inputFileFlag, "inputFile", "", "Path to a pre-serialized Msgpack input file. If set, -inputFileFormat must be msgpack.")
	flag.StringVar(&inputFileFormatFlag, "inputFileFormat", "yaml", "Format of the primary input data: yaml or msgpack. If msgpack, -inputFile must be provided.")
	flag.StringVar(&targetTypeStringFlag, "targetTypeString", "", "Target cty type string for when -inputFileFormat is msgpack.")
	flag.Parse()

	logf(LogPrefix(domTooling, actInfo, statStart), "Flags parsed: stdout=%v, format=%s, inputFile=%s, inputFileFormat=%s, targetTypeString=%s", outputToStdout, formatFlag, inputFileFlag, inputFileFormatFlag, targetTypeStringFlag)

	if inputFileFormatFlag == "msgpack" {
		if inputFileFlag == "" {
			log.Fatalf("%s -inputFile must be provided when -inputFileFormat is msgpack", LogPrefix(domError, actInfo, statError))
		}
		if targetTypeStringFlag == "" {
			log.Fatalf("%s -targetTypeString must be provided when -inputFileFormat is msgpack", LogPrefix(domError, actInfo, statError))
		}
		logf(LogPrefix(domEncoding, actInfo, statStart), "Msgpack input file format specified. Main YAML argument will be used for metadata only.")
	} else if inputFileFormatFlag != "yaml" {
		log.Fatalf("%s Invalid -inputFileFormat: %s. Must be 'yaml' or 'msgpack'.", LogPrefix(domError, actInfo, statError), inputFileFormatFlag)
	}

	if formatFlag != "json" && formatFlag != "msgpack" {
		log.Fatalf("%s Invalid -format: %s. Must be 'json' or 'msgpack'.", LogPrefix(domError, actInfo, statError), formatFlag)
	}

	if flag.NArg() < 1 {
		log.Fatalf("%s Usage: go run go_cty_generator.go [flags] <path_to_testcase.yaml>", LogPrefix(domError, actInfo, statError))
	}
	testCasePath := flag.Arg(0)

	if _, err := os.Stat(testCasePath); os.IsNotExist(err) {
		log.Fatalf("%s Test case YAML file not found: %s", LogPrefix(domError, actInfo, statError), testCasePath)
	}

	outputBaseDir := filepath.Join("output")
	if !outputToStdout { // Create output dir only if not writing main output to stdout
		if formatFlag == "json" || (formatFlag == "msgpack" && inputFileFormatFlag == "yaml") { // For msgpack output from yaml, or json output
			err := os.MkdirAll(outputBaseDir, 0755)
			if err != nil {
				log.Fatalf("%s Failed to create base output directory %s: %v", LogPrefix(domError, actWrite, statError), outputBaseDir, err)
			}
		}
	}

	logf(LogPrefix(domTooling, actInfo, statStart), "Processing test case metadata from: %s", testCasePath)
	yamlFile, err := ioutil.ReadFile(testCasePath)
	if err != nil {
		log.Fatalf("%s Failed to read YAML file %s: %v", LogPrefix(domError, actInfo, statError), testCasePath, err)
	}

	var testCaseData TestCaseData // This will hold metadata if input is msgpack
	err = yaml.Unmarshal(yamlFile, &testCaseData)
	if err != nil {
		log.Fatalf("%s Failed to unmarshal YAML from %s: %v", LogPrefix(domError, actInfo, statError), testCasePath, err)
	}

	baseName := filepath.Base(testCasePath)
	testCaseNameFromFile := strings.TrimSuffix(baseName, filepath.Ext(baseName))
	effectiveTestCaseName := testCaseData.Name
	if effectiveTestCaseName == "" {
		effectiveTestCaseName = testCaseNameFromFile
	}

	var ctyType cty.Type
	var ctyVal cty.Value

	if inputFileFormatFlag == "msgpack" {
		logf(LogPrefix(domEncoding, actInfo, statStart), "Processing Msgpack input from file: %s", inputFileFlag)
		ctyType, err = parseTypeDefinition(targetTypeStringFlag)
		if err != nil {
			log.Fatalf("%s Failed to parse targetTypeString '%s' for Msgpack input: %v", LogPrefix(domTypeSystem, actConvert, statError), targetTypeStringFlag, err)
		}
		logf(LogPrefix(domTypeSystem, actConvert, statOK), "Parsed target type for Msgpack input: %s", ctyType.FriendlyName())

		msgpackBytes, err := ioutil.ReadFile(inputFileFlag)
		if err != nil {
			log.Fatalf("%s Failed to read Msgpack input file %s: %v", LogPrefix(domEncoding, actRead, statError), inputFileFlag, err)
		}
		logf(LogPrefix(domEncoding, actRead, statOK), "Read %d bytes from Msgpack input file %s", len(msgpackBytes), inputFileFlag)

		var rawMsgpackData interface{}
		err = msgpack.Unmarshal(msgpackBytes, &rawMsgpackData)
		if err != nil {
			log.Fatalf("%s Failed to unmarshal Msgpack from %s: %v", LogPrefix(domEncoding, actConvert, statError), inputFileFlag, err)
		}
		logf(LogPrefix(domEncoding, actConvert, statOK), "Successfully unmarshalled Msgpack data from %s", inputFileFlag)

		ctyVal, err = goToCtyValue(rawMsgpackData, ctyType)
		if err != nil {
			log.Fatalf("%s Failed to convert unmarshalled Msgpack data to cty.Value for %s: %v", LogPrefix(domValue, actDefine, statError), effectiveTestCaseName, err)
		}
		logf(LogPrefix(domValue, actDefine, statOK), "Created cty.Value from Msgpack input for %s: %s", effectiveTestCaseName, ctyVal.GoString())

		// This path is specifically for "Msgpack to JSON loaded" test cases.
		// Output is always JSON to stdout, overriding -format and -stdout flags for this specific mode.
		logf(LogPrefix(domEncoding, actInfo, statOK), "Msgpack input loaded. Outputting as JSON to stdout.") // Corrected statInfo to statOK
		jsonComparable, err := ctyValueToJSONComparable(ctyVal)
		if err != nil {
			log.Fatalf("%s Failed to convert cty.Value (from Msgpack) to JSONComparableValue for %s: %v", LogPrefix(domError, actMarshal, statError), effectiveTestCaseName, err)
		}
		jsonBytes, err := json.MarshalIndent(jsonComparable, "", "  ")
		if err != nil {
			log.Fatalf("%s Failed to marshal JSON (from Msgpack value) for %s: %v", LogPrefix(domError, actMarshal, statError), effectiveTestCaseName, err)
		}
		fmt.Println(string(jsonBytes))
		logf(LogPrefix(domTooling, actWrite, statOK), "Successfully wrote JSON (from Msgpack value) to stdout for %s", effectiveTestCaseName)
		logf(LogPrefix(domTooling, actInfo, statOK), "Finished processing Msgpack input to JSON output for: %s", testCasePath)
		return // Exit after this special path
	}

	// Else (inputFileFormat is "yaml") - Standard YAML processing
	logf(LogPrefix(domTooling, actInfo, statStart), "Processing YAML input from file: %s", testCasePath) // Corrected statInfo to statStart
	ctyType, err = parseTypeDefinition(testCaseData.TypeDefinition)
	if err != nil {
		log.Fatalf("%s Failed to parse type definition for %s: %v", LogPrefix(domTypeSystem, actConvert, statError), effectiveTestCaseName, err)
	}
	logf(LogPrefix(domTypeSystem, actConvert, statOK), "Parsed type for %s: %s", effectiveTestCaseName, ctyType.FriendlyName())

	ctyVal, err = goToCtyValue(testCaseData.RawInput, ctyType)
	if err != nil {
		log.Fatalf("%s Failed to create cty.Value for %s: %v", LogPrefix(domValue, actDefine, statError), effectiveTestCaseName, err)
	}
	logf(LogPrefix(domValue, actDefine, statOK), "Created cty.Value for %s: %s", effectiveTestCaseName, ctyVal.GoString())

	// Output Handling (only if inputFileFormat was "yaml")
	if formatFlag == "msgpack" {
		logf(LogPrefix(domEncoding, actInfo, statStart), "Format is msgpack. Preparing Msgpack output for %s.", effectiveTestCaseName)
		// Convert cty.Value to JSONComparableValue first, then marshal that to Msgpack
		// This ensures the structure being msgpack'd is the same as what would be json'd
		jsonComparable, err := ctyValueToJSONComparable(ctyVal)
		if err != nil {
			log.Fatalf("%s Failed to convert cty.Value to JSONComparableValue for Msgpack: %v", LogPrefix(domError, actMarshal, statError), err)
		}

		msgpackBytes, err := msgpack.Marshal(jsonComparable)
		if err != nil {
			log.Fatalf("%s Failed to marshal JSONComparableValue to Msgpack for %s: %v", LogPrefix(domEncoding, actMarshal, statError), effectiveTestCaseName, err)
		}
		logf(LogPrefix(domEncoding, actMarshal, statOK), "Successfully marshalled to %d Msgpack bytes for %s", len(msgpackBytes), effectiveTestCaseName)

		if outputToStdout {
			_, err = os.Stdout.Write(msgpackBytes)
			if err != nil {
				log.Fatalf("%s Failed to write Msgpack to stdout for %s: %v", LogPrefix(domEncoding, actWrite, statError), effectiveTestCaseName, err)
			}
			logf(LogPrefix(domTooling, actWrite, statOK), "Successfully wrote Msgpack to stdout for %s", effectiveTestCaseName)
		} else {
			caseOutputDir := filepath.Join(outputBaseDir, testCaseNameFromFile)
			err = os.MkdirAll(caseOutputDir, 0755) // Ensure dir exists
			if err != nil {
				log.Fatalf("%s Failed to create output directory %s: %v", LogPrefix(domError, actWrite, statError), caseOutputDir, err)
			}
			goValueMsgpackFile := filepath.Join(caseOutputDir, "go_value.msgpack")
			err = ioutil.WriteFile(goValueMsgpackFile, msgpackBytes, 0644)
			if err != nil {
				log.Fatalf("%s Failed to write %s: %v", LogPrefix(domEncoding, actWrite, statError), goValueMsgpackFile, err)
			}
			logf(LogPrefix(domTooling, actWrite, statOK), "Successfully wrote %s", goValueMsgpackFile)

			// The go_type.json file should still be written as it's independent of the value format
			typeDescription := describeType(ctyType)
			goTypeBytes, err := json.MarshalIndent(typeDescription, "", "  ")
			if err != nil {
				log.Fatalf("%s Failed to marshal go_type.json for %s (Msgpack mode): %v", LogPrefix(domError, actMarshal, statError), effectiveTestCaseName, err)
			}
			goTypeFile := filepath.Join(caseOutputDir, "go_type.json")
			err = ioutil.WriteFile(goTypeFile, goTypeBytes, 0644)
			if err != nil {
				log.Fatalf("%s Failed to write %s (Msgpack mode): %v", LogPrefix(domError, actWrite, statError), goTypeFile, err)
			}
			logf(LogPrefix(domTooling, actWrite, statOK), "Successfully wrote %s (Msgpack mode)", goTypeFile)
		}
	} else { // formatFlag is "json"
		logf(LogPrefix(domEncoding, actInfo, statStart), "Format is json. Preparing JSON output for %s.", effectiveTestCaseName)
		jsonComparable, err := ctyValueToJSONComparable(ctyVal)
		if err != nil {
			log.Fatalf("%s Failed to convert cty.Value to JSONComparableValue for %s: %v", LogPrefix(domError, actMarshal, statError), effectiveTestCaseName, err)
		}
		goValueBytes, err := json.MarshalIndent(jsonComparable, "", "  ")
		if err != nil {
			log.Fatalf("%s Failed to marshal JSON for %s: %v", LogPrefix(domError, actMarshal, statError), effectiveTestCaseName, err)
		}

		if outputToStdout {
			fmt.Println(string(goValueBytes))
			logf(LogPrefix(domTooling, actWrite, statOK), "Successfully wrote go_value JSON to stdout for %s", effectiveTestCaseName)
		} else {
			caseOutputDir := filepath.Join(outputBaseDir, testCaseNameFromFile) // Recalculate or ensure it's set
			err = os.MkdirAll(caseOutputDir, 0755) // Ensure dir exists
			if err != nil {
				log.Fatalf("%s Failed to create output directory %s: %v", LogPrefix(domError, actWrite, statError), caseOutputDir, err)
			}
			logf(LogPrefix(domTooling, actWrite, statStart), "Ensured output directory exists: %s", caseOutputDir)

			goValueFile := filepath.Join(caseOutputDir, "go_value.json")
			err = ioutil.WriteFile(goValueFile, goValueBytes, 0644)
			if err != nil {
				log.Fatalf("%s Failed to write %s: %v", LogPrefix(domError, actWrite, statError), goValueFile, err)
			}
			logf(LogPrefix(domTooling, actWrite, statOK), "Successfully wrote %s", goValueFile)

			typeDescription := describeType(ctyType)
			goTypeBytes, err := json.MarshalIndent(typeDescription, "", "  ")
			if err != nil {
				log.Fatalf("%s Failed to marshal go_type.json for %s: %v", LogPrefix(domError, actMarshal, statError), effectiveTestCaseName, err)
			}
			goTypeFile := filepath.Join(caseOutputDir, "go_type.json")
			err = ioutil.WriteFile(goTypeFile, goTypeBytes, 0644)
			if err != nil {
				log.Fatalf("%s Failed to write %s: %v", LogPrefix(domError, actWrite, statError), goTypeFile, err)
			}
			logf(LogPrefix(domTooling, actWrite, statOK), "Successfully wrote %s", goTypeFile)
		}
	}

	logf(LogPrefix(domTooling, actInfo, statOK), "Finished processing test case: %s", testCasePath)
}
