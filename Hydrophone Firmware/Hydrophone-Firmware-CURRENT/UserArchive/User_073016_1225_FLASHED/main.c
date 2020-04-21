/**
 *  Keil project for Hydrophones
 *
 *  Before you start, select your target, on the right of the "Load" button
 *
 *  @author     Torkom Pailevanian
 *  @website    http://stm32f4-discovery.com
 *  @ide        Keil uVision 5
 *  @stdperiph  STM32F4xx Standard peripheral drivers version 1.4.0 or greater required
 */
/* Include core modules */
#include "stm32f4xx.h"
/* Include my libraries here */
#include "defines.h"
#include "tm_stm32f4_spi.h"
#include "tm_stm32f4_delay.h"
#include "tm_stm32f4_mco_output.h"
#include "max11043.h"
#include "AD9850.h"
#include "tm_stm32f4_spi_dma.h"
#include "tm_stm32f4_general.h"
#include "stdio.h"
#include "string.h"
#include "stm32f4xx_dma.h"
#include "data_processor.h"
#include "tm_stm32f4_usart.h"
#include "tm_stm32f4_usart_dma.h"
#include "data_processor.h"
 
 
#define CS_Pin GPIO_Pin_0
#define EOC GPIO_Pin_0
#define CONVRUN_Pin GPIO_Pin_1
 
#define pingerFrequency 30
#define initThreshold (0.01f)

//#pragma import(__use_no_semihosting_swi)
 
// Private function constructors
void init_SPI1(void);
void init_SPI1_DMA(void);
void init_USART3(void);
void init_USART3_Interrupt(void);
void init_messageBuffer(void);
 
char output_str[100];

bool messageReceived, messageStarted;
char messageBuffer[100] = {0};
int messageBuffer_index;

 
 
void InitConv_IRQ(){
     
    NVIC_InitTypeDef NVIC_InitStructure;
    EXTI_InitTypeDef EXTI_InitStructure;
     
        /* Connect EXTI Line0 to PA0 pin (i.e. EXTI0CR[0])*/
    SYSCFG_EXTILineConfig(EXTI_PortSourceGPIOA, EXTI_PinSource0);
    // SYSCFG->EXTICR[0] &= SYSCFG_EXTICR1_EXTI0_PA;     // Same as above, but with direct register access
     
    /* Configure EXTI Line0 */
    EXTI_InitStructure.EXTI_Line = EXTI_Line0;              // PA0 is connected to EXTI0
    EXTI_InitStructure.EXTI_Mode = EXTI_Mode_Interrupt;     // Interrupt mode
     
        //EXTI_InitStructure.EXTI_Trigger = EXTI_Trigger_Falling;   // Trigger on Falling edge (When EOC goes Low)
        EXTI_InitStructure.EXTI_Trigger = EXTI_Trigger_Rising_Falling;  // Trigger on Rising and Falling edge 
         
        EXTI_InitStructure.EXTI_LineCmd = ENABLE;               // Enable the interrupt
    EXTI_Init(&EXTI_InitStructure);                         // Initialize EXTI
     
    /* Enable and set priorities for the EXTI0 in NVIC */
    NVIC_InitStructure.NVIC_IRQChannel = EXTI0_IRQn;                // Function name for EXTI_Line0 interrupt handler
    NVIC_InitStructure.NVIC_IRQChannelPreemptionPriority = 0x00;    // Set priority
    NVIC_InitStructure.NVIC_IRQChannelSubPriority = 0x00;           // Set sub priority
    NVIC_InitStructure.NVIC_IRQChannelCmd = ENABLE;                 // Enable the interrupt
    NVIC_Init(&NVIC_InitStructure);                                 // Add to NVIC
     
}
 
void EXTI0_IRQHandler(void) {
 
    /* Make sure that interrupt flag is set */
    if (EXTI_GetITStatus(EXTI_Line0) != RESET) {
        /* Do your stuff when PD0 is changed */
                if(GPIO_ReadInputDataBit(GPIOA, EOC)){
                    // EOC Rising edge so raise chip select
                    TM_GPIO_SetPinHigh(GPIOB, CS_Pin );
                }else if(!GPIO_ReadInputDataBit(GPIOA, EOC)){
                    // EOC falling edge so read new ADC data
                    MAX11043_readAllChannels(SPI1, GPIOB, CS_Pin);
                }
        /* Clear interrupt flag */
        EXTI_ClearITPendingBit(EXTI_Line0);
    }
}

void USART3_IRQHandler(void){
     
    // check if the USART1 receive interrupt flag was set
    if (USART_GetITStatus(USART3, USART_IT_RXNE)){
         
      char ch = USART3->DR; // the character from the USART1 data register is saved in c
      
			if (ch == '$'){
				messageBuffer_index = 0;
				messageStarted = true;
			}
			
			else if (ch == '#') {
				if (messageStarted) {
					messageStarted = false;
					messageReceived = true; 
				}
			}
			
			else {
				messageBuffer[messageBuffer_index] = ch;
				messageBuffer_index++;
			}
    }
}



void processMessage(void)
{
    if(messageBuffer[0] == '0'){
        int frequency = (messageBuffer[1]-'0')*10 + (messageBuffer[2]-'0');
				if (frequency < 20 || frequency > 40) {
					sprintf(output_str, "Invalid frequency setting of %d kHz, frequency must be between 20 kHz and 40 kHz\n\r", frequency);
					TM_USART_DMA_Send(USART3, (uint8_t *)output_str, strlen(output_str));
				}
				else {
					sprintf(output_str, "Changing pinger frequency to %d kHz\n\r", frequency);
					TM_USART_DMA_Send(USART3, (uint8_t *)output_str, strlen(output_str));
          initializeOrChangeFrequency(frequency);
				}
				
		} 
    else if(messageBuffer[0] == '1'){
        float threshold = (messageBuffer[1] - '0') + (messageBuffer[2] - '0')*0.1f + (messageBuffer[3] - '0')*0.01f + (messageBuffer[4] - '0')*0.001f;
				if (threshold < 0 || threshold > 1)
				{
					sprintf(output_str, "Invalid trigger threshold of %f V, threshold must be between 0 V and 1 V\n\r", threshold);
					TM_USART_DMA_Send(USART3, (uint8_t *)output_str, strlen(output_str));
				}
				else
				{
					changeThreshold(threshold);
					sprintf(output_str, "Changing threshold to %f V\n\r", threshold);
					TM_USART_DMA_Send(USART3, (uint8_t *)output_str, strlen(output_str));
				}
    }
		messageReceived = false;
}


int main(void) {
     
    /* Initialize system */
    SystemInit();
     
    /* Initialize delay */
    TM_DELAY_Init();
     
    /* Initialize MCO2 output, pin PC9 */
    TM_MCOOUTPUT_InitMCO2();
     
    /* Set MCO2 output = SYSCLK / 4 */
    //TM_MCOOUTPUT_SetOutput2(TM_MCOOUTPUT2_Source_SYSCLK, TM_MCOOUTPUT_Prescaler_5);
    TM_MCOOUTPUT_SetOutput2(TM_MCOOUTPUT2_Source_HSE, TM_MCOOUTPUT_Prescaler_1);
     
    /* Initialize SPI */
    /* SCK = PA5, MOSI = PA7, MISO = PA6, CS = PB0 */
    init_SPI1();
    init_SPI1_DMA();
     
    // Initialize the EOC
    TM_GPIO_Init(GPIOA, EOC, TM_GPIO_Mode_IN, TM_GPIO_OType_PP, TM_GPIO_PuPd_NOPULL, TM_GPIO_Speed_High);
     
    TM_GPIO_Init(GPIOB, CONVRUN_Pin, TM_GPIO_Mode_OUT, TM_GPIO_OType_PP, TM_GPIO_PuPd_DOWN, TM_GPIO_Speed_High);
     
    TM_USART_Init(USART3, TM_USART_PinsPack_3, 115200);
     
    // Init TX DMA for USART3 
		TM_USART_DMA_Init(USART3);
     
		sprintf(output_str, "USART3 has been initialized\n\r");
		
		TM_USART_DMA_Send(USART3, (uint8_t *) output_str, strlen(output_str));
		
		Delayms(5);
     
    sprintf(output_str, "Looking for %d kHz\n\r", pingerFrequency);
		
		TM_USART_DMA_Send(USART3, (uint8_t *) output_str, strlen(output_str));
		Delayms(5);
     
    sprintf(output_str, "Triggering on: %f V\n\r", initThreshold);
     
    TM_USART_DMA_Send(USART3, (uint8_t *) output_str, strlen(output_str));

    // Uses the USART RX pin as a GPIO for debugging purposes (should be commented out during regular operation)
		//TM_GPIO_Init(GPIOD, GPIO_Pin_9, TM_GPIO_Mode_OUT, TM_GPIO_OType_PP, TM_GPIO_PuPd_NOPULL, TM_GPIO_Speed_High);
 
    TM_GPIO_SetPinHigh(GPIOB, CS_Pin );
     
		// Disable ADC conversion before configuring ADC
    TM_GPIO_SetPinLow(GPIOB, CONVRUN_Pin );
     
		// Initalizes ADC 
    MAX11043_init(SPI1, GPIOB, CS_Pin );
     
		// Renable ADC conversion after configuring ADC 
    TM_GPIO_SetPinHigh(GPIOB, CONVRUN_Pin );
		
		// Initialize message buffer with 0s
		init_messageBuffer();
		
    // Initialize the USART3 Receive interrupt
    init_USART3_Interrupt();
     
		// Set initial pinger frequency and thresholds 
    initializeOrChangeFrequency(pingerFrequency);
		changeThreshold(initThreshold);
     
		// Initialize ADC interrupt 
    InitConv_IRQ();

    while(1)
    {	
        if(messageReceived)	// if received a complete message
        {
						// FOR DEBUGGING
            //TM_USART_DMA_Send(USART3, (uint8_t *)messageBuffer, strlen(messageBuffer));  
						processMessage();
        }
        process_ADC_Data();
    }
 
}



void init_SPI1(void){
     
    GPIO_InitTypeDef GPIO_InitStruct;
    SPI_InitTypeDef SPI_InitStruct;
     
    // enable clock for used IO pins
    RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOA, ENABLE);
     
    /* configure pins used by SPI1
     * PA5 = SCK
     * PA6 = MISO
     * PA7 = MOSI
     */
    GPIO_InitStruct.GPIO_Pin = GPIO_Pin_7 | GPIO_Pin_6 | GPIO_Pin_5;
    GPIO_InitStruct.GPIO_Mode = GPIO_Mode_AF;
    GPIO_InitStruct.GPIO_OType = GPIO_OType_PP;
    GPIO_InitStruct.GPIO_Speed = GPIO_Speed_100MHz;
    GPIO_InitStruct.GPIO_PuPd = GPIO_PuPd_NOPULL;
    GPIO_Init(GPIOA, &GPIO_InitStruct);
     
    // connect SPI1 pins to SPI alternate function
    GPIO_PinAFConfig(GPIOA, GPIO_PinSource5, GPIO_AF_SPI1);
    GPIO_PinAFConfig(GPIOA, GPIO_PinSource6, GPIO_AF_SPI1);
    GPIO_PinAFConfig(GPIOA, GPIO_PinSource7, GPIO_AF_SPI1);
     
     
    // enable clock for used IO pins
    RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOB, ENABLE);
     
    // Configure the chip select pin
    //   in this case we will use PB0 
    GPIO_InitStruct.GPIO_Pin = CS_Pin;
    GPIO_InitStruct.GPIO_Mode = GPIO_Mode_OUT;
    GPIO_InitStruct.GPIO_OType = GPIO_OType_PP;
    GPIO_InitStruct.GPIO_Speed = GPIO_Speed_100MHz;
    GPIO_InitStruct.GPIO_PuPd = GPIO_PuPd_UP;
    GPIO_Init(GPIOB, &GPIO_InitStruct);
     
    GPIOB->BSRRL |= CS_Pin; // set PB1 high
     
     
    // enable peripheral clock
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_SPI1, ENABLE);
     
    /* configure SPI1 in Mode 0 
     * CPOL = 0 --> clock is low when idle
     * CPHA = 0 --> data is sampled at the first edge
     */
      
    SPI_StructInit(&SPI_InitStruct);
    SPI_InitStruct.SPI_Direction = SPI_Direction_2Lines_FullDuplex; // set to full duplex mode, seperate MOSI and MISO lines
    SPI_InitStruct.SPI_Mode = SPI_Mode_Master;     // transmit in master mode, NSS pin has to be always high
    SPI_InitStruct.SPI_DataSize = SPI_DataSize_8b; // one packet of data is 8 bits wide
    SPI_InitStruct.SPI_CPOL = SPI_CPOL_Low;        // clock is low when idle
    SPI_InitStruct.SPI_CPHA = SPI_CPHA_1Edge;      // data sampled at first edge
    SPI_InitStruct.SPI_NSS = SPI_NSS_Soft | SPI_NSSInternalSoft_Set; // set the NSS management to internal and pull internal NSS high
    SPI_InitStruct.SPI_BaudRatePrescaler = SPI_BaudRatePrescaler_2; // SPI frequency is APB2 frequency / 4
    SPI_InitStruct.SPI_FirstBit = SPI_FirstBit_MSB;// data is transmitted MSB first
    SPI_Init(SPI1, &SPI_InitStruct); 
     
    /* Disable first */
    SPI1->CR1 &= ~SPI_CR1_SPE;
     
    /* Init SPI */
    SPI_Init(SPI1, &SPI_InitStruct);
     
    /* Enable SPI */
    SPI1->CR1 |= SPI_CR1_SPE;
     
    // Enable the SPI2 RX & TX DMA requests
  //SPI_I2S_DMACmd(SPI1, SPI_I2S_DMAReq_Rx | SPI_I2S_DMAReq_Tx, ENABLE);
     
    //while(SPI_I2S_GetFlagStatus(SPI1, SPI_I2S_FLAG_TXE) == RESET);
}
 
void init_SPI1_DMA(void)
{
    DMA_InitTypeDef DMA_InitStructure;
     
    RCC->AHB1ENR |= RCC_AHB1ENR_DMA2EN;
    //DMA_Cmd(DMA2_Stream3, DISABLE);
    //DMA_Cmd(DMA2_Stream2, DISABLE);
         
    /* Deinitialize DMA Streams */
    //DMA_DeInit(DMA2_Stream5); //SPI1_TX_DMA_STREAM
    //DMA_DeInit(DMA2_Stream0); //SPI1_RX_DMA_STREAM
     
    DMA_StructInit(&DMA_InitStructure);
    DMA_InitStructure.DMA_BufferSize = 9;
    DMA_InitStructure.DMA_FIFOMode = DMA_FIFOMode_Disable ;
    DMA_InitStructure.DMA_FIFOThreshold = DMA_FIFOThreshold_1QuarterFull ;
    DMA_InitStructure.DMA_MemoryBurst = DMA_MemoryBurst_Single ;
    DMA_InitStructure.DMA_MemoryDataSize = DMA_MemoryDataSize_Byte;
    DMA_InitStructure.DMA_MemoryInc = DMA_MemoryInc_Enable;
    DMA_InitStructure.DMA_Mode = DMA_Mode_Normal;
  
    DMA_InitStructure.DMA_PeripheralBaseAddr = (uint32_t)(&(SPI1->DR));
    DMA_InitStructure.DMA_PeripheralBurst = DMA_PeripheralBurst_Single;
    DMA_InitStructure.DMA_PeripheralDataSize = DMA_PeripheralDataSize_Byte;
    DMA_InitStructure.DMA_MemoryDataSize = DMA_MemoryDataSize_Byte;
    DMA_InitStructure.DMA_PeripheralInc = DMA_PeripheralInc_Disable;
    DMA_InitStructure.DMA_Priority = DMA_Priority_High;
     
    TM_DMA_ClearFlag(DMA2_Stream3, DMA_FLAG_ALL);
  
    /* Configure Tx DMA */
    DMA_InitStructure.DMA_Channel = DMA_Channel_3;
    DMA_InitStructure.DMA_DIR = DMA_DIR_MemoryToPeripheral;
    DMA_InitStructure.DMA_Memory0BaseAddr = (uint32_t) get_TX_buffer_addr();
    DMA_Init(DMA2_Stream3, &DMA_InitStructure);
     
    TM_DMA_ClearFlag(DMA2_Stream2, DMA_FLAG_ALL);
  
    /* Configure Rx DMA */
    DMA_InitStructure.DMA_Channel = DMA_Channel_3;
    DMA_InitStructure.DMA_DIR = DMA_DIR_PeripheralToMemory;
    DMA_InitStructure.DMA_Memory0BaseAddr = (uint32_t) get_RX_buffer_addr();
    DMA_Init(DMA2_Stream2, &DMA_InitStructure);
         
    /* Enable RX stream */
    DMA2_Stream2->CR |= DMA_SxCR_EN;
     
    /* Enable TX stream */
    DMA2_Stream3->CR |= DMA_SxCR_EN;
     
    /* Enable SPI RX & TX DMA */
    SPI1->CR2 |= SPI_CR2_RXDMAEN | SPI_CR2_TXDMAEN;
      
    //SPI_I2S_ClearFlag(SPI1, SPI_I2S_FLAG_TXE);
    //SPI_I2S_ClearFlag(SPI1, SPI_I2S_FLAG_RXNE);
     
    /* Enable DMA channels */
    //DMA_Cmd(DMA2_Stream0, ENABLE);
    //DMA_Cmd(DMA2_Stream5, ENABLE);
}
 
void init_USART3(void)
{
     
    USART_InitTypeDef USART_InitStructure;
  GPIO_InitTypeDef GPIO_InitStructure;
 
  /* Peripheral Clock Enable -------------------------------------------------*/
  /* Enable GPIO clock */
  RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOD | RCC_AHB1Periph_GPIOD, ENABLE);
   
  /* Enable USART clock */
  RCC_AHB1PeriphClockCmd(RCC_APB1Periph_USART3, ENABLE);
   
  /* Enable the DMA clock */
  //RCC_AHB1PeriphClockCmd(USARTx_DMAx_CLK, ENABLE);
   
  /* USARTx GPIO configuration -----------------------------------------------*/
  /* Connect USART pins to AF7 */
  GPIO_PinAFConfig(GPIOD, GPIO_Pin_8, GPIO_AF_USART3);
  GPIO_PinAFConfig(GPIOD, GPIO_Pin_9, GPIO_AF_USART3);
   
  /* Configure USART Tx and Rx as alternate function push-pull */
  GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF;
  GPIO_InitStructure.GPIO_Speed = GPIO_Speed_100MHz;
  GPIO_InitStructure.GPIO_OType = GPIO_OType_PP;
  GPIO_InitStructure.GPIO_PuPd = GPIO_PuPd_UP;
   
  GPIO_InitStructure.GPIO_Pin = GPIO_Pin_8;
  GPIO_Init(GPIOD, &GPIO_InitStructure);
   
  GPIO_InitStructure.GPIO_Pin = GPIO_Pin_9;
  GPIO_Init(GPIOD, &GPIO_InitStructure);
  
  /* USARTx configuration ----------------------------------------------------*/
  /* Enable the USART OverSampling by 8 */
  //USART_OverSampling8Cmd(USART3, ENABLE); 
   
  /* USARTx configured as follows:
        - BaudRate = 115200 baud
        - Word Length = 8 Bits
        - one Stop Bit
        - No parity
        - Hardware flow control disabled (RTS and CTS signals)
        - Receive and transmit enabled
  */
  USART_InitStructure.USART_BaudRate = 9600;
  USART_InitStructure.USART_WordLength = USART_WordLength_8b;
  USART_InitStructure.USART_StopBits = USART_StopBits_1;
  /* When using Parity the word length must be configured to 9 bits */
  USART_InitStructure.USART_Parity = USART_Parity_No;
  USART_InitStructure.USART_HardwareFlowControl = USART_HardwareFlowControl_None;
  USART_InitStructure.USART_Mode = USART_Mode_Rx | USART_Mode_Tx;
  USART_Init(USART3, &USART_InitStructure);
     
     
}

void init_USART3_Interrupt(void)
{
    NVIC_InitTypeDef NVIC_InitStruct;
    /**
    * Enable RX interrupt
    */
    USART_ITConfig(USART3, USART_IT_RXNE, ENABLE);
  
    /**
    * Set Channel to USART1
    * Set Channel Cmd to enable. That will enable USART1 channel in NVIC
    * Set Both priorities to 0. This means high priority
    *
    * Initialize NVIC
    */
    NVIC_InitStruct.NVIC_IRQChannel = USART3_IRQn;
    NVIC_InitStruct.NVIC_IRQChannelCmd = ENABLE;
    NVIC_InitStruct.NVIC_IRQChannelPreemptionPriority = 0;
    NVIC_InitStruct.NVIC_IRQChannelSubPriority = 0;
    NVIC_Init(&NVIC_InitStruct);
}
 
void init_messageBuffer(void)
{
    messageReceived = false;
		messageStarted = false;  
		messageBuffer_index = 0;
    memset(messageBuffer, 0x00, sizeof(messageBuffer));		
}
 
