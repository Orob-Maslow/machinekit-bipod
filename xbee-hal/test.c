
#include <stdio.h>
#include <stdlib.h>
#include <termios.h>
#include <fcntl.h>
#include <string.h>
#include <stdint.h>

int fd;

struct {
    uint8_t pos;
    uint8_t cksum;
} tx;

struct {
    uint16_t batt;
    uint8_t cksum;
} rx;

#define RX_SIZE 3 //computed as 4 but on the atmel it's 3

void setup()
{
    if ((fd = open("/dev/ttyO1", O_RDWR | O_NONBLOCK))<0)
    {
        printf("UART: Failed to open the file.\n");
        return;
    }

    //
    struct termios options; // the termios structure is vital
    tcgetattr(fd, &options); // sets the parameters associated with file

    // Set up the communications options:
    // 9600 baud, 8-bit, enable receiver, no modem control lines
    options.c_cflag = B57600 | CS8 | CREAD | CLOCAL;
//    options.c_iflag = IGNPAR | ICRNL; // ignore partity errors, CR -> newline
    tcflush(fd, TCIFLUSH); // discard file information not transmitted
    tcsetattr(fd, TCSANOW, &options); // changes occur immmediately
    printf("opened port ok");
}

char CRC8(char *data, char len) 
{
    char crc = 0x00;
    while (len--)
    {
        char extract = *data++;
        char tempI;
        for (tempI = 8; tempI; tempI--) 
        {
            char sum = (crc ^ extract) & 0x01;
            crc >>= 1;
            if(sum) 
            {
                crc ^= 0x8C;
            }
            extract >>= 1;
        }
    }
    return crc;
}

void main(void)
{
    setup();
    int i = 0;
    for(i = 0; i< 100; i+=10)
    {
        printf("pos %d\n", i);
        tx.pos = i; //in;
        char buf[sizeof(tx)];
        memcpy(&buf, &tx, sizeof(tx));
        tx.cksum = CRC8(buf,sizeof(tx)-1);
        memcpy(&buf, &tx, sizeof(tx));

        printf("writing...\n");
        write (fd, buf, sizeof(tx));
        printf("done\n");

        usleep (35 * 1000);             // sleep enough to transmit the 7 plus

        char rx_buf[RX_SIZE];
        printf("reading...\n");
        int n = read(fd, rx_buf, RX_SIZE);
        printf("done\n");

        //copy buffer to structure
        memcpy(&rx, &rx_buf, RX_SIZE);
        printf("read %d : %x %x %x\n", n, rx_buf[0], rx_buf[1], rx_buf[2]);
        if(rx.cksum != CRC8(rx_buf,RX_SIZE-1))
            printf("bad cksum\n");
        else
            printf("batt %d\n", rx.batt);
    }
}
