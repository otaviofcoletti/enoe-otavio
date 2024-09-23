# MQTT Broker Service Configuration

Este documento fornece instruções detalhadas para configurar e executar o serviço Mosquitto MQTT Broker usando os arquivos fornecidos.

## Pré-requisitos

- Um servidor Linux com `systemd` instalado.
- Acesso root ou sudo ao servidor.

## Passos para Configuração

### 1. Copiar o Arquivo de Serviço

Copie o arquivo `mosquitto_custom.service` para o diretório de serviços do `systemd`.

```sh
sudo cp mosquitto_custom.service /etc/systemd/system/
```

### 2. Ativar o Serviço

Ative o serviço para que ele inicie automaticamente ao ligar o servidor.

```sh
sudo systemctl enable mosquitto_custom.service
```

### 3. Recarregar os Arquivos do `systemd`

Recarregue os arquivos de configuração do `systemd` para aplicar as mudanças.

```sh
sudo systemctl daemon-reload
```

### 4. Iniciar o Serviço

Inicie o serviço Mosquitto.

```sh
sudo systemctl start mosquitto_custom.service
```

### 5. Verificar o Status do Serviço

Verifique se o serviço está rodando corretamente.

```sh
sudo systemctl status mosquitto_custom.service
```

### 6. Reiniciar o Serviço

Se necessário, você pode reiniciar o serviço.

```sh
sudo systemctl restart mosquitto_custom.service
```

### 7. Parar o Serviço

Para parar o serviço, use o comando:

```sh
sudo systemctl stop mosquitto_custom.service
```

## Arquivos de Configuração

### `config.json`

Este arquivo contém as configurações do broker MQTT e as credenciais de acesso.

```json
{
    "MQTT": {
      "broker_endpoint": "100.66.3.93",
      "port": 1883
    },
    "CREDENTIALS": {
      "username": "raspberry",
      "password": "rasberry.publisher"
    }
}
```

### `mosquitto_custom.service`

Arquivo de serviço `systemd` para o Mosquitto.  Configure os caminhos e o usuário se necessário

```ini
[Unit]
Description=Mosquitto MQTT Broker Service
After=network.target

[Service]
WorkingDirectory=/home/intermidia/enoe-otavio/MQTT_Broker 
ExecStart=/usr/sbin/mosquitto -c /home/intermidia/enoe-otavio/MQTT_Broker/config-server.conf -v 
Restart=always
RestartSec=10
User=intermidia
KillMode=process
TimeoutStartSec=infinity

[Install]
WantedBy=multi-user.target
```

### `config-server.conf`

Configuração do servidor Mosquitto.

```properties
listener 1883 0.0.0.0

per_listener_settings true

password_file /home/intermidia/enoe-otavio/MQTT_Broker/users.txt

allow_anonymous false

require_certificate false
```
## Configuração de Usuários no Mosquitto

Para configurar usuários no Mosquitto, siga os passos abaixo:

### 1. Criar o Arquivo de Senhas

Crie um arquivo de senhas que será usado pelo Mosquitto para autenticar os usuários. Utilize o comando `mosquitto_passwd` para adicionar usuários e senhas ao arquivo.

```sh
sudo mosquitto_passwd -c /home/intermidia/enoe-otavio/MQTT_Broker/users.txt <nome_do_usuario>
```

Você será solicitado a inserir e confirmar a senha para o usuário.

### 2. Adicionar Mais Usuários

Para adicionar mais usuários ao arquivo de senhas existente, use o comando sem a opção `-c`:

```sh
sudo mosquitto_passwd /home/intermidia/enoe-otavio/MQTT_Broker/users.txt <nome_do_usuario>
```

### 3. Configurar o Mosquitto para Usar o Arquivo de Senhas

Certifique-se de que o arquivo de configuração do Mosquitto (`config-server.conf`) está apontando para o arquivo de senhas correto. O arquivo deve conter a linha:

```properties
password_file /home/intermidia/enoe-otavio/MQTT_Broker/users.txt
```

### 4. Reiniciar o Serviço Mosquitto

Após configurar os usuários, reinicie o serviço Mosquitto para aplicar as mudanças.

```sh
sudo systemctl restart mosquitto_custom.service
```

### 5. Verificar a Autenticação

Para verificar se a autenticação está funcionando corretamente, tente conectar ao broker Mosquitto usando um cliente MQTT com as credenciais configuradas.

```sh
mosquitto_sub -h <broker_endpoint> -t <topic> -u <nome_do_usuario> -P <senha>
```

Se a conexão for bem-sucedida, a configuração de usuários está correta.

## Conclusão

Seguindo os passos acima, você deve ser capaz de configurar e executar o serviço Mosquitto MQTT Broker no seu servidor. Certifique-se de que todos os arquivos de configuração estão corretamente configurados e que o serviço está rodando conforme esperado.
