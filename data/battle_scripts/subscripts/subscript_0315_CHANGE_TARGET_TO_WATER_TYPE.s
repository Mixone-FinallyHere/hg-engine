.include "asm/include/battle_commands.inc"

.data

_000:
    CheckAbility CHECK_OPCODE_HAVE, BATTLER_CATEGORY_DEFENDER, ABILITY_MULTITYPE, _037
    CompareMonDataToValue OPCODE_NEQ, BATTLER_CATEGORY_DEFENDER, BMON_DATA_TYPE_1, TYPE_WATER, _016
    CompareMonDataToValue OPCODE_EQU, BATTLER_CATEGORY_DEFENDER, BMON_DATA_TYPE_2, TYPE_WATER, _037

_016:
    UpdateMonData OPCODE_SET, BATTLER_CATEGORY_DEFENDER, BMON_DATA_TYPE_1, TYPE_WATER
    UpdateMonData OPCODE_SET, BATTLER_CATEGORY_DEFENDER, BMON_DATA_TYPE_2, TYPE_WATER
    Call BATTLE_SUBSCRIPT_ATTACK_MESSAGE_AND_ANIMATION
    // {0} transformed into the Water type!
    PrintMessage 1330, TAG_NICKNAME_ABILITY, BATTLER_CATEGORY_MSG_TEMP, BATTLER_CATEGORY_MSG_BATTLER_TEMP
    Wait 
    WaitButtonABTime 30
    End 

_037:
    UpdateVar OPCODE_FLAG_ON, BSCRIPT_VAR_MOVE_STATUS_FLAGS, MOVE_STATUS_FAILED
    End 
