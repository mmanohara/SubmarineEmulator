/* Includes */
#include "stm32f4xx.h"
#include "defines.h"


/** Parameters and Constants (edit carefully, but as needed) */
#define SAMPLING_FREQ_KHZ (111) /** Sampling rate */
#define SPEED_OF_SOUND (58425.2f) /** inches per second */
#define SIDE_LENGTH (0.65f) /** hydrophone spacing in inches */
#define TRIGGER_THRESHOLD_VOLTS (0.03f) /** Amplitude of wave needed to trigger the system (in volts) */
#define TRIGGER_DELAY_SEC (0.001f) /** Time to wait after being triggered before actually taking the reading */
#define VALIDATION_THRESHOLD_VOLTS (0.08f) /** Amplitude needed before actually take the reading (in volts) */
#define SLEEP_TIME_SEC (0.25f) /** Time to wait after taking a reading for reverberations to die down */


/** Must be called to initailize, as well as whenever you want to change the pinger frequency */
void initializeOrChangeFrequency(int SIGNAL_FREQ_KHZ);

void changeThreshold(float threshold);

/** Process four new data points (in volts, unless the above constants are sacled accordingly).
	- If a ping is triggered, then the return value is the (new-line terminated) message that needs to be sent over the UART
		- The first three numbers in the string are the direction of the pinger (x,y,z)
		- The next four numbers are differnces in phase (mostly useful for debugging)
		- Also, in this case, the function will take longer than the alloted time to return, so some readings may be skipped.
		- Do NOT call this function (for example via an interupt) if the previous call has not yet returned (for example,
			even if the previous call is taking longer than the alloted time because it is computing the pinger direction)
	- Otherwise the empty string, "", is returned.
   Do not free any returned strings */
//const char* process(float frontLeftData, float frontRightData, float backRightData, float backLeftData, char* serialMsg, uint8_t* triggered);
bool process(float frontLeftData, float frontRightData, float backRightData, float backLeftData, char* serialMsg, uint8_t* triggered);
