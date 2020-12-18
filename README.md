# Benchmark Decision Maker

## Installation
To install just trigger the following command in this repo:

```console
$ pip install .
```

Or if you want to install in development mode

```console
$ python setup.py develop
```
## Execution

Can be executed issuing the `decision_maker` command.

```console
$ decision_maker -h
usage: decision_maker [-h] -b BASELINE_UUID -r RESULTS_FILE -t TOLERANCY_RULES [-o {yaml,json}]

optional arguments:
  -h, --help            show this help message and exit
  -b BASELINE_UUID, --baseline-uuid BASELINE_UUID
  -r RESULTS_FILE, --results-file RESULTS_FILE
  -t TOLERANCY_RULES, --tolerancy-rules TOLERANCY_RULES
  -o {yaml,json}, --output {yaml,json}

$ decision_maker -r cfg/input_results.json  -b a7dfb872-06bc-5e10-b878-eca5eb0b3683 -t cfg/tolerancy_rules.yaml
```

## Configuration

This tool uses a tolerancy rules file to, to return different results depending on the rules described. It's a YAML file with the following that looks like:

```yaml
- json_path: "test_type/stream/protocol/*/message_size/*/num_threads/1/avg(norm_byte)"
  tolerancy: -20
- json_path: "test_type/rr/protocol/*/message_size/*/num_threads/*/90.0percentiles(norm_ltcy)"
  tolerancy: 30
```

It's basically list of dictionaries where the `json_path` key indicates the path of the results of the given results file. Wildcards are used to match several keys at a certain level. And `tolerancy` defines the tolerance percentage acepted. i.e a 10 would mean any metric 10% higher than the baseline metric will be considered an error, and -10 would mean the opposite, any metric at least 10% below the baseline value will be considered an error.


## Example

Given The following results file:

```yaml
{                                     
    "test_type": {                                                                                                     
        "stream": {                                                                                                    
            "protocol": {                                                                                              
                "tcp": {             
                    "message_size": {       
                        "64": {       
                            "num_threads": {          
                                "1": {                                                                                 
                                    "max(norm_byte)": {                                                                
                                        "281238bb-d217-57e2-a68a-64289f86b9ad": 47414272.0,
                                        "a7dfb872-06bc-5e10-b878-eca5eb0b3683": 73905152.0
                                    },                                                                                 
                                    "avg(norm_byte)": {                                                                
                                        "281238bb-d217-57e2-a68a-64289f86b9ad": 35374943.82122905,
                                        "a7dfb872-06bc-5e10-b878-eca5eb0b3683": 70476003.55555555                      
                                    },                                                                                 
                                    "50.0percentiles(norm_byte)": {                               
                                        "281238bb-d217-57e2-a68a-64289f86b9ad": 37089280.0,
                                        "a7dfb872-06bc-5e10-b878-eca5eb0b3683": 70538752.0
                                    }                                                                                  
                                }                                                                                      
                            }         
                        },                             
                        "1024": {                                                                                      
                            "num_threads": {                                                                           
                                "1": {
                                    "max(norm_byte)": {
                                        "281238bb-d217-57e2-a68a-64289f86b9ad": 439697408.0,
                                        "a7dfb872-06bc-5e10-b878-eca5eb0b3683": 619495424.0
                                    },
                                    "avg(norm_byte)": {
                                        "281238bb-d217-57e2-a68a-64289f86b9ad": 328862942.97206706,
                                        "a7dfb872-06bc-5e10-b878-eca5eb0b3683": 617195383.2888889
                                    },
                                    "50.0percentiles(norm_byte)": {
                                        "281238bb-d217-57e2-a68a-64289f86b9ad": 333037568.0,                           
                                        "a7dfb872-06bc-5e10-b878-eca5eb0b3683": 617734144.0
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
```

And the following tolerancy config:

```yaml
- json_path: "test_type/stream/protocol/*/message_size/*/num_threads/1/avg(norm_byte)"
  tolerancy: -47
```


An invocation of decision_maker will give the following output

```
$ decision_maker -r ex -b a7dfb872-06bc-5e10-b878-eca5eb0b3683 -t ex2.yaml  
test_type:
  stream:
    protocol:
      tcp:
        message_size:
          '1024':
            num_threads:
              '1':
                avg(norm_byte): {}
          '64':
            num_threads:
              '1':
                avg(norm_byte):
                  281238bb-d217-57e2-a68a-64289f86b9ad: 35374943.82122905
                  a7dfb872-06bc-5e10-b878-eca5eb0b3683: 70476003.55555555
$ echo $?
1
```

Where we can observe the metrics not meeting the tolerations from the baseline metric and RS is 0.
