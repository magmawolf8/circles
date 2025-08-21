#include "invsq.h"

q16_16_t sqrt32_q16(uint32_t n) {
    uint32_t res = 0;

    uint32_t bit = 1 << 30;
    while (bit > n)
        bit >>= 2;

    while (bit) {
        if (n >= res + bit) {
            n -= res + bit;
            res = (res >> 1) + bit;
        } else {
            res >>= 1;
        }
        bit >>= 2;
    }

    // at this point, res = xb if b=1. res = 2xb if b=0.5.
    // n is not yet updated. currently it is r^2 - x^2.
    // 2x + 1 = n already happened in the loop above.
    // proper variables were updated.
    // Next, need to 
    // now it is time to do 2x * 2 + 1 = 4*n.
    
    for (uint8_t _ = 1; 16 >= _; _++) {
        if (n >= res + 1) {
            n -= res + 1;
            res = (res << 1) | 1;
        } else {
            res <<= 1;
        }
        n <<= 2;
    }


    // now, the remainder should be processed.
    // I would left-shift the integer portion, then calculate fractional portion.
    // I need to squeeze another 16 bits of the root from the remainder (n).
    // Do some more trickery... left shift res (to make space for another bit)
    // Left shift the remainder as well, by 2 bits... 
    


    return res;
}

uint32_t divu32_q(uint32_t a, uint32_t b, uint8_t frac) {
    uint32_t quo = 0;
    uint32_t rem = 0;
    uint32_t hi = 0;

    for (int k = 32 - 1 + frac; k >= 0; --k) {
        hi = (hi << 1) | (rem >> 31);
        rem <<= 1;

        if (k >= frac)
            rem |= (a >> (k - frac)) & 1;

        if (hi || rem >= b) {
            uint32_t borrow = (rem < b);
            rem -= b;
            hi -= borrow;

            quo |= (uint32_t)1 << k;
        }
    }

    return quo;
}
