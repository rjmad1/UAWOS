import os
import json
import yaml

def test_json_validity():
    scaffolding_path = r"c:\Users\rajaj\Projects\UAWOS\governance\ai_eos_scaffolding"
    okf_schema_file = os.path.join(scaffolding_path, "okf_schema.json")
    print(f"Validating JSON Schema: {okf_schema_file}")
    with open(okf_schema_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print("OKF Schema is valid JSON.")

def test_yaml_validity():
    scaffolding_path = r"c:\Users\rajaj\Projects\UAWOS\governance\ai_eos_scaffolding"
    files = ["speckit_config.yaml", "agent_registry.yaml", "ci_validation_pipeline.yaml"]
    for file in files:
        file_path = os.path.join(scaffolding_path, file)
        print(f"Validating YAML file: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            yaml.safe_load(f)
        print(f"{file} is valid YAML.")

if __name__ == "__main__":
    test_json_validity()
    test_yaml_validity()
    print("All syntax checks passed successfully!")
