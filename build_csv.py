import csv
import redis

if __name__ == "__main__":
    redis_server = redis.Redis(host='localhost', port=6379)
    with open('data.csv', 'w') as csv_file:
        csv_writer = csv.writer(csv_file)

        for key in redis_server.keys('*'):
            key = key.decode('utf-8')
            if key[:8] != 'session:':
                for hkey in redis_server.hkeys(key):
                    hkey = hkey.decode('utf-8')
                    value = redis_server.hget(key, hkey).decode('utf-8')
                    csv_writer.writerow((key, hkey, value))