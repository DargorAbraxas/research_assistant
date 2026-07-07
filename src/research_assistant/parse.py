import pymupdf4llm
import json

md = pymupdf4llm.to_json("data/faithfulness_to_refusal:_a_causal_audit_of_neuron_selectors.pdf")

def save_json(dict_data, filename):
    with open(filename, "w") as f:
        json_str = json.dumps(dict_data, indent=4)
        f.write(json_str)


