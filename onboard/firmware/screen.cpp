#include <ctime>
#include <iostream>
#include "ILI9341_TFT_LCD_RDL.hpp"

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

uint8_t SetupHWSPI(void);
void end(void);

uint8_t SetupHWSPI(void) {

	myTFT.SetupGPIO(RST_TFT, DC_TFT);
	myTFT.InitScreenSize(TFT_WIDTH, TFT_HEIGHT);
	if (myTFT.InitSPI(HWSPI_DEVICE, HWSPI_CHANNEL, HWSPI_SPEED, HWSPI_FLAGS, GPIO_CHIP_DEVICE) != rpiDisplay_Success) {
	
		return 3;
	}
	delayMilliSecRDL(100);
	return 0;
}


int main() {
	
}


