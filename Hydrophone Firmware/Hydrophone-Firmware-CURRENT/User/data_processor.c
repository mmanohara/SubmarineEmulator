#define _USE_MATH_DEFINES		/** Visual Studio artifact */
#define _CRT_SECURE_NO_WARNINGS /** Visual Studio artifact */

#include "data_processor.h"
#include <math.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#define FLOAT_PI 3.14159265358979323846264338327950288f

/** Variables (internally managed) */
#define SAMPLING_FREQ_HZ (SAMPLING_FREQ_KHZ * 1000) /** Sampling frequency */
#define WINDOW_LEN (SAMPLING_FREQ_HZ / 1000) /** Fixed 1 ms window */


int SIGNAL_FREQ_HZ; /** Frequency of the pinger */
float NORMALIZED_TRIGGER_THRESHOLD_HI;
float NORMALIZED_TRIGGER_THRESHOLD_LO;
float TRIGGER_THRESHOLD_HI;
float TRIGGER_THRESHOLD_LO;

float side_length = SIDE_LENGTH;

/** woot doot this is Eilleen testing out github perms**/
/** Precompute sin and cos with frequency equal to SIGNAL_FREQ_HZ, for 1ms worth of data at a rate equal to SAMPLING_FREQ_HZ
	* It assumes SIGNAL_FREQ_HZ and SAMPLING_FREQ_HZ are integer multiples of 1000 to gaurentee that the table is periodic. Otherwise it will silently fail */
float sinTable[WINDOW_LEN], cosTable[WINDOW_LEN];
void recomputeSinCosTable() {
	int i;
	for (i = 0; i < WINDOW_LEN; i++) {
		sinTable[i] = sin(i * 2 * FLOAT_PI * SIGNAL_FREQ_HZ / (double)SAMPLING_FREQ_HZ);
		cosTable[i] = cos(i * 2 * FLOAT_PI * SIGNAL_FREQ_HZ / (double)SAMPLING_FREQ_HZ);
	}
}



/** Stores and calculates everything pertinent to a single hydrophone using a circular buffer */
int Hydrophone_curInd; // Current index into the circular buffer 'buf'
struct Hydrophone {
// Private:
	float buf[WINDOW_LEN]; // A circular buffer to store all data points in the current window
// Public:
	float sinAccum; // Sin function dotted with the signal in the current window
	float cosAccum; // Cos function dotted with the signal in the current window
	float normAccum; // Sum of squares of data points in the current window
};

// Part of Hydrophone class
// Reset the accumlated values to 0 (must be called on initialization, as well as to reset numerical error build up)
void Hydrophone_reinitialize(struct Hydrophone* this) {
	int i;
	for (i = 0; i < WINDOW_LEN; i++)
		this->buf[i] = 0;
	Hydrophone_curInd = this->sinAccum = this->cosAccum = this->normAccum = 0;
}

// Part of Hydrophone class
// Add a new data point and shift the current window one unit over
void Hydrophone_add(struct Hydrophone* this, float newVal) {
	this->normAccum -= this->buf[Hydrophone_curInd] * this->buf[Hydrophone_curInd];
	float diff = newVal - this->buf[Hydrophone_curInd];
	this->sinAccum += diff * sinTable[Hydrophone_curInd];
	this->cosAccum += diff * cosTable[Hydrophone_curInd];
	this->buf[Hydrophone_curInd] = newVal;
	this->normAccum += this->buf[Hydrophone_curInd] * this->buf[Hydrophone_curInd];
}

// Part of Hydrophone class
// Compute the squared magnitude of the frequency component we are interested in
float Hydrophone_magSq(struct Hydrophone* this) {
	return this->sinAccum*this->sinAccum + this->cosAccum*this->cosAccum;
}

// Part of Hydrophone class
// Compute the norm of the signal (scaling is arbitrary, except that it matches the scale of magSq())
float Hydrophone_normSq(struct Hydrophone* this) {
	return this->normAccum * WINDOW_LEN / 2;
}

// Part of Hydrophone class
// Compute the phase of the signal in the current window. WARNING: this is expensive
float Hydrophone_phase(struct Hydrophone* this) {
	return atan2(this->sinAccum, this->cosAccum);
}

struct Hydrophone hydrophone[4];





/** (Public Function) See header file for details */
void initializeOrChangeFrequency(int SIGNAL_FREQ_KHZ) {
	SIGNAL_FREQ_HZ = SIGNAL_FREQ_KHZ * 1000;
	switch (SIGNAL_FREQ_KHZ) {
		case 25000:
			side_length = 0.9;
			break;
		case 30000:
			side_length = 0.8;
			break;
		case 35000:
			side_length = 0.7;
			break;
		case 40000:
			side_length = 0.6;
			break;
	}
	recomputeSinCosTable();
	int i;
	for (i = 0; i < 4; i++)
		Hydrophone_reinitialize(&hydrophone[i]);
}

void changeThreshold(float threshold_hi, float threshold_lo) {
	TRIGGER_THRESHOLD_HI = threshold_hi;
	NORMALIZED_TRIGGER_THRESHOLD_HI = threshold_hi * threshold_hi * WINDOW_LEN * WINDOW_LEN / 4.0f;
	TRIGGER_THRESHOLD_LO = threshold_lo;
	NORMALIZED_TRIGGER_THRESHOLD_LO = threshold_lo * threshold_lo * WINDOW_LEN * WINDOW_LEN / 4.0f;
}

void changeSideLength(float side_length_new) {
	side_length = side_length_new;
}


// Internal state variables for detecting when a ping is happening and when to take a reading
typedef enum { LISTENING, TRIGGERED_HI, TRIGGERED_LO, SLEEPING_HI, SLEEPING_LO } Mode;
Mode mode = LISTENING;
int ticksSinceLastMode = 0;

//char serialMsg[200]; // Output message (which actually contains data)
char emptyMsg[] = "";

int processing = 0; // Used (as a boolean) to check if the function is being re-entered
/** (Public Function) See header file for details */
bool process(float frontLeftData, float frontRightData, float backRightData, float backLeftData, char* serialMsg, uint8_t* triggered) {
	if (processing) // If you re-enter this function, it will just quit. This is bad to do in general, but ok if there is a ping
		return false;

	processing = 1;

	float dir[3], dPhase[4], data[4] = { frontLeftData, frontRightData, backRightData, backLeftData };

	// Compute average magnitue of the frequency we are interested and overall average norm of the signal
	int i;
	for (i = 0; i < 4; i++) 
		Hydrophone_add(&hydrophone[i], data[i]);

	Hydrophone_curInd++;
	if (Hydrophone_curInd == WINDOW_LEN)
		Hydrophone_curInd = 0;

	float magnitudeSq = Hydrophone_magSq(hydrophone);

	ticksSinceLastMode++;

	switch (mode) {
	case LISTENING:
		if (magnitudeSq > NORMALIZED_TRIGGER_THRESHOLD_HI) {
			mode = TRIGGERED_HI;
			ticksSinceLastMode = 0;
		}
		if (magnitudeSq > NORMALIZED_TRIGGER_THRESHOLD_LO) {
			mode = TRIGGERED_LO;
			ticksSinceLastMode = 0;
		}
		break;
	case TRIGGERED_HI:
		if (ticksSinceLastMode > TRIGGER_DELAY_SEC * SAMPLING_FREQ_HZ) {
			float normSq = Hydrophone_normSq(hydrophone);
			if (/*magnitudeSq > 0.5f * normSq && *//*magnitudeSq > NORMALIZED_VALIDATION_THRESHOLD*/ magnitudeSq > NORMALIZED_TRIGGER_THRESHOLD_HI) {
				// In this case we will run overtime to compute the angle of the pinger (and then go to sleep)
				float phase[4];
				for (i = 0; i < 4; i++)
					phase[i] = Hydrophone_phase(&hydrophone[i]);

				for (i = 0; i < 4; i++) {
					dPhase[i] = phase[i] - phase[(i + 1) % 4];
					if (dPhase[i] > FLOAT_PI)
						dPhase[i] -= 2 * FLOAT_PI;
					if (dPhase[i] < -FLOAT_PI)
						dPhase[i] += 2 * FLOAT_PI;
				}

				dir[0] = (dPhase[3] - dPhase[1]) * SPEED_OF_SOUND / (4 * FLOAT_PI * SIGNAL_FREQ_HZ * side_length);
				dir[1] = (dPhase[0] - dPhase[2]) * SPEED_OF_SOUND / (4 * FLOAT_PI * SIGNAL_FREQ_HZ * side_length);
				dir[2] = 1 - dir[0] * dir[0] - dir[1] * dir[1];
				dir[2] = sqrt(dir[2] < 0 ? 0 : dir[2]);

				mode = SLEEPING_HI;
				ticksSinceLastMode = 0;

				// To prevent numerical errors from buiding up in sinAccum and cosAccum
				for (i = 0; i < 4; i++)
					Hydrophone_reinitialize(&hydrophone[i]);

				// Create the output message
				sprintf(serialMsg, "$%f %f %f %f %f %f %f %f#\n\r", dir[0], dir[1], dir[2], dPhase[0], dPhase[1], dPhase[2], dPhase[3], magnitudeSq);
				processing = 0;
				*triggered = true;
				return true;
			}
			else {
				mode = LISTENING;
				ticksSinceLastMode = 0;

				// To prevent numerical errors from buiding up in sinAccum and cosAccum
				for (i = 0; i < 4; i++)
					Hydrophone_reinitialize(&hydrophone[i]);
			}
		}
		break;
		case TRIGGERED_LO:
		if (ticksSinceLastMode > TRIGGER_DELAY_SEC * SAMPLING_FREQ_HZ) {
			float normSq = Hydrophone_normSq(hydrophone);
			if (/*magnitudeSq > 0.5f * normSq && *//*magnitudeSq > NORMALIZED_VALIDATION_THRESHOLD*/ magnitudeSq > NORMALIZED_TRIGGER_THRESHOLD_LO) {
				// In this case we will run overtime to compute the angle of the pinger (and then go to sleep)
				float phase[4];
				for (i = 0; i < 4; i++)
					phase[i] = Hydrophone_phase(&hydrophone[i]);

				for (i = 0; i < 4; i++) {
					dPhase[i] = phase[i] - phase[(i + 1) % 4];
					if (dPhase[i] > FLOAT_PI)
						dPhase[i] -= 2 * FLOAT_PI;
					if (dPhase[i] < -FLOAT_PI)
						dPhase[i] += 2 * FLOAT_PI;
				}

				dir[0] = (dPhase[3] - dPhase[1]) * SPEED_OF_SOUND / (4 * FLOAT_PI * SIGNAL_FREQ_HZ * side_length);
				dir[1] = (dPhase[0] - dPhase[2]) * SPEED_OF_SOUND / (4 * FLOAT_PI * SIGNAL_FREQ_HZ * side_length);
				dir[2] = 1 - dir[0] * dir[0] - dir[1] * dir[1];
				dir[2] = sqrt(dir[2] < 0 ? 0 : dir[2]);

				mode = SLEEPING_LO;
				ticksSinceLastMode = 0;

				// To prevent numerical errors from buiding up in sinAccum and cosAccum
				for (i = 0; i < 4; i++)
					Hydrophone_reinitialize(&hydrophone[i]);

				// Create the output message
				sprintf(serialMsg, "$%f %f %f %f %f %f %f %f#\n\r", dir[0], dir[1], dir[2], dPhase[0], dPhase[1], dPhase[2], dPhase[3], magnitudeSq);
				processing = 0;
				*triggered = true;
				return true;
			}
			else {
				mode = LISTENING;
				ticksSinceLastMode = 0;

				// To prevent numerical errors from buiding up in sinAccum and cosAccum
				for (i = 0; i < 4; i++)
					Hydrophone_reinitialize(&hydrophone[i]);
			}
		}

		break;
	case SLEEPING_HI: // To prevent triggering on reverberations
		if (ticksSinceLastMode > SLEEP_TIME_SEC * SAMPLING_FREQ_HZ) {
			mode = LISTENING;
			ticksSinceLastMode = 0;
		}
		break;
	case SLEEPING_LO: // To prevent triggering on reverberations
		if (ticksSinceLastMode > SLEEP_TIME_SEC * SAMPLING_FREQ_HZ) {
			mode = LISTENING;
			ticksSinceLastMode = 0;
		}
		break;
	}
	
	switch (mode) {
	case LISTENING:
		if (magnitudeSq > NORMALIZED_TRIGGER_THRESHOLD_LO) {
			mode = TRIGGERED_LO;
			ticksSinceLastMode = 0;
		}
		break;
		case TRIGGERED_LO:
		if (ticksSinceLastMode > TRIGGER_DELAY_SEC * SAMPLING_FREQ_HZ) {
			float normSq = Hydrophone_normSq(hydrophone);
			if (/*magnitudeSq > 0.5f * normSq && *//*magnitudeSq > NORMALIZED_VALIDATION_THRESHOLD*/ magnitudeSq > NORMALIZED_TRIGGER_THRESHOLD_LO) {
				// In this case we will run overtime to compute the angle of the pinger (and then go to sleep)
				float phase[4];
				for (i = 0; i < 4; i++)
					phase[i] = Hydrophone_phase(&hydrophone[i]);

				for (i = 0; i < 4; i++) {
					dPhase[i] = phase[i] - phase[(i + 1) % 4];
					if (dPhase[i] > FLOAT_PI)
						dPhase[i] -= 2 * FLOAT_PI;
					if (dPhase[i] < -FLOAT_PI)
						dPhase[i] += 2 * FLOAT_PI;
				}

				dir[0] = (dPhase[3] - dPhase[1]) * SPEED_OF_SOUND / (4 * FLOAT_PI * SIGNAL_FREQ_HZ * side_length);
				dir[1] = (dPhase[0] - dPhase[2]) * SPEED_OF_SOUND / (4 * FLOAT_PI * SIGNAL_FREQ_HZ * side_length);
				dir[2] = 1 - dir[0] * dir[0] - dir[1] * dir[1];
				dir[2] = sqrt(dir[2] < 0 ? 0 : dir[2]);

				mode = SLEEPING_LO;
				ticksSinceLastMode = 0;

				// To prevent numerical errors from buiding up in sinAccum and cosAccum
				for (i = 0; i < 4; i++)
					Hydrophone_reinitialize(&hydrophone[i]);

				// Create the output message
				sprintf(serialMsg, "$%f %f %f %f %f %f %f %f#\n\r", dir[0], dir[1], dir[2], dPhase[0], dPhase[1], dPhase[2], dPhase[3], magnitudeSq);
				processing = 0;
				*triggered = true;
				return true;
			}
			else {
				mode = LISTENING;
				ticksSinceLastMode = 0;

				// To prevent numerical errors from buiding up in sinAccum and cosAccum
				for (i = 0; i < 4; i++)
					Hydrophone_reinitialize(&hydrophone[i]);
			}
		}

		break;
	case SLEEPING_LO: // To prevent triggering on reverberations
		if (ticksSinceLastMode > SLEEP_TIME_SEC * SAMPLING_FREQ_HZ) {
			mode = LISTENING;
			ticksSinceLastMode = 0;
		}
		break;
	}

	processing = 0;
	return false;
}
