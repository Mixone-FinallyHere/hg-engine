#ifndef NUZLOCKE_H
#define NUZLOCKE_H

#include "types.h"

#include "battle.h"

void Nuzlocke_RegisterEncounter(void *bw);
BOOL Nuzlocke_ShouldBlockBall(struct BattleStruct *sp);

#endif
