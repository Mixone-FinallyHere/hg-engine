#include "config.h"
#include "types.h"

#include "constants/battle_constants.h"
#include "constants/maps.h"

#include "battle.h"
#include "nuzlocke.h"
#include "pokemon.h"
#include "save.h"
#include "script.h"

#ifdef IMPLEMENT_HARDCODE_NUZLOCKE

// battle types that are never subject to the nuzlocke capture restriction, mirroring the
// existing guaranteed-capture exemptions (safari/pal park/tutorial) in CalculateBallShakesInternal
#define NUZLOCKE_EXEMPT_BATTLE_TYPES (BATTLE_TYPE_TRAINER | BATTLE_TYPE_SAFARI | BATTLE_TYPE_PAL_PARK | BATTLE_TYPE_TUTORIAL | BATTLE_TYPE_BUG_CONTEST | BATTLE_TYPE_TOTEM)

static BOOL RouteIsUsed(u32 mapId)
{
    struct SAVE_MISC_DATA *misc = Sav2_Misc_get(SaveBlock2_get());

    if (mapId >= MAP_ID_MAX) {
        return FALSE;
    }

    return (misc->nuzlockeRouteUsed[mapId / 8] >> (mapId % 8)) & 1;
}

static void SetRouteUsed(u32 mapId)
{
    struct SAVE_MISC_DATA *misc = Sav2_Misc_get(SaveBlock2_get());

    if (mapId >= MAP_ID_MAX) {
        return;
    }

    misc->nuzlockeRouteUsed[mapId / 8] |= (1 << (mapId % 8));
}

#endif // IMPLEMENT_HARDCODE_NUZLOCKE

/**
 *  @brief register a wild battle's encountered species against the current route, locking it
 *         if any of the wild mon(s) are a species not yet owned in the pokédex (dupes clause).
 *         must be called once bw is fully populated with the wild party (i.e. from ServerInit).
 *
 *  @param bw battle work structure
 */
void Nuzlocke_RegisterEncounter(void *bw)
{
#ifdef IMPLEMENT_HARDCODE_NUZLOCKE

    if (BattleTypeGet(bw) & NUZLOCKE_EXEMPT_BATTLE_TYPES) {
        return;
    }

    int enemyClients[2] = { BATTLER_ENEMY, BATTLER_ENEMY2 };

    for (int i = 0; i < (s32)NELEMS(enemyClients); i++) {
        int client_no = enemyClients[i];

        if (BattleWorkPokeCountGet(bw, client_no) == 0) {
            continue;
        }

        struct PartyPokemon *mon = BattleWorkPokemonParamGet(bw, client_no, 0);
        if (mon == NULL) {
            continue;
        }

        u16 species = GetMonData(mon, MON_DATA_SPECIES, NULL);

        if (!Battle_CheckIfHasCaughtMon(bw, species)) {
            SetRouteUsed(gFieldSysPtr->location->mapId);
        }
    }

#endif // IMPLEMENT_HARDCODE_NUZLOCKE
}

/**
 *  @brief determine whether poké balls should be unusable/guaranteed to fail against the
 *         current wild target because its route already had its one legal capture used
 *
 *  @param sp global battle structure
 *  @return TRUE if ball usage should be blocked
 */
BOOL Nuzlocke_ShouldBlockBall(struct BattleStruct *sp)
{
#ifdef IMPLEMENT_HARDCODE_NUZLOCKE

    if (BattleTypeGet(gBattleSystem) & NUZLOCKE_EXEMPT_BATTLE_TYPES) {
        return FALSE;
    }

    if (sp->battlemon[sp->defence_client].rare) { // shiny clause: always catchable
        return FALSE;
    }

    return RouteIsUsed(gFieldSysPtr->location->mapId);

#else

    return FALSE;

#endif // IMPLEMENT_HARDCODE_NUZLOCKE
}
