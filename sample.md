
```json
{
    "name": "commands",
    "body": [
        {
            "name": "repeat-n",
            "count": 10,
            "body": [
                {
                    "name": "gpio-write",
                    "pin": 16,
                    "value": 1
                },
                {
                    "name": "wait",
                    "duration": 1
                },
                {
                    "name": "gpio-write",
                    "pin": 16,
                    "value": 0
                },
                {
                    "name": "wait-sec",
                    "duration": 1
                }
            ]
        }
    ]
}
```


```
# repeat-n
proc new

## gpio set 16 1
proc set gpio_mode[16] 1
prog set gpio_value[16] 1

## wait 1 sec
proc unop timestamp idt reg[10]
proc set reg_int[11] 1000
proc binop reg_int[10] + reg_int[11] reg_int[12]
proc block timestamp >= reg_int[12]

## gpio set 16 0
proc set gpio_mode[16] 1
prog set gpio_value[16] 0

## wait 1 sec
proc unop timestamp idt reg[10]
proc set reg_int[11] 1000
proc binop reg_int[10] + reg_int[11] reg_int[12]
proc block timestamp >= reg_int[12]

## Loop control
proc unop reg_int[8] ++ reg_int[8]
proc ifelse reg_int[8] < reg_int[9]
proc call 11
proc noop

proc push 11



# main
proc del 10
proc new

proc set reg_int[8] 0
proc set reg_int[9] 10
proc call 11

proc push 10

proc run 10

```