#include "max11043.h"
#include "defines.h"
#include "tm_stm32f4_spi.h"
#include "tm_stm32f4_delay.h"
#include "tm_stm32f4_mco_output.h"
#include "tm_stm32f4_gpio.h"
#include "tm_stm32f4_spi_dma.h"
#include "tm_stm32f4_general.h"
#include "stdio.h"
#include "string.h"
#include "data_processor.h"
#include "tm_stm32f4_usart.h"
#include "tm_stm32f4_usart_dma.h"


/* Private variables */
static uint8_t dataWrite[3] = {0,0,0};						// Array for data output to the device
																									// dataWrite[0] - command byte
																									// dataWrite[1-2] - data to be written

static uint8_t dataRead[9] = {0,0,0,0,0,0,0,0,0}; // Array for data input from the device
																									// dataRead[0] - read data when sending command byte
																									// dataRead[1-8] - data read from the device 
volatile int16_t dataBuffer[1000];
volatile float dataBufferf[1000];
volatile float dataBufferAf[1000];
volatile float dataBufferBf[1000];
volatile float dataBufferCf[1000];
volatile float dataBufferDf[1000];
volatile uint16_t bufferCounter = 0;
volatile uint16_t bufferCounterf = 0;

volatile uint8_t TX_Buffer[9], RX_Buffer[9];
uint32_t val;

volatile int16_t chA, chB, chC, chD;
volatile float chA_V, chB_V, chC_V, chD_V;

volatile bool newSampleAcquired;

char serialMsg[200]; // String modified by process
char outputStr[200]; // Output message (which actually contains temporary copy of serialMsg for output)
uint8_t triggered;
const char process_text[] = "processed\n";

/* Private functions */
bool checkWritten( uint8_t* dataOut, uint8_t* dataIn, uint32_t count );
void init_Buffer(void);

/* Public functions */

void MAX11043_writeReg( SPI_TypeDef* SPIx, GPIO_TypeDef* GPIOx, uint16_t CS_Pin, uint8_t addr, uint8_t* dataOut, uint32_t count ){
		uint32_t i;
		
		dataWrite[0] = ( addr << 2 ) | 0x00; // Writing to address addr
		
		for(i = 1; i < count; i++){
			
			dataWrite[i] = dataOut[i-1];
			
		}
	
		TM_GPIO_SetPinLow(GPIOx, CS_Pin ); 
		
		TM_SPI_WriteMulti( SPIx, dataWrite, count);
								 
		TM_GPIO_SetPinHigh(GPIOx, CS_Pin);
	
}

void MAX11043_readReg( SPI_TypeDef* SPIx, GPIO_TypeDef* GPIOx, uint16_t CS_Pin, uint8_t addr, uint8_t* dataIn, uint32_t count ){
		uint32_t i;
	
		dataWrite[0] = ( addr << 2 ) | 0x02; // Reading from address addr
		
		TM_GPIO_SetPinLow(GPIOx, CS_Pin ); 
		
		TM_SPI_SendMulti( SPIx, dataWrite, dataRead, count);
								 
		TM_GPIO_SetPinHigh(GPIOx, CS_Pin);
	
		for(i = 1; i < count; i++){
			
			dataIn[i-1] = dataRead[i];
			
		}
	
}

bool MAX11043_init( SPI_TypeDef* SPIx, GPIO_TypeDef* GPIOx, uint16_t CS_Pin ){
	uint8_t addr;
	uint8_t registerDataWrite[2];
	uint8_t registerDataRead[2];
	uint16_t registerData16;
	uint32_t count;
	
	init_Buffer();
	
	newSampleAcquired = false;
	triggered = false;
	
	bufferCounter = 0;
	
	count = 3;
	
	// ---------------------------------------------------------

	registerData16 = (EXTCLK_CLOCK_IN | CLK_DIV_6 | PD_NORMAL_POWER | PDA_NORMAL | 
									PDB_NORMAL | PDC_NORMAL | PDD_NORMAL | PDDAC_POWER_DOWN | 
									PDOSC_NORMAL | BITS_16 | SCHANA_OFF | SCHANB_OFF | SCHANC_OFF | 
									SCHAND_OFF | DECSEL_24 );


	
	// Disassemble data into one byte segments
	registerDataWrite[0] = (registerData16 & 0xFF00) >> 8;
	registerDataWrite[1] = registerData16 & 0x00FF;
	addr = CONFIG;
	
	// Write data to configuration register
	MAX11043_writeReg( SPIx, GPIOx, CS_Pin, addr, registerDataWrite, count );
	
	Delayms(1);
	
	registerDataRead[0] = 0;
	registerDataRead[1] = 0;
	
	// Read to verify data was correctly written
	MAX11043_readReg( SPIx, GPIOx, CS_Pin, addr, registerDataRead, count );
	
	Delayms(1);

	// Check if written
	if( !checkWritten(registerDataWrite, registerDataRead, count))
		return false;
	
	// ---------------------------------------------------------

	registerData16 = ( BDAC_40_AVDD | DIFF_2X | EQ_DISABLED | MODG_GAIN_1 | 
											PDPGA_POWER_DOWN | FILT_ENABLED | PGAG_GAIN_8 | ENBIASP_ENABLED | 
											ENBIASN_ENABLED );
	
	// Disassemble data into one byte segments
	registerDataWrite[0] = (registerData16 & 0xFF00) >> 8;
	registerDataWrite[1] = registerData16 & 0x00FF;
	
	
	addr = CONFIG_A;
	
	// Write data to configuration register
	MAX11043_writeReg( SPIx, GPIOx, CS_Pin, addr, registerDataWrite, count );
	
	Delayms(1);
	
	registerDataRead[0] = 0;
	registerDataRead[1] = 0;
	
	// Read to verify data was correctly written
	MAX11043_readReg( SPIx, GPIOx, CS_Pin, addr, registerDataRead, count );
	
	Delayms(1);

	// Check if written
	if( !checkWritten(registerDataWrite, registerDataRead, count))
		return false;
	
	// ---------------------------------------------------------
	
	addr = CONFIG_B;
	
	// Write data to configuration register
	MAX11043_writeReg( SPIx, GPIOx, CS_Pin, addr, registerDataWrite, count );
	
	Delayms(1);
	
	registerDataRead[0] = 0;
	registerDataRead[1] = 0;
	
	// Read to verify data was correctly written
	MAX11043_readReg( SPIx, GPIOx, CS_Pin, addr, registerDataRead, count );
	
	Delayms(1);

	// Check if written
	if( !checkWritten(registerDataWrite, registerDataRead, count))
		return false;
	
	// ---------------------------------------------------------
	
	addr = CONFIG_C;
	
	// Write data to configuration register
	MAX11043_writeReg( SPIx, GPIOx, CS_Pin, addr, registerDataWrite, count );
	
	Delayms(1);
	
	registerDataRead[0] = 0;
	registerDataRead[1] = 0;
	
	// Read to verify data was correctly written
	MAX11043_readReg( SPIx, GPIOx, CS_Pin, addr, registerDataRead, count );
	
	Delayms(1);

	// Check if written
	if( !checkWritten(registerDataWrite, registerDataRead, count))
		return false;
	
	// ---------------------------------------------------------
	
	addr = CONFIG_D;
	
	// Write data to configuration register
	MAX11043_writeReg( SPIx, GPIOx, CS_Pin, addr, registerDataWrite, count );
	
	Delayms(1);
	
	registerDataRead[0] = 0;
	registerDataRead[1] = 0;
	
	// Read to verify data was correctly written
	MAX11043_readReg( SPIx, GPIOx, CS_Pin, addr, registerDataRead, count );
	
	Delayms(1);

	// Check if written
	if( !checkWritten(registerDataWrite, registerDataRead, count))
		return false;
	
	// ---------------------------------------------------------
	
	registerData16 = ( EXTREF_INT | EXBUFA_INT | EXBUFB_INT | EXBUFC_INT | 
											EXBUFD_INT | EXBUFDAC_INT | EXBUFDACH_INT | 
											EXBUFDACL_INT );
	
	// Disassemble data into one byte segments
	registerDataWrite[0] = (registerData16 & 0xFF00) >> 8;
	registerDataWrite[1] = registerData16 & 0x00FF;

	addr = REFERENCE;
	
	// Write data to configuration register
	MAX11043_writeReg( SPIx, GPIOx, CS_Pin, addr, registerDataWrite, count );
	
	Delayms(1);
	
	registerDataRead[0] = 0;
	registerDataRead[1] = 0;
	
	// Read to verify data was correctly written
	MAX11043_readReg( SPIx, GPIOx, CS_Pin, addr, registerDataRead, count );
	
	Delayms(1);

	// Check if written
	if( !checkWritten(registerDataWrite, registerDataRead, count))
		return false;
	
	// ---------------------------------------------------------
	
	
	// If all registers were written to successfuly then return true
	return true;
	
}


bool MAX11043_readAllChannels( SPI_TypeDef* SPIx, GPIO_TypeDef* GPIOx, uint16_t CS_Pin ){

	//TM_GPIO_SetPinLow(GPIOD, GPIO_Pin_8 );
	chA = (RX_Buffer[1] << 8) | RX_Buffer[2];
	chB = (RX_Buffer[3] << 8) | RX_Buffer[4];
	chC = (RX_Buffer[5] << 8) | RX_Buffer[6];
	chD = (RX_Buffer[7] << 8) | RX_Buffer[8];
	//TM_GPIO_SetPinHigh(GPIOD, GPIO_Pin_8 );
	newSampleAcquired = true;

	
	dataBuffer[bufferCounter] = chB;
	bufferCounter += 1;
	
	if(bufferCounter == 1000)
		bufferCounter = 0;
	
	
	DMA_ClearFlag(DMA2_Stream2, DMA_FLAG_TCIF2);
	DMA_ClearFlag(DMA2_Stream3, DMA_FLAG_TCIF3);
	
	GPIOB->BSRRH =CS_Pin;	
	
	/* Enable RX stream */
	DMA2_Stream2->CR |= DMA_SxCR_EN;
	
	/* Enable TX stream */
	DMA2_Stream3->CR |= DMA_SxCR_EN;
	
	SPI_I2S_ITConfig( SPI1, SPI_I2S_IT_TXE, ENABLE);
	
	/* Wait till SPI DMA do it's job */
	/* You can do other stuff instead */
	//while (TM_SPI_DMA_Working(SPI1));
	
	//TM_GPIO_SetPinHigh(GPIOx, CS_Pin ); 
	
	return true;
	
}

/* Private functions */

bool checkWritten( uint8_t* dataOut, uint8_t* dataIn, uint32_t count ){
uint32_t i;
	
	for( i = 0 ; i < count-1 ; i++ )
	{
			if( dataOut[i] != dataIn[i] )
				return false;
	}
	
	return true;
	
}

bool MAX11043_readChannelA( SPI_TypeDef* SPIx, GPIO_TypeDef* GPIOx, uint16_t CS_Pin ){

	uint8_t addr;
	uint8_t registerDataRead[8];
	uint32_t count;
	
	count = 3; 	// equals number of transfer you would like to have + command byte
							// 	value is in bytes
	
	// ---------------------------------------------------------
	
	addr = ADCB; // Want to read channelA


	// Read to verify data was correctly written
	MAX11043_readReg( SPIx, GPIOx, CS_Pin, addr, registerDataRead, count );

	//dataBuffer[bufferCounter] = ((registerDataRead[0] << 8 ) | registerDataRead[1]) + 0x8000;
	dataBuffer[bufferCounter] = ((registerDataRead[0] << 8 ) | registerDataRead[1]);
	bufferCounter += 1;
	
	if(bufferCounter == 1000)
		bufferCounter = 0;
	
	return true;
	
}

uint32_t get_TX_buffer_addr(void){
	return (uint32_t) &TX_Buffer;
}

uint32_t get_RX_buffer_addr(void){
	return (uint32_t) &RX_Buffer;
}

void init_Buffer(void)
{
	uint8_t addr;
	
	memset(TX_Buffer, 0x00, sizeof(TX_Buffer));
	
	bufferCounter = 0;
	
	addr = ADCABCD; // Want to read all four channels
	//addr = ADCAB; // Want to read all four channels
	
	TX_Buffer[0] = ( addr << 2 ) | 0x02; // Reading from address addr
	
	RX_Buffer[0] = 0;
	RX_Buffer[1] = 1;
	RX_Buffer[2] = 2;
	RX_Buffer[3] = 3;
	RX_Buffer[4] = 4;
	RX_Buffer[5] = 5;
	RX_Buffer[6] = 6;
	RX_Buffer[7] = 7;
	RX_Buffer[8] = 8;
	
}

void process_ADC_Data(void)
{
	if(newSampleAcquired){
		
	TM_GPIO_SetPinLow(GPIOD, GPIO_Pin_9 );
	
	
	chA_V = chA * VOLTS_PER_TICK;
	chB_V = chB * VOLTS_PER_TICK;
	chC_V = chC * VOLTS_PER_TICK;
	chD_V = chD * VOLTS_PER_TICK;
	
	/*
	chA_V = (float) chA / TICKS_PER_VOLT;
	chB_V = (float) chB / TICKS_PER_VOLT;
	chC_V = (float) chC / TICKS_PER_VOLT;
	chD_V = (float) chD / TICKS_PER_VOLT;
	*/
	dataBufferAf[bufferCounterf] = chA_V;

	dataBufferBf[bufferCounterf] = chB_V;

	dataBufferCf[bufferCounterf] = chC_V;

	dataBufferDf[bufferCounterf] = chD_V;
	bufferCounterf += 1;
	
	if(bufferCounterf == 1000)
		bufferCounterf = 0;
	
	
	process(chA_V, chB_V, chC_V, chD_V, serialMsg, &triggered);
	//TM_USART_Puts(USART3, dir_str);
	
	//TM_USART_Puts(USART3, "processed");
	if(triggered){
		strcpy (outputStr,serialMsg);
		TM_USART_DMA_Send(USART3, (uint8_t *)outputStr, strlen(outputStr));
		triggered = false;
	}
	TM_GPIO_SetPinHigh(GPIOD, GPIO_Pin_9 );
	
	newSampleAcquired = false;
	}
}
