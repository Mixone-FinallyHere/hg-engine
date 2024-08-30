.include "asm/include/battle_commands.inc"

.data

_000:
    PrintMessage 1463, TAG_NICKNAME_ITEM, BATTLER_CATEGORY_ATTACKER, BATTLER_CATEGORY_ATTACKER
    Wait 
    WaitButtonABTime 30
    RemoveItem BATTLER_CATEGORY_ATTACKER
    End