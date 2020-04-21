/**************************************************************************/
/*!
    @file     RA8875.c
    @author   Torkom Pailevanian

 This is the library for the Adafruit RA8875 Driver board for TFT displays

    @section  HISTORY
    
    v1.0 - First release
*/

#include "stm32f4xx.h"
#include "defines.h"

/**
 * @brief  Deinitializes pin(s)
 * @note   Pins(s) will be set as analog mode to get low power consumption
 * @param  GPIOx: GPIOx PORT where you want to set pin as input
 * @param  GPIO_Pin: Select GPIO pin(s). You can select more pins with | (OR) operator to set them as input
 * @retval None
 */
bool AD9850_Init(void);

//void AD9850_ParallelSend(uint32_t freq1, uint32_t freq2 );
void AD9850_ParallelSend( double freq );





