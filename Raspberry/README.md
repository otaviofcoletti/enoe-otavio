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






