import math
#
#
#
#
#********************************
#                       Constants
#********************************
LED_POINT_MAP = [
    [0, 15], [3, 27], [5, 40], [8, 52], [13, 15], [19, 27], [23, 40], [29, 52], [26, 15], [32, 27], [36, 40], [42, 52], [39, 15], [45, 27], [49, 40], [55, 52], [52, 15], [58, 27], [62, 40], [68, 52], [65, 15], [71, 27], [75, 40], [81, 52], [78, 15], [84, 27], [88, 40], [94, 52], [91, 15], [97, 27], [101, 40], [107, 52], [104, 15], [110, 27], [114, 40], [120, 52], [117, 15], [123, 27], [127, 40], [133, 52], [130, 15], [136, 27], [140, 40], [146, 52], [143, 15], [149, 27], [153, 40], [198, 64], [156, 15], [162, 27], [170, 52], [211, 52], [175, 15], [179, 27], [174, 40], [211, 64], [3, 64], [19, 64], [36, 64], [91, 64], [0, 0], [146, 64], [162, 64], [179, 64], [0, 0], [None, None], [None, None], [None, None], [16, 0], [None, None], [None, None], [None, None], [29, 0], [None, None], [None, None], [224, 64], [42, 0], [None, None], [None, None], [None, None], [55, 0], [None, None], [None, None], [None, None], [71, 0], [None, None], [None, None], [None, None], [84, 0], [None, None], [None, None], [None, None], [97, 0], [None, None], [None, None], [None, None], [110, 0], [None, None], [None, None], [None, None], [127, 0], [None, None], [None, None], [None, None], [140, 0], [None, None], [None, None], [None, None], [153, 0], [None, None], [None, None], [None, None], [166, 0], [None, None], [198, 27], [198, 15], [182, 0], [None, None], [211, 27], [211, 15], [198, 0], [None, None], [224, 27], [224, 15], [211, 0], [None, None], [None, None], [224, 0]
]
key_width = 13 # keyboard units

GRAVITY_K = 0x17FFFFF
D_0_V = 0x488 # Q12.4
EMA_FACTOR = 10
MAX_INST_EMA = (1 << (32 - EMA_FACTOR)) - 1
THRESHOLD_EMA = round(MAX_INST_EMA * 17 / 720) # 20 words per minute
MIN_D_P = 20 # keyboard units

UPPER_LIM_EMA = round(MAX_INST_EMA * 42 / 720) # 50 words per minute
MAX_D_P = 50 # keyboard units

sharpness = 0.25
MAX_LOGISTIC = 191
ENTRY_WIDTH = 4
TABLE_SIZE = 0x10000 >> ENTRY_WIDTH
#
#
#
#
#********************************
#                          Bounds
#********************************
MIN_PX, MIN_PY = 0xFFFFFFFF, 0xFFFFFFFF
MAX_PX, MAX_PY = 0, 0
for point in LED_POINT_MAP:
    if point[0] is None:
        continue
    if point[0] < MIN_PX:
        MIN_PX = point[0]
    if point[0] > MAX_PX:
        MAX_PX = point[0]
    if point[1] < MIN_PY:
        MIN_PY = point[1]
    if point[1] > MAX_PY:
        MAX_PY = point[1]

unscaled_min_px = MIN_PX - key_width // 2 + MIN_D_P
unscaled_max_px = MAX_PX + key_width // 2 - MIN_D_P
unscaled_min_py = MIN_PY - key_width // 2 + MIN_D_P
unscaled_max_py = MAX_PY + key_width // 2 - MIN_D_P

dist = unscaled_max_px - unscaled_min_px
dist -= unscaled_max_py - unscaled_min_py
r = dist // 2
if dist >= 0:
    unscaled_max_py += r
    unscaled_min_py -= r
else:
    unscaled_max_px += r
    unscaled_min_px -= r

K = ((1 << 32) - 1)/((unscaled_max_px - unscaled_min_px)**2 + (unscaled_max_py - unscaled_min_py)**2)
K = math.sqrt(K)
K_q17_15 = K * 2**15

LED_POINT_MAP = [
    [round(K_q17_15*point[0]), round(K_q17_15*point[1])] 
    if point[0] is not None 
    else [None, None] 
    for point in LED_POINT_MAP
]

MIN_PX = unscaled_min_px * K_q17_15
MAX_PX = unscaled_max_px * K_q17_15
MIN_PY = unscaled_min_py * K_q17_15
MAX_PY = unscaled_max_py * K_q17_15

MAX_D_P *= K
MIN_D_P *= K

MIN_D_P = round(MIN_D_P)
MAX_D_P = round(MAX_D_P)
MIN_PX = round(MIN_PX)
MAX_PX = round(MAX_PX)
MIN_PY = round(MIN_PY)
MAX_PY = round(MAX_PY)
#
#
#
#
#********************************
#                     Logit table
#********************************
LOGIT_TABLE = list()

def logistic_from_points(x5, x95):
    k = (2 * math.log(19)) / (x95 - x5)
    x0 = x5 + (math.log(19) / k)

    def f(x):
        return L_min + (L_max - L_min) / (1 + math.exp(-k * (x - x0)))

    return x0, k

x0, k = logistic_from_points(THRESHOLD_EMA, UPPER_LIM_EMA);

def f(x):
    return -math.log((MAX_D_P - MIN_D_P) / (x - MIN_D_P) - 1) / k + x0

for i in range(MAX_D_P - MIN_D_P + 1):
    if i == 0:
        LOGIT_TABLE.append(0)
    elif i == MAX_D_P - MIN_D_P:
        LOGIT_TABLE.append(0xFFFFFFFF)
    else:
        val = round(f(MIN_D_P + i))
        LOGIT_TABLE.append(0 if val < 0 else (0xFFFFFFFF if val > 0xFFFFFFFF else val))
#
#
#
#
#********************************
#                  Logistic table
#********************************
LOGISTIC_TABLE = list()
sharpness /= K
for i in range(TABLE_SIZE):
    LOGISTIC_TABLE.append(round(MAX_LOGISTIC/(1 + math.exp(-sharpness * (i << ENTRY_WIDTH)))))
#
#
#
#
#********************************
# Write everything to constants.c
#********************************
def emit_table(table):
    res = list()
    for entry in table:
        res.append(f"{hex(entry)}, ")
    return "".join(res)

with open("constants.c", "w") as f:
    f.write(f"""\
#include "constants.h"

const q17_15_t MIN_PX = {MIN_PX};
const q17_15_t MAX_PX = {MAX_PX};
const q17_15_t MIN_PY = {MIN_PY};
const q17_15_t MAX_PY = {MAX_PY};

const int32_t GRAVITY_K = {GRAVITY_K};

const int32_t D_0_V = {D_0_V};

const uint32_t MAX_INST_EMA = {MAX_INST_EMA};
const uint8_t EMA_FACTOR = {EMA_FACTOR};
const uint32_t THRESHOLD_EMA = {THRESHOLD_EMA};
const uint32_t MIN_D2_P = {MIN_D_P * MIN_D_P};
const uint16_t MIN_D_P = {MIN_D_P};

const uint32_t UPPER_LIM_EMA = {UPPER_LIM_EMA};
const uint16_t MAX_D_P = {MAX_D_P};

const uint8_t MAX_LOGISTIC = {MAX_LOGISTIC};
const uint8_t ENTRY_WIDTH = {ENTRY_WIDTH};
const uint16_t TABLE_SIZE = {TABLE_SIZE};

""")
    f.write("const uint32_t LOGIT_TABLE[] = {\n")
    f.write(emit_table(LOGIT_TABLE))
    f.write("\n};\n\n")

    f.write("const xy_t LED_POINT_MAP[] = {\n")
    for point in LED_POINT_MAP:
        if point[0] is not None:
            f.write(f"{{{point[0]}, {point[1]}}}, ")
        else:
            f.write("{NO_LED, NO_LED}, ")
    f.write("\n};\n\n")

    f.write("const uint8_t LOGISTIC_TABLE[] = {\n")
    f.write(emit_table(LOGISTIC_TABLE))
    f.write("\n};\n")
