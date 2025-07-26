
# Possible call example:
```
python main.py -d OneHour   -t 500  --semi-quiet
python main.py -d ThreeHour -t 300
python main.py -d OneDay    -t 900
```

# CLI keys:
```
-q, --semi-quiet  - dont notify when zero violators
-t, --threshold   - total traffic amount threshold to qualify as violation
-d, --detail      - stats span, can be <OneHour|ThreeHour|OneDay>
```

# Possible config files example:

config.toml:
```
baseUrl = "http://192.168.0.1:88/rci/show/ip/hotspot/summary"
Debug = false
manualChats = [ "1001111111234", "1001111811234", "7891625487" ]
```

secrets.toml:
```
botToken = "999999999:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
routerCredent = ["rest-api-user", "rest-api-password"]
```
