
# Примеры вызова:
```
python main.py -d OneHour   -t 500  --semi-quiet
python main.py -d ThreeHour -t 300
python main.py -d OneDay    -t 900
```

# CLI ключи:
```
-q, --semi-quiet  - dont notify when zero violators
-t, --threshold   - total traffic amount threshold to qualify as violation
-d, --detail      - stats span, can be <OneHour|ThreeHour|OneDay>
```

# Пример конфига:

config.toml:
```
[General]
Debug = false

[Telega]
botToken = "7502347503:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
manualChats = [ "-1001111111234", "-1001111811234", "7891625487" ]

[Router]
baseUrl = "https://stats.box.org"
credent = ["user", "pass"]
doAuth = true # for internet connect

```

# Запуск по таймеру в systemd:
```
cp ./systemd/trafwatch.* $home/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user restart trafwatch-hourly.timer
systemctl --user restart trafwatch-threehour.timer
systemctl --user restart trafwatch-daily.timer
# или systemctl enable --now ...
```

# Контейнеризация, cron:
```
# создать образ, копируя конфиги
docker build --network host  -t trafwatch -f Dockerfile .

# запустить контейнер
docker run --name myTrafWatcher trafwatch

# запустить контейнер с подменой конфига и crontab
docker run  -v $(pwd)/crontab:/etc/cron.d/trafwatch -v $(pwd)/app/config.toml:/app/config.toml  --name myTrafWatcher trafwatch

# стандартные команды докера
docker exec -it myTrafWatcher  cat /var/log/cron.log
docker ps
docker stop myTrafWatcher
```

