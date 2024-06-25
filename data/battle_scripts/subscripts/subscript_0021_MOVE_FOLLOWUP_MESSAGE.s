.include "asm/include/battle_commands.inc"

.data

_000:
    WaitButtonABTime 15
    CompareVarToValue OPCODE_FLAG_NOT, BSCRIPT_VAR_MOVE_STATUS_FLAGS, MOVE_STATUS_SPLASH, _011
    // But nothing happened!
    PrintMessage 795, TAG_NONE
    GoTo _101

_011:
    CompareVarToValue OPCODE_FLAG_NOT, BSCRIPT_VAR_MOVE_STATUS_FLAGS, MOVE_STATUS_ENDURED_ITEM, _043
    CompareMonDataToValue OPCODE_EQU, BATTLER_CATEGORY_DEFENDER, BMON_DATA_ABILITY, ABILITY_STURDY, _104
    PlayBattleAnimation BATTLER_CATEGORY_DEFENDER, BATTLE_ANIMATION_HELD_ITEM
    Wait 
    // {0} hung on using its {1}!
    PrintMessage 912, TAG_NICKNAME_ITEM, BATTLER_CATEGORY_DEFENDER, BATTLER_CATEGORY_DEFENDER
    CheckItemHoldEffect CHECK_OPCODE_NOT_HAVE, BATTLER_CATEGORY_DEFENDER, HOLD_EFFECT_ENDURE, _038
    RemoveItem BATTLER_CATEGORY_DEFENDER

_038:
    Wait 
    WaitButtonABTime 30
    GoTo _073

_043:
    CompareVarToValue OPCODE_FLAG_NOT, BSCRIPT_VAR_MOVE_STATUS_FLAGS, MOVE_STATUS_ENDURED, _063
    CompareMonDataToValue OPCODE_NEQ, BATTLER_CATEGORY_DEFENDER, BMON_DATA_HP, 1, _063
    // {0} endured the hit!
    PrintMessage 445, TAG_NICKNAME, BATTLER_CATEGORY_DEFENDER
    Wait 
    WaitButtonABTime 30
    GoTo _073

_063:
    CompareVarToValue OPCODE_FLAG_NOT, BSCRIPT_VAR_MOVE_STATUS_FLAGS, MOVE_STATUS_ONE_HIT_KO, _073
    // It’s a one-hit KO!
    PrintMessage 775, TAG_NONE
    GoTo _101

_073:
    CompareVarToValue OPCODE_FLAG_SET, BSCRIPT_VAR_BATTLE_STATUS, BATTLE_STATUS_IGNORE_TYPE_EFFECTIVENESS, _104
    CompareVarToValue OPCODE_AND, BSCRIPT_VAR_MOVE_STATUS_FLAGS, MOVE_STATUS_NOT_VERY_EFFECTIVE|MOVE_STATUS_SUPER_EFFECTIVE, _104
    CompareVarToValue OPCODE_FLAG_NOT, BSCRIPT_VAR_MOVE_STATUS_FLAGS, MOVE_STATUS_SUPER_EFFECTIVE, _093
    // It’s super effective!
    PrintMessage 780, TAG_NONE
    GoTo _101

_093:
    CompareVarToValue OPCODE_FLAG_NOT, BSCRIPT_VAR_MOVE_STATUS_FLAGS, MOVE_STATUS_NOT_VERY_EFFECTIVE, _104
    // It’s not very effective...
    PrintMessage 779, TAG_NONE

_101:
    Wait 
    WaitButtonABTime 30

_104:
    End 
