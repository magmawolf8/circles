#include "constants.h"
#include "logistic.h"

uint8_t logistic32_u8(int32_t n) {
    uint16_t un, i0, i1, w;
    uint32_t r0, r1, res;

    un = (n < 0 ? -n : n);

    i0 = un >> ENTRY_WIDTH;
    i1 = (i0 < TABLE_SIZE - 1 ? i0 + 1 : i0);
    w = un & ((1u << ENTRY_WIDTH) - 1);

    r0 = (uint32_t)(LOGISTIC_TABLE[i0]) * (uint32_t)((1u << ENTRY_WIDTH) - w);
    r1 = (uint32_t)(LOGISTIC_TABLE[i1]) * (uint32_t)(w);

    res = r0 + r1;
    res >>= ENTRY_WIDTH;

    if (n < 0) res = MAX_LOGISTIC - res;

    return res;
}
