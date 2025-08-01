# Описание
## Программа призвана получить с REST-морды роутера Keenetic статистику по потреблению трафика клиентами. В случае высоких показателей отправлять отчеты в телеграм-канал.

# Примеры вызова:
```
python main.py -d OneHour   -t 500  --semi-quiet
python main.py -d ThreeHour -t 300
python main.py -d OneDay    -t 900
```

# CLI ключи:
```
-q, --semi-quiet  - не рассылать оповещение если порог не превышен
-t, --threshold   - порог суммы входящего и исходящего трафика для потребителя
-d, --detail      - окно сбора статистики трафика, может быть <OneHour|ThreeHour|OneDay>
```

# Пример конфига:
```
config.toml:
------------
[General]
Debug = false

[Telega]
botToken = "7502347503:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
manualChats = [ "-1001111111234", "-1001111811234", "7891625487" ]

[Router]
baseUrl = "https://stats.box.org"
credent = ["user", "pass"]
doAuth = true # это было надо если роутер не в локальной сети
```

# Телега:
- создать бота
- создать канал, добавить бота в админы
- узнать токен бота
- узнать ид канала
- вписать в конфиг

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
docker run -d --network host --name myTrafWatcher trafwatch

# запустить контейнер с подменой конфига и crontab
docker run --network host -v $(pwd)/crontab:/etc/cron.d/trafwatch -v $(pwd)/app/config.toml:/app/config.toml  --name myTrafWatcher trafwatch

# стандартные команды докера
docker exec -it myTrafWatcher  cat /var/log/cron.log
docker ps
docker stop myTrafWatcher
```
возможно вам не потребуется ```--network host```

