.include "asm/include/battle_commands.inc"

.data

_000:
    CheckItemHoldEffect CHECK_OPCODE_HAVE, BATTLER_CATEGORY_ATTACKER, HOLD_EFFECT_ARCEUS_FIGHTING, _086
    CheckItemHoldEffect CHECK_OPCODE_HAVE, BATTLER_CATEGORY_ATTACKER, HOLD_EFFECT_ARCEUS_FLYING, _092
    CheckItemHoldEffect CHECK_OPCODE_HAVE, BATTLER_CATEGORY_ATTACKER, HOLD_EFFECT_ARCEUS_POISON, _098
    CheckItemHoldEffect CHECK_OPCODE_HAVE, BATTLER_CATEGORY_ATTACKER, HOLD_EFFECT_ARCEUS_GROUND, _104
    CheckItemHoldEffect CHECK_OPCODE_HAVE, BATTLER_CATEGORY_ATTACKER, HOLD_EFFECT_ARCEUS_ROCK, _110
    CheckItemHoldEffect CHECK_OPCODE_HAVE, BATTLER_CATEGORY_ATTACKER, HOLD_EFFECT_ARCEUS_BUG, _116
    CheckItemHoldEffect CHECK_OPCODE_HAVE, BATTLER_CATEGORY_ATTACKER, HOLD_EFFECT_ARCEUS_GHOST, _122
    CheckItemHoldEffect CHECK_OPCODE_HAVE, BATTLER_CATEGORY_ATTACKER, HOLD_EFFECT_ARCEUS_STEEL, _128
    CheckItemHoldEffect CHECK_OPCODE_HAVE, BATTLER_CATEGORY_ATTACKER, HOLD_EFFECT_ARCEUS_FAIRY, _134
    CheckItemHoldEffect CHECK_OPCODE_HAVE, BATTLER_CATEGORY_ATTACKER, HOLD_EFFECT_ARCEUS_FIRE, _140
    CheckItemHoldEffect CHECK_OPCODE_HAVE, BATTLER_CATEGORY_ATTACKER, HOLD_EFFECT_ARCEUS_WATER, _146
    CheckItemHoldEffect CHECK_OPCODE_HAVE, BATTLER_CATEGORY_ATTACKER, HOLD_EFFECT_ARCEUS_GRASS, _152
    CheckItemHoldEffect CHECK_OPCODE_HAVE, BATTLER_CATEGORY_ATTACKER, HOLD_EFFECT_ARCEUS_ELECTRIC, _158
    CheckItemHoldEffect CHECK_OPCODE_HAVE, BATTLER_CATEGORY_ATTACKER, HOLD_EFFECT_ARCEUS_PSYCHIC, _164
    CheckItemHoldEffect CHECK_OPCODE_HAVE, BATTLER_CATEGORY_ATTACKER, HOLD_EFFECT_ARCEUS_ICE, _170
    CheckItemHoldEffect CHECK_OPCODE_HAVE, BATTLER_CATEGORY_ATTACKER, HOLD_EFFECT_ARCEUS_DRAGON, _176
    CheckItemHoldEffect CHECK_OPCODE_HAVE, BATTLER_CATEGORY_ATTACKER, HOLD_EFFECT_ARCEUS_DARK, _182
    GoTo _186

_086:
    UpdateVar OPCODE_SET, BSCRIPT_VAR_MOVE_TYPE, TYPE_FIGHTING
    GoTo _186

_092:
    UpdateVar OPCODE_SET, BSCRIPT_VAR_MOVE_TYPE, TYPE_FLYING
    GoTo _186

_098:
    UpdateVar OPCODE_SET, BSCRIPT_VAR_MOVE_TYPE, TYPE_POISON
    GoTo _186

_104:
    UpdateVar OPCODE_SET, BSCRIPT_VAR_MOVE_TYPE, TYPE_GROUND
    GoTo _186

_110:
    UpdateVar OPCODE_SET, BSCRIPT_VAR_MOVE_TYPE, TYPE_ROCK
    GoTo _186

_116:
    UpdateVar OPCODE_SET, BSCRIPT_VAR_MOVE_TYPE, TYPE_BUG
    GoTo _186

_122:
    UpdateVar OPCODE_SET, BSCRIPT_VAR_MOVE_TYPE, TYPE_GHOST
    GoTo _186

_128:
    UpdateVar OPCODE_SET, BSCRIPT_VAR_MOVE_TYPE, TYPE_STEEL
    GoTo _186

_134:
    UpdateVar OPCODE_SET, BSCRIPT_VAR_MOVE_TYPE, TYPE_MYSTERY
    GoTo _186

_140:
    UpdateVar OPCODE_SET, BSCRIPT_VAR_MOVE_TYPE, TYPE_FIRE
    GoTo _186

_146:
    UpdateVar OPCODE_SET, BSCRIPT_VAR_MOVE_TYPE, TYPE_WATER
    GoTo _186

_152:
    UpdateVar OPCODE_SET, BSCRIPT_VAR_MOVE_TYPE, TYPE_GRASS
    GoTo _186

_158:
    UpdateVar OPCODE_SET, BSCRIPT_VAR_MOVE_TYPE, TYPE_ELECTRIC
    GoTo _186

_164:
    UpdateVar OPCODE_SET, BSCRIPT_VAR_MOVE_TYPE, TYPE_PSYCHIC
    GoTo _186

_170:
    UpdateVar OPCODE_SET, BSCRIPT_VAR_MOVE_TYPE, TYPE_ICE
    GoTo _186

_176:
    UpdateVar OPCODE_SET, BSCRIPT_VAR_MOVE_TYPE, TYPE_DRAGON
    GoTo _186

_182:
    UpdateVar OPCODE_SET, BSCRIPT_VAR_MOVE_TYPE, TYPE_DARK

_186:
    CalcCrit 
    CalcDamage 
    End 
