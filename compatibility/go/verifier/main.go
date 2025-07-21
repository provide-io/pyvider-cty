package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"math/big"
	"os"
	"path/filepath"
	"reflect"

	"github.com/hashicorp/go-hclog"
	"github.com/zclconf/go-cty/cty"
	"github.com/zclconf/go-cty/cty/msgpack"
)

type ManifestEntry struct {
	Type      json.RawMessage `json:"type"`
	Value     json.RawMessage `json:"value"`
	IsUnknown bool            `json:"isUnknown"`
	IsNull    bool            `json:"isNull"`
}

var logger hclog.Logger

// Recursively parse a CtyType from its JSON representation.
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
		if len(typeList) != 2 { return cty.NilType, fmt.Errorf("type array must have 2 elements") }
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

// Recursively build an expected cty.Value from the manifest's JSON value.
func buildExpectedValue(ty cty.Type, valData json.RawMessage) (cty.Value, error) {
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
		vals := make([]cty.Value, len(rawElems))
		for i, rawElem := range rawElems {
			elemTy := ty.ElementType()
			if ty.IsTupleType() { elemTy = ty.TupleElementType(i) }
			val, err := buildExpectedValue(elemTy, rawElem); if err != nil { return cty.NilVal, err }; vals[i] = val
		}
		if ty.IsListType() { return cty.ListVal(vals), nil }
		if ty.IsSetType() { return cty.SetVal(vals), nil }
		return cty.TupleVal(vals), nil
	}
	if ty.IsMapType() || ty.IsObjectType() {
		var rawMap map[string]json.RawMessage; if err := json.Unmarshal(valData, &rawMap); err != nil { return cty.NilVal, err }
		vals := make(map[string]cty.Value)
		for k, rawVal := range rawMap {
			elemTy := ty.ElementType()
			if ty.IsObjectType() { elemTy = ty.AttributeType(k) }
			val, err := buildExpectedValue(elemTy, rawVal); if err != nil { return cty.NilVal, err }; vals[k] = val
		}
		if ty.IsMapType() { return cty.MapVal(vals), nil }
		return cty.ObjectVal(vals), nil
	}
	return cty.NilVal, fmt.Errorf("cannot build expected value for type %s", ty.FriendlyName())
}

func main() {
	logger = hclog.New(&hclog.LoggerOptions{Name: "fixture-verifier", Level: hclog.Info})
	fixtureDir := flag.String("directory", "", "Directory containing fixtures and manifest.json.")
	flag.Parse()
	if *fixtureDir == "" { logger.Error("-directory flag is required"); os.Exit(1) }

	manifestPath := filepath.Join(*fixtureDir, "manifest.json")
	manifestBytes, err := os.ReadFile(manifestPath)
	if err != nil { logger.Error("Failed to read manifest.json", "error", err); os.Exit(1) }

	var manifest map[string]ManifestEntry
	if err := json.Unmarshal(manifestBytes, &manifest); err != nil { logger.Error("Failed to parse manifest.json", "error", err); os.Exit(1) }

	failures := 0
	for name, entry := range manifest {
		ty, err := parseCtyType(entry.Type)
		if err != nil { logger.Error("Failed to parse type from manifest", "case", name, "error", err); failures++; continue }

		fixturePath := filepath.Join(*fixtureDir, name+".msgpack")
		fixtureBytes, err := os.ReadFile(fixturePath)
		if err != nil { logger.Error("Failed to read fixture file", "case", name, "error", err); failures++; continue }

		deserializedVal, err := msgpack.Unmarshal(fixtureBytes, ty)
		if err != nil { logger.Error("Failed to deserialize fixture", "case", name, "error", err); failures++; continue }

		if entry.IsUnknown {
			if !deserializedVal.IsUnknown() { logger.Error("Value should be Unknown, but is not", "case", name); failures++ }
		} else if entry.IsNull {
			if !deserializedVal.IsNull() { logger.Error("Value should be Null, but is not", "case", name); failures++ }
		} else {
			expectedVal, err := buildExpectedValue(ty, entry.Value)
			if err != nil { logger.Error("Failed to build expected value", "case", name, "error", err); failures++; continue }
			if !deserializedVal.Equals(expectedVal).True() {
				logger.Error("Deserialized value does not equal expected value", "case", name, "got", deserializedVal.GoString(), "want", expectedVal.GoString()); failures++
			}
		}
		if failures == 0 { logger.Info("Verified fixture", "case", name) }
	}

	if failures > 0 {
		logger.Error(fmt.Sprintf("%d verification(s) failed.", failures))
		os.Exit(1)
	}
	logger.Info("✅ All fixtures verified successfully.")
}
