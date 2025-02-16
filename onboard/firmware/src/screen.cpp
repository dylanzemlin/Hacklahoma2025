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

const char BYTE_CONFIRMED_CHARACTER = '0';
const char BYTE_NEWLINE = '1';
const char BYTE_BACKSPACE = '2';
const char BYTE_PREDICTION = '3';
const char SCREEN_CLEAR = '4';
const char TIME_REMAINING = '5';
const char PEEPO_START = '6';
const char PEEPO_FAIL = '7';
const char PEEPO_SUCCESS = '8';

struct frame {
	char data[2];
};

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
int started = 0;
char last_time_received = '0';

std::pair<uint16_t, uint16_t> cursorPos = {0, 0};
std::queue<frame> dataQueue;
std::mutex dataMutex;

void drawing();
void receiveData(int sock);
uint8_t SetupHWSPI(void);
void shutdown(void);

void drawing() {
    myTFT.fillScreen(RDLC_BLACK);
    myTFT.setTextColor(RDLC_BLUE, RDLC_WHITE);
    myTFT.setFont(font_inconsola);

	// flip the screen vertically
	ILI9341_TFT::TFT_rotate_e rot = ILI9341_TFT::TFT_rotate_e::TFT_Degrees_180;
	myTFT.setRotation(rot);

    while (true) {
        std::this_thread::sleep_for(std::chrono::milliseconds(10));

        struct frame dataToDraw;
        {
            std::lock_guard<std::mutex> lock(dataMutex);
            if (!dataQueue.empty()) {
                dataToDraw = dataQueue.front();
                dataQueue.pop();
			} else {
				continue;
			}
		}

		if (started == 0)
		{
			// draw a black screen with white text
			myTFT.fillScreen(RDLC_BLUE);
			myTFT.setTextColor(RDLC_WHITE, RDLC_BLACK);

			if (dataToDraw.data[0] == PEEPO_START)
			{
				last_time_received = dataToDraw.data[1];
			}

			if (dataToDraw.data[0] == PEEPO_SUCCESS)
			{
				started = 1;
				myTFT.fillScreen(RDLC_BLACK);
				myTFT.setTextColor(RDLC_BLUE, RDLC_WHITE);
				myTFT.setFont(font_inconsola);
				myTFT.setCursor(0, 0);
				continue;
			}

			if (dataToDraw.data[0] == PEEPO_FAIL)
			{
				started = 0;
				last_time_received = '0';
			}

			// draw the time in the middle of the screen
			myTFT.setCursor(100, 150);
			myTFT.print(last_time_received);
			myTFT.setCursor(0, 0);
			continue;
		}

		if (dataToDraw.data[0] == BYTE_CONFIRMED_CHARACTER) {
			myTFT.setTextColor(RDLC_BLACK, RDLC_WHITE);
			myTFT.print(dataToDraw.data[1]);
			cursorPos.first += 25;
			if (cursorPos.first >= 225) {
				cursorPos.first = 0;
				cursorPos.second += 20;
			}
			myTFT.setCursor(cursorPos.first, cursorPos.second);
			std::cout << "Confirmed character: " << dataToDraw.data[1] << std::endl;
        } 
		else if (dataToDraw.data[0] == BYTE_NEWLINE) {
			cursorPos.first = 0;
			cursorPos.second += 20;
			myTFT.setCursor(cursorPos.first, cursorPos.second);
		}
		else if (dataToDraw.data[0] == BYTE_BACKSPACE) {
			myTFT.setCursor(cursorPos.first - 25, cursorPos.second);
        } 
		else if (dataToDraw.data[0] == BYTE_PREDICTION) {
			myTFT.setTextColor(RDLC_RED);
			myTFT.print(dataToDraw.data[1]);
			myTFT.setCursor(cursorPos.first, cursorPos.second);
        } 
		else if (dataToDraw.data[0] == SCREEN_CLEAR) {
			myTFT.fillScreen(RDLC_BLACK);
			cursorPos = {0, 0};
			myTFT.setCursor(cursorPos.first, cursorPos.second);
			started = 0;
		}
		else if (dataToDraw.data[0] == TIME_REMAINING) {
			// draw the time remaining in the bottom right corner
			char time_remain = dataToDraw.data[1];

			uint16_t last_cursor_x = cursorPos.first;
			uint16_t last_cursor_y = cursorPos.second;
			myTFT.setCursor(150, 150);
			myTFT.setTextColor(RDLC_BLACK, RDLC_WHITE);
			myTFT.print(time_remain);
			cursorPos.first = last_cursor_x;
			cursorPos.second = last_cursor_y;
			myTFT.setCursor(cursorPos.first, cursorPos.second);
		}
    }
}

void receiveData(int sock) {
	char buffer[6];
	struct sockaddr_in cliaddr;
	socklen_t len = sizeof(cliaddr);
	int n;

	while (1) {
		n = recvfrom(sock, (char *)buffer, 6, MSG_WAITALL, (struct sockaddr *) &cliaddr, &len);
		if (n > 0) {
			std::lock_guard<std::mutex> lock(dataMutex);
			struct frame temp;
			temp.data[0] = buffer[0];
			temp.data[1] = buffer[1];
			dataQueue.push(temp);
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


