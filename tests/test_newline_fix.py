import json
import sys
import os

# Add scripts directory to sys.path to import send_to_discord
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from scripts.send_to_discord import process_payload

def test_process_payload():
    print("Testing process_payload...")
    
    # Case 1: literal \n
    input_str = "Line 1\\nLine 2"
    expected = "Line 1\nLine 2"
    result = process_payload(input_str)
    assert result == expected, f"Expected {repr(expected)}, got {repr(result)}"
    print("Case 1 passed: literal \\n converted to newline.")

    # Case 2: recursive dict
    input_dict = {"a": "val1\\nval2", "b": [{"c": "val3\\nval4"}]}
    expected_dict = {"a": "val1\nval2", "b": [{"c": "val3\nval4"}]}
    result_dict = process_payload(input_dict)
    assert result_dict == expected_dict, f"Expected {expected_dict}, got {result_dict}"
    print("Case 2 passed: recursive processing works.")

def test_json_parsing_logic():
    print("Testing JSON parsing logic with strict=False...")
    
    def parse_like_script(payload_or_content):
        if isinstance(payload_or_content, str) and payload_or_content.strip().startswith('{'):
            try:
                return json.loads(payload_or_content, strict=False)
            except json.JSONDecodeError:
                return {"content": payload_or_content}
        return {"content": payload_or_content}

    # Case 3: JSON with real newline inside a value (allowed by strict=False)
    input_str = '{"description": "Line 1\nLine 2"}'
    result = parse_like_script(input_str)
    result = process_payload(result)
    
    assert "description" in result
    assert result["description"] == "Line 1\nLine 2"
    print("Case 3 passed: JSON with internal newline handled.")

    # Case 4: JSON with indentation (broken by previous replace logic, now fixed)
    input_str = """{
  "description": "Indented JSON"
}"""
    result = parse_like_script(input_str)
    result = process_payload(result)
    assert result["description"] == "Indented JSON"
    print("Case 4 passed: Indented JSON handled.")

if __name__ == "__main__":
    try:
        test_process_payload()
        test_json_parsing_logic()
        print("\nAll tests passed!")
    except AssertionError as e:
        print(f"\nTest failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        sys.exit(1)
