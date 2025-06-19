from pyvider.cty.codec import parse_type_string_to_ctytype, CtyTypeParseError

# Replace with the actual type string extracted in step 3
type_string_to_test = "object({cpu_utilization=number,memory_usage=number,disk_io=list(number)})"

print(f"Testing type string: {type_string_to_test}")
try:
    parsed_type = parse_type_string_to_ctytype(type_string_to_test)
    print(f"Successfully parsed: {parsed_type}")
    print(f"String representation of parsed type: {str(parsed_type)}")
except CtyTypeParseError as e:
    print(f"Parsing failed: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
