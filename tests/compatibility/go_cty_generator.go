
package main

import (
	"encoding/json"
	"fmt"
	"log"
	"math/big"
	"os"
	"reflect" // Needed for type structure generation

	"github.com/zclconf/go-cty/cty"
	// ctyjson "github.com/zclconf/go-cty/cty/json" // Removed as we are not generating this output anymore
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

func goToCtyValue(v interface{}) (cty.Value, error) {
	pfx := LogPrefix(domValue, actConvert, statStart)
	logf(pfx, "Converting Go value of type %T to cty.Value", v)
	switch vTyped := v.(type) {
	case string:
		logf(LogPrefix(domValue, actConvert, statOK), "Converted Go string")
		return cty.StringVal(vTyped), nil
	case bool:
		logf(LogPrefix(domValue, actConvert, statOK), "Converted Go bool")
		return cty.BoolVal(vTyped), nil
	case int:
		logf(LogPrefix(domValue, actConvert, statOK), "Converted Go int to NumberIntVal")
		return cty.NumberIntVal(int64(vTyped)), nil
	case int64:
		logf(LogPrefix(domValue, actConvert, statOK), "Converted Go int64 to NumberIntVal")
		return cty.NumberIntVal(vTyped), nil
	case float64:
		logf(LogPrefix(domValue, actConvert, statOK), "Converted Go float64 to NumberVal (using big.Float)")
		bf := big.NewFloat(vTyped)
		return cty.NumberVal(bf), nil
	case map[string]interface{}:
		logf(LogPrefix(domValue, actConvert, statStart), "Handling nested map -> mapToCtyObject")
		return mapToCtyObject(vTyped)
	case []interface{}:
		logf(LogPrefix(domValue, actConvert, statStart), "Handling nested slice -> sliceToCtyList")
		return sliceToCtyList(vTyped)
	case nil:
		err := fmt.Errorf("cannot convert bare Go nil to cty.Value without target type")
		logf(LogPrefix(domValue, actConvert, statError), "%v", err)
		return cty.NilVal, err
	default:
		err := fmt.Errorf("unhandled Go type in goToCtyValue: %T", v)
		logf(LogPrefix(domValue, actConvert, statError), "%v", err)
		return cty.NilVal, err
	}
}

func mapToCtyObject(data map[string]interface{}) (cty.Value, error) {
	pfx := LogPrefix(domValue, actConvert, statStart)
	logf(pfx, "Converting map with %d keys to cty.ObjectVal", len(data))
	attrs := make(map[string]cty.Value)
	for k, v := range data {
		if v == nil {
			pfxItem := LogPrefix(domValue, actConvert, statWarn)
			logf(pfxItem, "Skipping nil value for key '%s' in mapToCtyObject", k)
			continue // Skip nil values when creating object attributes implicitly
		}
		val, err := goToCtyValue(v)
		if err != nil {
			logf(LogPrefix(domError, actConvert, statError), "Failed converting nested key '%s': %v", k, err)
			return cty.NilVal, fmt.Errorf("error converting nested key '%s': %w", k, err)
		}
		attrs[k] = val
		logf(LogPrefix(domValue, actConvert, statOK), "  Converted key '%s' to type %s", k, val.Type().FriendlyName())
	}
	logf(LogPrefix(domValue, actConvert, statOK), "Successfully created attribute map for ObjectVal")
	return cty.ObjectVal(attrs), nil
}

func sliceToCtyList(data []interface{}) (cty.Value, error) {
	pfx := LogPrefix(domValue, actConvert, statStart)
	logf(pfx, "Converting slice with %d elements to cty.ListVal", len(data))
	if len(data) == 0 {
		logf(LogPrefix(domValue, actConvert, statEmpty), "Slice is empty, creating ListValEmpty(DynamicPseudoType)")
		return cty.ListValEmpty(cty.DynamicPseudoType), nil
	}
	vals := make([]cty.Value, len(data))
	var firstType cty.Type
	for i, v := range data {
		if v == nil {
			err := fmt.Errorf("nil value encountered at index %d in slice; cannot determine list type", i)
			logf(LogPrefix(domValue, actConvert, statError), "%v", err)
			return cty.NilVal, err
		}
		val, err := goToCtyValue(v)
		if err != nil {
			logf(LogPrefix(domError, actConvert, statError), "Failed converting slice element %d: %v", i, err)
			return cty.NilVal, fmt.Errorf("error converting slice element %d: %w", i, err)
		}
		vals[i] = val
		if i == 0 {
			firstType = val.Type()
			logf(LogPrefix(domValue, actInfo, statOK), "  Inferred list element type from first element: %s", firstType.FriendlyName())
		} else {
			if !val.Type().Equals(firstType) {
				err := fmt.Errorf("inconsistent types in slice: expected %s, got %s at index %d. Cannot create concrete cty.ListVal", firstType.FriendlyName(), val.Type().FriendlyName(), i)
				logf(LogPrefix(domError, actConvert, statError), "%v", err)
				return cty.NilVal, err
			}
		}
		logf(LogPrefix(domValue, actConvert, statOK), "  Converted slice element %d to type %s", i, val.Type().FriendlyName())
	}
	logf(LogPrefix(domValue, actConvert, statOK), "Creating ListVal with consistent element type: %s", firstType.FriendlyName())
	return cty.ListVal(vals), nil
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
		result["elementType"] = describeType(ty.ElementType())
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
	logf(LogPrefix(domTooling, actInfo, statStart), "Starting cty generator script")

	// --- Define Basic Types ---
	logf(LogPrefix(domTypeSystem, actDefine, statStart), "Defining basic cty types")
	stringType := cty.String
	numberType := cty.Number
	boolType := cty.Bool
	logf(LogPrefix(domTypeSystem, actDefine, statOK), "Basic types defined")

	// --- Define Complex Types ---
	logf(LogPrefix(domTypeSystem, actDefine, statStart), "Defining complex cty types (network, disk, coordinate)")
	networkObjectType := cty.Object(map[string]cty.Type{
		"subnet":            stringType, "vpc_id": stringType, "security_groups":   cty.List(stringType), "private_endpoints": cty.Set(stringType),
	})
	diskObjectType := cty.Object(map[string]cty.Type{
		"size_gb": numberType, "type": stringType, "iops": numberType,
	})
	coordinateTupleType := cty.Tuple([]cty.Type{
		numberType, numberType, numberType,
	})
	logf(LogPrefix(domTypeSystem, actDefine, statOK), "Defined network, disk, coordinate object/tuple types")

	logf(LogPrefix(domTypeSystem, actDefine, statStart), "Defining main server object type")
	serverObjectType := cty.Object(map[string]cty.Type{
		"name": stringType, "instance_type": stringType, "active": boolType,
		"cpu_cores": numberType, "ram_gb": numberType, "network": networkObjectType,
		"disks": cty.List(diskObjectType), "tags": cty.Map(stringType),
		"metadata": cty.Map(cty.DynamicPseudoType), "location": coordinateTupleType,
		"extra_config": cty.DynamicPseudoType, "backup_policy": stringType, "region": stringType,
	})
	logf(LogPrefix(domTypeSystem, actDefine, statOK), "Defined main server object type")

	// --- Create Raw Go Structure for Comparison ---
	logf(LogPrefix(domTooling, actDefine, statStart), "Defining raw Go structure (map[string]interface{})")
	rawNetwork := map[string]interface{}{
		"subnet": "subnet-abcdef01234567890", "vpc_id": "vpc-0123456789abcdef0",
		"security_groups": []interface{}{"sg-web", "sg-internal"}, "private_endpoints": []interface{}{},
	}
	rawDisk1 := map[string]interface{}{"size_gb": 100, "type": "gp3", "iops": 3000}
	rawDisk2 := map[string]interface{}{"size_gb": 500, "type": "io2", "iops": nil}
	rawDisks := []interface{}{rawDisk1, rawDisk2}
	rawTags := map[string]interface{}{"Environment": "production", "Project": "WebApp", "Owner": "PlatformTeam"}
	rawMetadata := map[string]interface{}{
		"created_by": "automation", "last_check_ok": true, "check_interval": 300,
		"nested_data": map[string]interface{}{"key": "value"},
	}
	rawLocation := []interface{}{45.5231, -122.6765, 15.0}
	// Using placeholder for unknown value in raw structure for clarity
	rawServer := map[string]interface{}{
		"name": "web-server-01", "instance_type": "t3.xlarge", "active": true,
		"cpu_cores": 4, "ram_gb": 16.0, "network": rawNetwork, "disks": rawDisks,
		"tags": rawTags, "metadata": rawMetadata, "location": rawLocation,
		"extra_config": "some arbitrary config string",
		"backup_policy": nil,                   // Go nil represents cty Null conceptually here
		"region":        "__cty_unknown__",     // Placeholder string represents cty Unknown
	}
	rawTopLevel := map[string]interface{}{
		"main_server":   rawServer,
		"backup_server": nil,                      // Go nil represents cty Null object
		"future_server": "__cty_unknown_object__", // Placeholder represents cty Unknown object
	}
	logf(LogPrefix(domTooling, actDefine, statOK), "Defined raw Go structure")


	// --- Create cty Values ---
	logf(LogPrefix(domValue, actDefine, statStart), "Creating cty values from raw structure where needed")
	serverName := cty.StringVal(rawServer["name"].(string))
	instanceType := cty.StringVal(rawServer["instance_type"].(string))
	active := cty.BoolVal(rawServer["active"].(bool))
	cpuCores := cty.NumberIntVal(int64(rawServer["cpu_cores"].(int)))
	ramGb := cty.NumberFloatVal(rawServer["ram_gb"].(float64))

	// Network
	logf(LogPrefix(domValue, actDefine, statStart), "Creating 'network' object value")
	sgVal, err := sliceToCtyList(rawNetwork["security_groups"].([]interface{}))
	if err != nil { log.Fatalf("%s Failed to create security_groups list: %v", LogPrefix(domError, actDefine, statError), err)}
	peVal := cty.SetValEmpty(stringType)
	networkVal := cty.ObjectVal(map[string]cty.Value{
		"subnet": cty.StringVal(rawNetwork["subnet"].(string)), "vpc_id": cty.StringVal(rawNetwork["vpc_id"].(string)),
		"security_groups": sgVal, "private_endpoints": peVal,
	})
    logf(LogPrefix(domValue, actDefine, statOK), "Created 'network' object value")

	// Disks
	logf(LogPrefix(domValue, actDefine, statStart), "Creating 'disks' list value")
	diskVals := make([]cty.Value, len(rawDisks))
	for i, rawDisk := range rawDisks {
		diskMap := rawDisk.(map[string]interface{})
		iopsVal := cty.NullVal(numberType) // Default to null
		if iopsRaw, ok := diskMap["iops"]; ok && iopsRaw != nil {
			switch v := iopsRaw.(type) {
			case int: iopsVal = cty.NumberIntVal(int64(v))
			case int64: iopsVal = cty.NumberIntVal(v)
			default: log.Fatalf("%s Unexpected type for 'iops': %T", LogPrefix(domError, actDefine, statError), iopsRaw)
			}
		}
		diskVals[i] = cty.ObjectVal(map[string]cty.Value{
			"size_gb": cty.NumberIntVal(int64(diskMap["size_gb"].(int))),
			"type":    cty.StringVal(diskMap["type"].(string)),
			"iops":    iopsVal,
		})
	}
	diskListVal := cty.ListVal(diskVals)
    logf(LogPrefix(domValue, actDefine, statOK), "Created 'disks' list value")

	// Tags
	logf(LogPrefix(domValue, actDefine, statStart), "Creating 'tags' map value")
	tagVals := make(map[string]cty.Value)
	for k, v := range rawTags { tagVals[k] = cty.StringVal(v.(string)) }
	tagsMapVal := cty.MapVal(tagVals)
    logf(LogPrefix(domValue, actDefine, statOK), "Created 'tags' map value")


	// Metadata (Using empty map workaround for map(dynamic))
	logf(LogPrefix(domValue, actDefine, statStart), "Creating empty 'metadata' map value (type: map(dynamic))")
	metaMapType := cty.Map(cty.DynamicPseudoType)
	metadataMapVal := cty.MapValEmpty(metaMapType)
	logf(LogPrefix(domValue, actDefine, statOK), "Created empty 'metadata' map value")


	// Location
	logf(LogPrefix(domValue, actDefine, statStart), "Creating 'location' tuple value")
	locFloats := rawLocation
	lat := big.NewFloat(locFloats[0].(float64)); lon := big.NewFloat(locFloats[1].(float64)); alt := big.NewFloat(locFloats[2].(float64))
	locationTupleVal := cty.TupleVal([]cty.Value{ cty.NumberVal(lat), cty.NumberVal(lon), cty.NumberVal(alt) })
    logf(LogPrefix(domValue, actDefine, statOK), "Created 'location' tuple value")


	// Other values
	logf(LogPrefix(domValue, actDefine, statStart), "Creating 'extra_config', 'backup_policy', 'region' values")
	extraConfigVal, err := goToCtyValue(rawServer["extra_config"])
    if err != nil { log.Fatalf("%s Failed to create extra_config value: %v", LogPrefix(domError, actDefine, statError), err) }
	backupPolicyVal := cty.NullVal(stringType)
	// WORKAROUND for Unknown Value Serialization
	logf(LogPrefix(domValue, actDefine, statWarn), "Replacing cty.UnknownVal for 'region' with placeholder string for JSON compatibility.")
	regionVal := cty.StringVal("__cty_unknown__") // Placeholder string
    logf(LogPrefix(domValue, actDefine, statOK), "Created 'extra_config', 'backup_policy', 'region' values")


	// --- Assemble the Main Server Object Value ---
	logf(LogPrefix(domValue, actDefine, statStart), "Assembling main server cty.ObjectVal")
	serverObjectVal := cty.ObjectVal(map[string]cty.Value{
		"name": serverName, "instance_type": instanceType, "active": active,
		"cpu_cores": cpuCores, "ram_gb": ramGb, "network": networkVal,
		"disks": diskListVal, "tags": tagsMapVal, "metadata": metadataMapVal,
		"location": locationTupleVal, "extra_config": extraConfigVal,
		"backup_policy": backupPolicyVal, "region": regionVal,
	})
	logf(LogPrefix(domValue, actDefine, statOK), "Assembled main server cty.ObjectVal")
	logf(LogPrefix(domTooling, actInfo, statOK), "Server Object GoString: %s", serverObjectVal.GoString())


	// --- Assemble Top-Level Value ---
	logf(LogPrefix(domValue, actDefine, statStart), "Assembling top-level cty.MapVal (simplified to avoid panic)")
	topLevelMapType := cty.Map(serverObjectType)
	topLevelValue := cty.MapVal(map[string]cty.Value{
		"main_server": serverObjectVal,
	})
	logf(LogPrefix(domValue, actDefine, statOK), "Assembled top-level cty.MapVal")
	logf(LogPrefix(domTooling, actInfo, statOK), "Top Level GoString: %s", topLevelValue.GoString())


	// --- Generate Output Files ---
	logf(LogPrefix(domTooling, actInfo, statStart), "Generating output files...")

	// 1. Raw Go Structure JSON
	rawFileName := "go-cty-raw-structure.json"
	logf(LogPrefix(domTooling, actMarshal, statStart), "Marshaling raw Go structure to JSON")
	rawJSONBytes, err := json.MarshalIndent(rawTopLevel, "", "  ")
	if err != nil { log.Fatalf("%s Failed to marshal raw Go structure to JSON: %v", LogPrefix(domError, actMarshal, statError), err) }
	logf(LogPrefix(domTooling, actWrite, statStart), "Writing raw structure to %s", rawFileName)
	err = os.WriteFile(rawFileName, rawJSONBytes, 0644)
	if err != nil { log.Fatalf("%s Failed to write raw structure JSON to file '%s': %v", LogPrefix(domError, actWrite, statError), rawFileName, err) }
	logf(LogPrefix(domTooling, actWrite, statOK), "Successfully wrote raw structure to %s", rawFileName)

	// 2. Type Structure JSON
	typeFileName := "go-cty-type-structure.json"
	logf(LogPrefix(domTypeSystem, actConvert, statStart), "Describing top-level cty.Type structure")
	typeDescription := describeType(topLevelMapType)
	logf(LogPrefix(domTypeSystem, actMarshal, statStart), "Marshaling type structure to JSON")
	typeJSONBytes, err := json.MarshalIndent(typeDescription, "", "  ")
	if err != nil { log.Fatalf("%s Failed to marshal type structure to JSON: %v", LogPrefix(domError, actMarshal, statError), err) }
	logf(LogPrefix(domTooling, actWrite, statStart), "Writing type structure to %s", typeFileName)
	err = os.WriteFile(typeFileName, typeJSONBytes, 0644)
	if err != nil { log.Fatalf("%s Failed to write type structure JSON to file '%s': %v", LogPrefix(domError, actWrite, statError), typeFileName, err) }
	logf(LogPrefix(domTooling, actWrite, statOK), "Successfully wrote type structure to %s", typeFileName)

	// --- REMOVED ctyjson Output Generation ---
	logf(LogPrefix(domTooling, actInfo, statOK), "Skipping generation of cty/json output file as requested.")

	fmt.Printf("✅ Successfully generated raw structure and type structure JSON files.\n")
}
