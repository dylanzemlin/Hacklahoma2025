#include <ctime>
#include <thread>
#include <iostream>
#include <bits/stdc++.h> 
#include <stdlib.h> 
#include <unistd.h> 
#include <string.h> 
#include <sys/types.h> 
#include <sys/socket.h> 
#include <arpa/inet.h> 
#include <netinet/in.h> 
#include "ILI9341_TFT_LCD_RDL.hpp"
#include "XPT2046_TS_TFT_LCD_RDL.hpp"

ILI9341_TFT myTFT;
int8_t RST_TFT = 27;
int8_t DC_TFT = 22;
int GPIO_CHIP_DEVICE = 0;

uint16_t TFT_WIDTH = 240;
uint16_t TFT_HEIGHT = 320;

int HWSPI_DEVICE = 0;
int HWSPI_CHANNEL = 0;
int HWSPI_SPEED = 8000000;
int HWSPI_FLAGS = 0;

std::pair<uint16_t, uint16_t> cursorPos = {0, 0};
std::queue<char> dataQueue;
std::mutex dataMutex;

void drawing();
void receiveData(int sock);
uint8_t SetupHWSPI(void);
void shutdown(void);

void drawing() {
    myTFT.fillScreen(RDLC_WHITE);
    myTFT.setTextColor(RDLC_BLACK, RDLC_WHITE);
    myTFT.setFont(font_inconsola);

    while (true) {
        std::this_thread::sleep_for(std::chrono::milliseconds(10));

        char dataToDraw;
        {
            std::lock_guard<std::mutex> lock(dataMutex);
            if (!dataQueue.empty()) {
                dataToDraw = dataQueue.front();
                dataQueue.pop();
			} else {
				continue;
			}
		}

		if (isalpha(dataToDraw)) {
			myTFT.print(dataToDraw);
			cursorPos.first += 25;
			if (cursorPos.first >= 225) {
				cursorPos.first = 0;
				cursorPos.second += 20;
			}
        } 
		else if (dataToDraw == ' ') {
			myTFT.print("\n");
		}
		else if (dataToDraw == '\n') {
            myTFT.print("\n");
            //myTFT.setCursor(cursorPos.first, cursorPos.second);
        } 
		else if (dataToDraw == '\b') {
            myTFT.setCursor(cursorPos.first - 1, cursorPos.second);
            myTFT.print(" ");
            myTFT.setCursor(cursorPos.first - 1, cursorPos.second);
        } 
		else if (dataToDraw == 'p') {
            myTFT.setTextColor(RDLC_GREY, RDLC_WHITE);
            myTFT.print(dataToDraw);
            myTFT.setTextColor(RDLC_BLACK, RDLC_WHITE);
        } 
		else {
            myTFT.setCursor(cursorPos.first, cursorPos.second);
        }
    }
}

void receiveData(int sock) {
	char buffer[1];
	struct sockaddr_in cliaddr;
	socklen_t len = sizeof(cliaddr);
	int n;

	while (1) {
		n = recvfrom(sock, (char *)buffer, 1, MSG_WAITALL, (struct sockaddr *) &cliaddr, &len);
		if (n > 0) {
			std::cout << "Received: " << buffer[0] << std::endl;
			buffer[n] = '\0';
			std::lock_guard<std::mutex> lock(dataMutex);
			dataQueue.push(buffer[0]);
		}
	}
}

uint8_t SetupHWSPI(void) {

	myTFT.SetupGPIO(RST_TFT, DC_TFT);
	myTFT.InitScreenSize(TFT_WIDTH, TFT_HEIGHT);
	if (myTFT.InitSPI(HWSPI_DEVICE, HWSPI_CHANNEL, HWSPI_SPEED, HWSPI_FLAGS, GPIO_CHIP_DEVICE) != rpiDisplay_Success) {
	
		return 3;
	}
	delayMilliSecRDL(100);
	return 0;

}

void shutdown(void) {
	myTFT.fillScreen(RDLC_BLACK);
	myTFT.PowerDown();
}


int main() {

	std::cout << "Starting Screen" << std::endl;
	if (SetupHWSPI() != 0) return -1;

	int sock;
	char buffer[1];
	struct sockaddr_in servaddr, cliaddr;

	if ((sock=socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
		perror("Socket creation failed.");
		exit(EXIT_FAILURE);
	}
	memset(&servaddr, 0, sizeof(servaddr));
	memset(&cliaddr, 0, sizeof(cliaddr));

	servaddr.sin_family = AF_INET;
	servaddr.sin_addr.s_addr = INADDR_ANY;
	servaddr.sin_port = htons(8080); 

	if (bind(sock, (const struct sockaddr *)&servaddr, sizeof(servaddr)) < 0) {
		perror("Bind failed.");
		exit(EXIT_FAILURE);
	}

	socklen_t len;
	int n;
	len = sizeof(cliaddr);

	myTFT.fillScreen(RDLC_WHITE);
	myTFT.setTextColor(RDLC_BLACK, RDLC_WHITE);
	myTFT.setFont(font_inconsola);

	std::thread udpReceiver(receiveData, sock);
	std::thread drawScreen(drawing);
	drawScreen.join();
	udpReceiver.join();

	shutdown();
	return 0;

}


