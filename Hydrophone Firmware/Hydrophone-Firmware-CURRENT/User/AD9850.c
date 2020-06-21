////////////////////////////////////////////////////////////////////////////////
// https://zissisprojects.wordpress.com                                        //
// ** AD9850 DDS module initial programming code for STM32fxxx **             //
// This example was tested on a STM32f407vg discovery board and it is not     //
// guranteed to be working as is on all stm32 microprocessors. Please refer to//
// your own device's manual for tweaking this code                            //
//                                                                            // 
// This code was made by Zissis Chiotis zchiotis@gmail.com                    //
// you may distribute this code and use it for non-commercial applications    //
////////////////////////////////////////////////////////////////////////////////
#include "stm32f4xx.h"
#include "defines.h"
#include "AD9850.h"
#include "tm_stm32f4_delay.h"
#include "tm_stm32f4_gpio.h"
#include "math.h"
#include "defines.h"

#define DSS_RST GPIO_Pin_6
#define DSS_FQ_UD GPIO_Pin_9
#define DSS_W_CLK GPIO_Pin_8

uint8_t W[5] = {0,0,0,0,0};                 //tword array, keep this array global 
uint32_t tword;

bool AD9850_Init(void){
	
		// Initialize GPIO
		TM_GPIO_Init(GPIOD, GPIO_Pin_0 | GPIO_Pin_1 | GPIO_Pin_2 | GPIO_Pin_3 | GPIO_Pin_4 | GPIO_Pin_5 | GPIO_Pin_6 | GPIO_Pin_7 |
												DSS_FQ_UD | DSS_W_CLK, TM_GPIO_Mode_OUT, TM_GPIO_OType_PP, TM_GPIO_PuPd_DOWN, TM_GPIO_Speed_High);
		
		TM_GPIO_Init(GPIOB, DSS_RST , TM_GPIO_Mode_OUT, TM_GPIO_OType_PP, TM_GPIO_PuPd_DOWN, TM_GPIO_Speed_High);
		
	
		TM_GPIO_SetPinLow(GPIOD, GPIO_Pin_0 | GPIO_Pin_1 | GPIO_Pin_2 | GPIO_Pin_3 | GPIO_Pin_4 | GPIO_Pin_5 | GPIO_Pin_6 | GPIO_Pin_7 | DSS_W_CLK );
		TM_GPIO_SetPinLow(GPIOB, DSS_RST );
		TM_GPIO_SetPinHigh(GPIOD, DSS_FQ_UD ); // Set FQ_UD pin high
	
		/* Reset the AD9850*/
		TM_GPIO_SetPinHigh(GPIOB, DSS_RST );
		Delayms(1);
		TM_GPIO_SetPinLow(GPIOB, DSS_RST  );
		// Device now reset
		
		return true;
}

 

void AD9850_ParallelSend( double freq )
{
		uint8_t k;
		tword = (int) (freq  * 34.359738);
		//tword = (int)( (freq / 100.0) * 3436.0);		// Tuning word calculation for use on the module with 125 MHz clock
		//tword = (int) (freq  * 85.899);   	// Tuning word calculation for use on the module with 50 MHz clock
		W[4] = tword;												//converting to 5words*8bits
		W[3] = tword >> 8;
		W[2] = tword >> 16;
		W[1] = tword >> 24;
		W[0] = 0x00;
	 
		TM_GPIO_SetPinLow(GPIOD, DSS_FQ_UD );    // FU_UD low
		
		for (k=0;k<5;k++){ 
			GPIO_Write(GPIOD, W[k]);                         //send the bits
			
			TM_GPIO_SetPinHigh(GPIOD, DSS_W_CLK );       //Pulse W_CLK
			TM_GPIO_SetPinLow(GPIOD, DSS_W_CLK ); 
		} 
		
		TM_GPIO_SetPinHigh(GPIOD, DSS_FQ_UD );       // FU_UD high
		
}

