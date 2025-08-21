#ifndef CONSTANTS_H
#define CONSTANTS_H
//
//
//
//
//********************************
//                        Includes
//********************************
#include QMK_KEYBOARD_H
//
//
//
//
//********************************
//    Fixed-point type definitions
//********************************
typedef int32_t q17_15_t; // used for position
typedef int32_t q16_16_t; // used during invsq
typedef int32_t q13_19_t; // used for velocity
typedef int32_t q12_20_t; // used during invsq
typedef int32_t q1_31_t;  // used during invsq

extern const q17_15_t MIN_PX;
extern const q17_15_t MAX_PX;
extern const q17_15_t MIN_PY;
extern const q17_15_t MAX_PY;

extern const int32_t GRAVITY_K;

extern const int32_t D_0_V; // 13 bit signed max

extern const uint32_t MAX_INST_EMA;
extern const uint8_t EMA_FACTOR;
extern const uint32_t THRESHOLD_EMA;
extern const uint32_t MIN_D2_P;
extern const uint16_t MIN_D_P;

extern const uint32_t LOGIT_TABLE[];
extern const uint32_t UPPER_LIM_EMA;
extern const uint16_t MAX_D_P;

typedef struct {
    q17_15_t x;
    q17_15_t y;
} xy_t;
extern const xy_t LED_POINT_MAP[];

extern const uint8_t LOGISTIC_TABLE[];
extern const uint8_t MAX_LOGISTIC;
extern const uint8_t ENTRY_WIDTH;
extern const uint16_t TABLE_SIZE;
#endif // CONSTANTS_H
