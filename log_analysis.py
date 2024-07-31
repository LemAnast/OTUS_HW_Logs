import os
import re
import json
from collections import defaultdict

# Шаблон для разбора строки лога
log_pattern = re.compile(
    r"(?P<ip>.*?) ([-]) ([-]) \[(?P<date>.*?)(?= ) (?P<timezone>.*?)\] \"(?P<request_method>.*?) (?P<path>.*?)(?P<request_version> HTTP/.*)?\" (?P<status>.*?) (?P<length>.*?) \"(?P<referrer>.*?)\" \"(?P<user_agent>.*?)\" (?P<duration>\d+)")


def parse_log_file(file):
    total_requests = 0
    method_counts = defaultdict(int)
    ip_counts = defaultdict(int)
    slow_requests = []

    with open(file, 'r') as f:
        for line in f:
            match = log_pattern.match(line)
            if match:
                total_requests += 1

                # Извлечение информации
                ip = match.group('ip')
                date = match.group('date')
                timezone = match.group('timezone')
                method = match.group('request_method')
                url = match.group('path')
                duration = int(match.group('duration'))

                # Увеличиваем количество запросов по методу
                if method in ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'HEAD']:
                    method_counts[method] += 1

                # Увеличиваем счетчик IP-адресов
                ip_counts[ip] += 1

                # Собираем информацию о медленных запросах
                slow_requests.append({
                    'ip': ip,
                    'date': f"[{date} {timezone}]",
                    'method': method,
                    'url': url,
                    'duration': duration
                })

    return total_requests, method_counts, ip_counts, slow_requests


def analyze_logs(file):
    requests, methods, ips, slow = parse_log_file(file)

    # Топ 3 IP адреса, с которых было сделано наибольшее количество запросов
    top_ips = sorted(ips.items(), key=lambda x: x[1], reverse=True)[:3]
    top_ips_dict = {ip: count for ip, count in top_ips}

    # Топ 3 самых долгих запросов
    top_slow_requests = sorted(slow, key=lambda x: x['duration'], reverse=True)[:3]

    return {
        'top_ips': top_ips_dict,
        'top_longest': top_slow_requests,
        'total_stat': dict(methods),
        'total_requests': requests
    }


def save_to_json(data, output_file):
    with open(output_file, 'w') as json_file:
        json.dump(data, json_file, indent=4)


def main():
    path = input("Введите путь к директории с логами или к файлу: ")

    if not (os.path.isfile(path) or os.path.isdir(path)):
        print("Указанный путь не существует.")
        return

    log_files = []
    if os.path.isfile(path):
        log_files.append(path)
    else:
        log_files = [os.path.join(path, file) for file in os.listdir(path) if file.endswith('.log')]

    # Обработка каждого лог-файла
    for log_file in log_files:
        result = analyze_logs(log_file)

        # Имя выходного файла на основе имени лог-файла
        output_file = f"{os.path.splitext(log_file)[0]}_stats.json"

        # Вывод статистики в терминал
        print(f"Статистика для файла {log_file}:\n")
        print(json.dumps(result, indent=4))

        # Сохранение в json файл
        save_to_json(result, output_file)
        print(f"Статистика сохранена в: {output_file}\n")


if __name__ == '__main__':
    main()
