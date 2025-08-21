#include "constants.h"
#include "expit.h"

uint16_t expitu32_u16(uint32_t n) {
    // binary search for the expit of n
    // correspond using the table
    uint16_t lo = 0, i, hi = MAX_D_P - MIN_D_P;

    if (LOGIT_TABLE[lo] >= n) return MIN_D_P;
    if (n >= LOGIT_TABLE[hi]) return MAX_D_P;

    while (hi >= lo) {
        i = (hi + lo) >> 1;
        if (LOGIT_TABLE[i] <= n) 
            lo = i + 1;
        else 
            hi = i - 1;
    }
    
    return hi + MIN_D_P;
}

