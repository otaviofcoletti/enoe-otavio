# Como usar:

## Para Raspberry 3 faça os seguintes passos (Não necessário para outras versões):

Abra o arquivo /boot/config.txt usando o seguinte comando: sudo nano /boot/config.txt Role até o final do arquivo e adicione as seguintes linhas ao arquivo:
enable_uart=1
dtoverlay=pi3-disable-bt
dtoverlay=pi3-miniuart-bt
Isso desativará o bluetooth no Raspberry Pi 3 e permitirá a comunicação serial em seu lugar.Salve e feche o arquivo pressionando simultaneamente Ctrl e X para sair da tela e pressionando Y para salvá-lo.


## Para descobrir qual a interface os dados estão sendo transmitidos

sudo apt‑get install minicom

minicom -b 9600 -o -D /dev/ttyS0

minicom -b 9600 -o -D /dev/ttyAMA0

Veja qual das duas existe alguma saída, a que funcionar é a saída da sua raspberry, na 4 a ttyS0 funcionou, na 2 e 3 foi a ttyAMA0.

### Atualize essa configuração nos arquivos onde pegam os dados do sensor ultrassônico: ultrassonic_file_writer.py

## Câmera IP

Para utilizar a câmera IP você deve criar uma rede manualmente

Na raspberry pode fazer da seguinte maneira:

sudo ifconfig eth0 10.1.1.10 netmask 255.255.255.0

O ip da câmera é 10.1.1.11, com esse comando você estará configurando o seu ip para 10.1.1.10.

Se quiser testar utilize o link no VLC para visualizar o streaming da câmera :vlc rtsp://admin:admin@10.1.1.11

Verifique se o VLC está instalado, caso contrário pode utilizar o código do projeto que deverá funcionar

Para liberar a porta /dev/ttyS0:
Desabilitar o serviço serial-getty:

Você pode parar e desabilitar o serviço que está iniciando o login na porta serial. Se estiver usando systemd, execute:

bash
Copiar
sudo systemctl stop serial-getty@ttyS0.service
sudo systemctl disable serial-getty@ttyS0.service
Isso impede que o serviço seja iniciado automaticamente no boot.

Verificar o arquivo de boot (caso seja um Raspberry Pi):

Em sistemas como o Raspberry Pi, a porta serial pode estar configurada para fornecer um console de login. Verifique o arquivo /boot/cmdline.txt e remova referências a console=ttyS0,115200 ou similares, se você não precisar desse console.


INSTALE O OPENCV PELO SUDO APT INSTALL

## Wifi

## Serviços

### Criadores de dados (imagem e sensores)

## MQTT

## Consumo de dados

## Tailscale


## Teste de camera e sensores





