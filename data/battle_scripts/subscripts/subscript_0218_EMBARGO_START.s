.include "asm/include/battle_commands.inc"

.data

_000:
    CompareVarToValue OPCODE_FLAG_SET, BSCRIPT_VAR_MOVE_STATUS_FLAGS, MOVE_STATUS_SEMI_INVULNERABLE|MOVE_STATUS_MISSED, _057
    CheckSubstitute BATTLER_CATEGORY_DEFENDER, _057
    CompareMonDataToValue OPCODE_EQU, BATTLER_CATEGORY_DEFENDER, BMON_DATA_ABILITY, ABILITY_MULTITYPE, _057
    CompareMonDataToValue OPCODE_NEQ, BATTLER_CATEGORY_DEFENDER, BMON_DATA_EMBARGO_TURNS, 0, _057
    CompareMonDataToValue OPCODE_EQU, BATTLER_CATEGORY_DEFENDER, BMON_DATA_HELD_ITEM, ITEM_GRISEOUS_ORB, _057
    CompareMonDataToValue OPCODE_NEQ, BATTLER_CATEGORY_DEFENDER, BMON_DATA_QUICK_CLAW_FLAG, 0, _057
    CompareMonDataToValue OPCODE_NEQ, BATTLER_CATEGORY_DEFENDER, BMON_DATA_CUSTAP_FLAG, 0, _057
    Call BATTLE_SUBSCRIPT_ATTACK_MESSAGE_AND_ANIMATION
    UpdateMonData OPCODE_FLAG_ON, BATTLER_CATEGORY_DEFENDER, BMON_DATA_MOVE_EFFECT, MOVE_EFFECT_FLAG_EMBARGO
    UpdateMonData OPCODE_SET, BATTLER_CATEGORY_DEFENDER, BMON_DATA_EMBARGO_TURNS, 5
    // {0} can’t use items anymore!
    PrintMessage 1135, TAG_NICKNAME, BATTLER_CATEGORY_DEFENDER
    Wait 
    WaitButtonABTime 30
    End 

_057:
    UpdateVar OPCODE_FLAG_ON, BSCRIPT_VAR_MOVE_STATUS_FLAGS, MOVE_STATUS_FAILED
    End 
