#!/usr/bin/env python3

import json
import yaml
from argparse import ArgumentParser


class Compare():

    def __init__(self, baseline_uuid, json_data):
        self.json_data = json_data
        self.json_path = []
        self.baseline_uuid = baseline_uuid
        self.tolerancy = 0
        self.compare_dict = {}
        self.rc = 0

    def _compare(self, input_dict, compare_dict):
        if self.baseline_uuid not in input_dict:
            print(f"Missing baseline UUID in input dict: {input_dict}")
            return
        # baseline value is the current value plus the tolerancy
        base_val = input_dict[self.baseline_uuid] + input_dict[self.baseline_uuid] * self.tolerancy / 100
        for u, v in input_dict.items():
            if self.tolerancy >= 0 and v > base_val:
                compare_dict[self.baseline_uuid] = input_dict[self.baseline_uuid]
                compare_dict[u] = v
                self.rc = 1
            elif self.tolerancy < 0 and v < base_val:
                compare_dict[self.baseline_uuid] = input_dict[self.baseline_uuid]
                compare_dict[u] = v
                self.rc = 1

# TODO: Check missing key errors
    def compare(self, json_path, tolerancy):
        # Split json path
        self.json_path = json_path.split("/")
        self.tolerancy = tolerancy
        self.compare_dict = {}

        # Data contains the dictionary
        # json_path contains the current json_path position
        # parent contains the output dictionary
        def recurse(data, json_path, parent):
            # If we haven't reached the first level
            if len(json_path) > 1:
                # In case of using a wildcard path iterate over each key and recurse using those
                if json_path[0] == "*":
                    for k in data:
                        parent[k] = {}
                        recurse(data[k], json_path[1::], parent[k])
                else:
                    if json_path[0] not in data:
                        print(f"Key {json_path[0]} not found in the keys from the current dict level: {list(data.keys())}")
                        return
                    parent[json_path[0]] = {}
                    recurse(data[json_path[0]], json_path[1::], parent[json_path[0]])
            # Last level before tolerancy
            else:
                # Add metric names to the dict and call compare with the metric name
                parent[json_path[0]] = {}
                self._compare(data[json_path[0]], parent[json_path[0]])

        recurse(self.json_data, self.json_path, self.compare_dict)
        return self.rc


if __name__ == "__main__":
    rc = 0
    parser = ArgumentParser()
    parser.add_argument("-b", "--baseline-uuid", required=True)
    parser.add_argument("-r", "--results-file", required=True)
    parser.add_argument("-j", "--json-paths-cfg", required=True)
    args = parser.parse_args()
    with open(args.results_file) as f:
        results_data = json.load(f)
    with open(args.json_paths_cfg) as f:
        json_paths = yaml.load(f, Loader=yaml.FullLoader)
    c = Compare(args.baseline_uuid, results_data)
    for json_path in json_paths:
        r = c.compare(json_path[0], json_path[1])
        if r:
            print(yaml.dump(c.compare_dict, indent=1))
            rc = r
    exit(rc)
