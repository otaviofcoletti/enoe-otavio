import psutil
import json

class RaspberrySystemInfo:
    def __init__(self):
        pass

    def get_cpu_temperature(self):
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temperature = float(f.read().strip()) / 1000.0
            return temperature
        except IOError:
            print("Failed to read CPU temperature")
            return None
        except ValueError:
            print("Unable to parse CPU temperature")
            return None

    def get_memory_usage(self):
        memory_info = psutil.virtual_memory()
        ram_usage = memory_info.percent
        return ram_usage

    def get_storage_percentage(self):
        disk_usage = psutil.disk_usage('/')
        storage_percentage = (disk_usage.used / disk_usage.total) * 100
        return storage_percentage

    def get_cpu_usage(self):
        cpu_usage = psutil.cpu_percent(interval=1)
        return cpu_usage

    def get_system_info(self):
        # Gather all the information
        cpu_temp = self.get_cpu_temperature()
        cpu_usage = self.get_cpu_usage()
        ram_usage = self.get_memory_usage()
        storage_usage = self.get_storage_percentage()

        # Combine them into a dictionary
        system_info = {
            "cpu_temperature": cpu_temp,
            "cpu_usage": cpu_usage,
            "ram_usage": ram_usage,
            "storage_usage": storage_usage
        }
        return system_info

    def format_info_for_mqtt(self):
        # Get system info
        system_info = self.get_system_info()

        # Convert the information to JSON format for MQTT
        return json.dumps(system_info)

# Exemplo de uso
# raspberry_info = RaspberrySystemInfo()
# mqtt_payload = raspberry_info.format_info_for_mqtt()

# Aqui você poderia publicar no tópico MQTT
# mqtt_client.publish("raspberry/system/info", mqtt_payload)
