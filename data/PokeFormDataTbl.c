#include "../include/types.h"
#include "../include/config.h"
#include "../include/pokemon.h"
#include "../include/constants/species.h"


// new format is 32 u16's per species
const u16 UNUSED PokeFormDataTbl[][32] =
{
#ifdef MEGA_EVOLUTIONS
    [SPECIES_VENUSAUR] = {
        NEEDS_REVERSION | SPECIES_MEGA_VENUSAUR,
    },
    [SPECIES_CHARIZARD] = {
        NEEDS_REVERSION | SPECIES_MEGA_CHARIZARD_X,
        NEEDS_REVERSION | SPECIES_MEGA_CHARIZARD_Y,
    },
    [SPECIES_BLASTOISE] = {
        NEEDS_REVERSION | SPECIES_MEGA_BLASTOISE,
    },
    [SPECIES_BEEDRILL] = {
        NEEDS_REVERSION | SPECIES_MEGA_BEEDRILL,
    },
    [SPECIES_PIDGEOT] = {
        NEEDS_REVERSION | SPECIES_MEGA_PIDGEOT,
    },
    [SPECIES_ALAKAZAM] = {
        NEEDS_REVERSION | SPECIES_MEGA_ALAKAZAM,
    },
    [SPECIES_SLOWBRO] = {
        NEEDS_REVERSION | SPECIES_MEGA_SLOWBRO,
        SPECIES_SLOWBRO_GALARIAN,
    },
    [SPECIES_GENGAR] = {
        NEEDS_REVERSION | SPECIES_MEGA_GENGAR,
    },
    [SPECIES_KANGASKHAN] = {
        NEEDS_REVERSION | SPECIES_MEGA_KANGASKHAN,
    },
    [SPECIES_PINSIR] = {
        NEEDS_REVERSION | SPECIES_MEGA_PINSIR,
    },
    [SPECIES_GYARADOS] = {
        NEEDS_REVERSION | SPECIES_MEGA_GYARADOS,
    },
    [SPECIES_AERODACTYL] = {
        NEEDS_REVERSION | SPECIES_MEGA_AERODACTYL,
    },
    [SPECIES_MEWTWO] = {
        NEEDS_REVERSION | SPECIES_MEGA_MEWTWO_X,
        NEEDS_REVERSION | SPECIES_MEGA_MEWTWO_Y,
    },
    [SPECIES_AMPHAROS] = {
        NEEDS_REVERSION | SPECIES_MEGA_AMPHAROS,
    },
    [SPECIES_STEELIX] = {
        NEEDS_REVERSION | SPECIES_MEGA_STEELIX,
    },
    [SPECIES_SCIZOR] = {
        NEEDS_REVERSION | SPECIES_MEGA_SCIZOR,
    },
    [SPECIES_HERACROSS] = {
        NEEDS_REVERSION | SPECIES_MEGA_HERACROSS,
    },
    [SPECIES_HOUNDOOM] = {
        NEEDS_REVERSION | SPECIES_MEGA_HOUNDOOM,
    },
    [SPECIES_TYRANITAR] = {
        NEEDS_REVERSION | SPECIES_MEGA_TYRANITAR,
    },
    [SPECIES_SCEPTILE] = {
        NEEDS_REVERSION | SPECIES_MEGA_SCEPTILE,
    },
    [SPECIES_BLAZIKEN] = {
        NEEDS_REVERSION | SPECIES_MEGA_BLAZIKEN,
    },
    [SPECIES_SWAMPERT] = {
        NEEDS_REVERSION | SPECIES_MEGA_SWAMPERT,
    },
    [SPECIES_GARDEVOIR] = {
        NEEDS_REVERSION | SPECIES_MEGA_GARDEVOIR,
    },
    [SPECIES_SABLEYE] = {
        NEEDS_REVERSION | SPECIES_MEGA_SABLEYE,
    },
    [SPECIES_MAWILE] = {
        NEEDS_REVERSION | SPECIES_MEGA_MAWILE,
    },
    [SPECIES_AGGRON] = {
        NEEDS_REVERSION | SPECIES_MEGA_AGGRON,
    },
    [SPECIES_MEDICHAM] = {
        NEEDS_REVERSION | SPECIES_MEGA_MEDICHAM,
    },
    [SPECIES_MANECTRIC] = {
        NEEDS_REVERSION | SPECIES_MEGA_MANECTRIC,
    },
    [SPECIES_SHARPEDO] = {
        NEEDS_REVERSION | SPECIES_MEGA_SHARPEDO,
    },
    [SPECIES_CAMERUPT] = {
        NEEDS_REVERSION | SPECIES_MEGA_CAMERUPT,
    },
    [SPECIES_ALTARIA] = {
        NEEDS_REVERSION | SPECIES_MEGA_ALTARIA,
    },
    [SPECIES_BANETTE] = {
        NEEDS_REVERSION | SPECIES_MEGA_BANETTE,
    },
    [SPECIES_ABSOL] = {
        NEEDS_REVERSION | SPECIES_MEGA_ABSOL,
    },
    [SPECIES_GLALIE] = {
        NEEDS_REVERSION | SPECIES_MEGA_GLALIE,
    },
    [SPECIES_SALAMENCE] = {
        NEEDS_REVERSION | SPECIES_MEGA_SALAMENCE,
    },
    [SPECIES_METAGROSS] = {
        NEEDS_REVERSION | SPECIES_MEGA_METAGROSS,
    },
    [SPECIES_LATIAS] = {
        NEEDS_REVERSION | SPECIES_MEGA_LATIAS,
    },
    [SPECIES_LATIOS] = {
        NEEDS_REVERSION | SPECIES_MEGA_LATIOS,
    },
    [SPECIES_RAYQUAZA] = {
        NEEDS_REVERSION | SPECIES_MEGA_RAYQUAZA,
    },
    [SPECIES_LOPUNNY] = {
        NEEDS_REVERSION | SPECIES_MEGA_LOPUNNY,
    },
    [SPECIES_GARCHOMP] = {
        NEEDS_REVERSION | SPECIES_MEGA_GARCHOMP,
    },
    [SPECIES_LUCARIO] = {
        NEEDS_REVERSION | SPECIES_MEGA_LUCARIO,
    },
    [SPECIES_ABOMASNOW] = {
        NEEDS_REVERSION | SPECIES_MEGA_ABOMASNOW,
    },
    [SPECIES_GALLADE] = {
        NEEDS_REVERSION | SPECIES_MEGA_GALLADE,
    },
    [SPECIES_AUDINO] = {
        NEEDS_REVERSION | SPECIES_MEGA_AUDINO,
    },
    [SPECIES_DIANCIE] = {
        NEEDS_REVERSION | SPECIES_MEGA_DIANCIE,
    },
#endif // MEGA_EVOLUTIONS

#ifdef PRIMAL_REVERSION
    [SPECIES_KYOGRE] = {
        NEEDS_REVERSION | SPECIES_KYOGRE_PRIMAL,
    },
    [SPECIES_GROUDON] = {
        NEEDS_REVERSION | SPECIES_GROUDON_PRIMAL,
    },
#endif // PRIMAL_REVERSION

    /**alolan forms**/
    [SPECIES_RATTATA] = {
        SPECIES_RATTATA_ALOLAN,
    },
    [SPECIES_RATICATE] = {
        SPECIES_RATICATE_ALOLAN,
        SPECIES_RATICATE_ALOLAN_LARGE,
    },
    [SPECIES_RAICHU] = {
        SPECIES_RAICHU_ALOLAN,
    },
    [SPECIES_SANDSHREW] = {
        SPECIES_SANDSHREW_ALOLAN,
    },
    [SPECIES_SANDSLASH] = {
        SPECIES_SANDSLASH_ALOLAN,
    },
    [SPECIES_VULPIX] = {
        SPECIES_VULPIX_ALOLAN,
    },
    [SPECIES_NINETALES] = {
        SPECIES_NINETALES_ALOLAN,
    },
    [SPECIES_DIGLETT] = {
        SPECIES_DIGLETT_ALOLAN,
    },
    [SPECIES_DUGTRIO] = {
        SPECIES_DUGTRIO_ALOLAN,
    },
    [SPECIES_MEOWTH] = {
        SPECIES_MEOWTH_ALOLAN,
        SPECIES_MEOWTH_GALARIAN,
    },
    [SPECIES_PERSIAN] = {
        SPECIES_PERSIAN_ALOLAN,
    },
    [SPECIES_GEODUDE] = {
        SPECIES_GEODUDE_ALOLAN,
    },
    [SPECIES_GRAVELER] = {
        SPECIES_GRAVELER_ALOLAN,
    },
    [SPECIES_GOLEM] = {
        SPECIES_GOLEM_ALOLAN,
    },
    [SPECIES_GRIMER] = {
        SPECIES_GRIMER_ALOLAN,
    },
    [SPECIES_MUK] = {
        SPECIES_MUK_ALOLAN,
    },
    [SPECIES_EXEGGUTOR] = {
        SPECIES_EXEGGUTOR_ALOLAN,
    },
    [SPECIES_MAROWAK] = {
        SPECIES_MAROWAK_ALOLAN,
        SPECIES_MAROWAK_ALOLAN_LARGE,
    },

    /**totems**/
    [SPECIES_GUMSHOOS] = {
        SPECIES_GUMSHOOS_LARGE,
    },
    [SPECIES_VIKAVOLT] = {
        SPECIES_VIKAVOLT_LARGE,
    },
    [SPECIES_RIBOMBEE] = {
        SPECIES_RIBOMBEE_LARGE,
    },
    [SPECIES_ARAQUANID] = {
        SPECIES_ARAQUANID_LARGE,
    },
    [SPECIES_LURANTIS] = {
        SPECIES_LURANTIS_LARGE,
    },
    [SPECIES_SALAZZLE] = {
        SPECIES_SALAZZLE_LARGE,
    },
    [SPECIES_TOGEDEMARU] = {
        SPECIES_TOGEDEMARU_LARGE,
    },
    [SPECIES_KOMMO_O] = {
        SPECIES_KOMMO_O_LARGE,
    },

    /**galarian forms**/
    [SPECIES_PONYTA] = {
        SPECIES_PONYTA_GALARIAN,
    },
    [SPECIES_RAPIDASH] = {
        SPECIES_RAPIDASH_GALARIAN,
    },
    [SPECIES_SLOWPOKE] = {
        SPECIES_SLOWPOKE_GALARIAN,
    },
    [SPECIES_FARFETCHD] = {
        SPECIES_FARFETCHD_GALARIAN,
    },
    [SPECIES_WEEZING] = {
        SPECIES_WEEZING_GALARIAN,
    },
    [SPECIES_MR_MIME] = {
        SPECIES_MR_MIME_GALARIAN,
    },
    [SPECIES_ARTICUNO] = {
        SPECIES_ARTICUNO_GALARIAN,
    },
    [SPECIES_ZAPDOS] = {
        SPECIES_ZAPDOS_GALARIAN,
    },
    [SPECIES_MOLTRES] = {
        SPECIES_MOLTRES_GALARIAN,
    },
    [SPECIES_SLOWKING] = {
        SPECIES_SLOWKING_GALARIAN,
    },
    [SPECIES_CORSOLA] = {
        SPECIES_CORSOLA_GALARIAN,
    },
    [SPECIES_ZIGZAGOON] = {
        SPECIES_ZIGZAGOON_GALARIAN,
    },
    [SPECIES_LINOONE] = {
        SPECIES_LINOONE_GALARIAN,
    },
    [SPECIES_DARUMAKA] = {
        SPECIES_DARUMAKA_GALARIAN,
    },
    [SPECIES_DARMANITAN] = {
        SPECIES_DARMANITAN_GALARIAN,
        NEEDS_REVERSION | SPECIES_DARMANITAN_ZEN_MODE,
        NEEDS_REVERSION | SPECIES_DARMANITAN_ZEN_MODE_GALARIAN,
    },
    [SPECIES_YAMASK] = {
        SPECIES_YAMASK_GALARIAN,
    },
    [SPECIES_STUNFISK] = {
        SPECIES_STUNFISK_GALARIAN,
    },

    /**cosmetic forms**/
    [SPECIES_PIKACHU] = {
        SPECIES_PIKACHU_COSPLAY,
        SPECIES_PIKACHU_ROCK_STAR,
        SPECIES_PIKACHU_BELLE,
        SPECIES_PIKACHU_POP_STAR,
        SPECIES_PIKACHU_PH_D,
        SPECIES_PIKACHU_LIBRE,
        SPECIES_PIKACHU_ORIGINAL_CAP,
        SPECIES_PIKACHU_HOENN_CAP,
        SPECIES_PIKACHU_SINNOH_CAP,
        SPECIES_PIKACHU_UNOVA_CAP,
        SPECIES_PIKACHU_KALOS_CAP,
        SPECIES_PIKACHU_ALOLA_CAP,
        SPECIES_PIKACHU_PARTNER_CAP,
        SPECIES_PIKACHU_WORLD_CAP,
        SPECIES_PIKACHU_PARTNER,
    },
    [SPECIES_EEVEE] = {
        SPECIES_EEVEE_PARTNER,
    },
    [SPECIES_BASCULIN] = {
        SPECIES_BASCULIN_BLUE_STRIPED,
        SPECIES_BASCULIN_WHITE_STRIPED,
    },
    [SPECIES_DEERLING] = {
        SPECIES_DEERLING_SUMMER,
        SPECIES_DEERLING_AUTUMN,
        SPECIES_DEERLING_WINTER,
    },
    [SPECIES_SAWSBUCK] = {
        SPECIES_SAWSBUCK_SUMMER,
        SPECIES_SAWSBUCK_AUTUMN,
        SPECIES_SAWSBUCK_WINTER,
    },
    [SPECIES_TORNADUS] = {
        SPECIES_TORNADUS_THERIAN,
    },
    [SPECIES_THUNDURUS] = {
        SPECIES_THUNDURUS_THERIAN,
    },
    [SPECIES_LANDORUS] = {
        SPECIES_LANDORUS_THERIAN,
    },
    [SPECIES_KYUREM] = {
        SPECIES_KYUREM_WHITE,
        SPECIES_KYUREM_BLACK,
    },
    [SPECIES_KELDEO] = {
        SPECIES_KELDEO_RESOLUTE,
    },
    [SPECIES_GENESECT] = {
        SPECIES_GENESECT_DOUSE_DRIVE,
        SPECIES_GENESECT_SHOCK_DRIVE,
        SPECIES_GENESECT_BURN_DRIVE,
        SPECIES_GENESECT_CHILL_DRIVE,
    },
    [SPECIES_GRENINJA] = {
        SPECIES_GRENINJA_BATTLE_BOND,
        NEEDS_REVERSION | SPECIES_GRENINJA_ASH,
    },
    [SPECIES_VIVILLON] = {
        SPECIES_VIVILLON_POLAR,
        SPECIES_VIVILLON_TUNDRA,
        SPECIES_VIVILLON_CONTINENTAL,
        SPECIES_VIVILLON_GARDEN,
        SPECIES_VIVILLON_ELEGANT,
        SPECIES_VIVILLON_MEADOW,
        SPECIES_VIVILLON_MODERN,
        SPECIES_VIVILLON_MARINE,
        SPECIES_VIVILLON_ARCHIPELAGO,
        SPECIES_VIVILLON_HIGH_PLAINS,
        SPECIES_VIVILLON_SANDSTORM,
        SPECIES_VIVILLON_RIVER,
        SPECIES_VIVILLON_MONSOON,
        SPECIES_VIVILLON_SAVANNA,
        SPECIES_VIVILLON_SUN,
        SPECIES_VIVILLON_OCEAN,
        SPECIES_VIVILLON_JUNGLE,
        SPECIES_VIVILLON_FANCY,
        SPECIES_VIVILLON_POKE_BALL,
    },
    [SPECIES_FLABEBE] = {
        SPECIES_FLABEBE_YELLOW_FLOWER,
        SPECIES_FLABEBE_ORANGE_FLOWER,
        SPECIES_FLABEBE_BLUE_FLOWER,
        SPECIES_FLABEBE_WHITE_FLOWER,
    },
    [SPECIES_FLOETTE] = {
        SPECIES_FLOETTE_YELLOW_FLOWER,
        SPECIES_FLOETTE_ORANGE_FLOWER,
        SPECIES_FLOETTE_BLUE_FLOWER,
        SPECIES_FLOETTE_WHITE_FLOWER,
        SPECIES_FLOETTE_ETERNAL_FLOWER,
    },
    [SPECIES_FLORGES] = {
        SPECIES_FLORGES_YELLOW_FLOWER,
        SPECIES_FLORGES_ORANGE_FLOWER,
        SPECIES_FLORGES_BLUE_FLOWER,
        SPECIES_FLORGES_WHITE_FLOWER,
    },
    [SPECIES_FURFROU] = {
        SPECIES_FURFROU_HEART,
        SPECIES_FURFROU_STAR,
        SPECIES_FURFROU_DIAMOND,
        SPECIES_FURFROU_DEBUTANTE,
        SPECIES_FURFROU_MATRON,
        SPECIES_FURFROU_DANDY,
        SPECIES_FURFROU_LA_REINE,
        SPECIES_FURFROU_KABUKI,
        SPECIES_FURFROU_PHARAOH,
    },
    [SPECIES_PUMPKABOO] = {
        SPECIES_PUMPKABOO_SMALL,
        SPECIES_PUMPKABOO_LARGE,
        SPECIES_PUMPKABOO_SUPER,
    },
    [SPECIES_GOURGEIST] = {
        SPECIES_GOURGEIST_SMALL,
        SPECIES_GOURGEIST_LARGE,
        SPECIES_GOURGEIST_SUPER,
    },
    [SPECIES_HOOPA] = {
        SPECIES_HOOPA_UNBOUND,
    },
    [SPECIES_ORICORIO] = {
        SPECIES_ORICORIO_POM_POM,
        SPECIES_ORICORIO_PAU,
        SPECIES_ORICORIO_SENSU,
    },
    [SPECIES_ROCKRUFF] = {
        SPECIES_ROCKRUFF_OWN_TEMPO,
    },
    [SPECIES_LYCANROC] = {
        SPECIES_LYCANROC_MIDNIGHT,
        SPECIES_LYCANROC_DUSK,
    },
    [SPECIES_MAGEARNA] = {
        SPECIES_MAGEARNA_ORIGINAL,
    },
    [SPECIES_TOXTRICITY] = {
        SPECIES_TOXTRICITY_LOW_KEY,
    },
    [SPECIES_SINISTEA] = {
        SPECIES_SINISTEA_ANTIQUE,
    },
    [SPECIES_POLTEAGEIST] = {
        SPECIES_POLTEAGEIST_ANTIQUE,
    },
    [SPECIES_ALCREMIE] = {
        SPECIES_ALCREMIE_BERRY_SWEET,
        SPECIES_ALCREMIE_LOVE_SWEET,
        SPECIES_ALCREMIE_STAR_SWEET,
        SPECIES_ALCREMIE_CLOVER_SWEET,
        SPECIES_ALCREMIE_FLOWER_SWEET,
        SPECIES_ALCREMIE_RIBBON_SWEET,
    },
    [SPECIES_URSHIFU] = {
        SPECIES_URSHIFU_RAPID_STRIKE,
    },
    [SPECIES_ZARUDE] = {
        SPECIES_ZARUDE_DADA,
    },
    [SPECIES_CALYREX] = {
        SPECIES_CALYREX_ICE_RIDER,
        SPECIES_CALYREX_SHADOW_RIDER,
    },

    /**Battle Forms**/
    [SPECIES_CASTFORM] = {
        NEEDS_REVERSION | SPECIES_CASTFORM_SUNNY,
        NEEDS_REVERSION | SPECIES_CASTFORM_RAINY,
        NEEDS_REVERSION | SPECIES_CASTFORM_SNOWY,
    },
    [SPECIES_CHERRIM] = {
        NEEDS_REVERSION | SPECIES_CHERRIM_SUNSHINE,
    },
    [SPECIES_SHELLOS] = {
        SPECIES_SHELLOS_EAST_SEA,
    },
    [SPECIES_GASTRODON] = {
        SPECIES_GASTRODON_EAST_SEA,
    },
    [SPECIES_DIALGA] = {
        SPECIES_DIALGA_ORIGIN,
    },
    [SPECIES_PALKIA] = {
        SPECIES_PALKIA_ORIGIN,
    },
    [SPECIES_MELOETTA] = {
        NEEDS_REVERSION | SPECIES_MELOETTA_PIROUETTE,
    },
    [SPECIES_AEGISLASH] = {
        NEEDS_REVERSION | SPECIES_AEGISLASH_BLADE,
    },
    [SPECIES_XERNEAS] = {
        NEEDS_REVERSION | SPECIES_XERNEAS_ACTIVE,
    },
    [SPECIES_ZYGARDE] = {
        SPECIES_ZYGARDE_10,
        SPECIES_ZYGARDE_10_POWER_CONSTRUCT,
        SPECIES_ZYGARDE_50_POWER_CONSTRUCT,
        NEEDS_REVERSION | SPECIES_ZYGARDE_10_COMPLETE,
        NEEDS_REVERSION | SPECIES_ZYGARDE_50_COMPLETE,
    },
    [SPECIES_WISHIWASHI] = {
        NEEDS_REVERSION | SPECIES_WISHIWASHI_SCHOOL,
    },
    [SPECIES_MINIOR] = {
        SPECIES_MINIOR_METEOR_ORANGE,
        SPECIES_MINIOR_METEOR_YELLOW,
        SPECIES_MINIOR_METEOR_GREEN,
        SPECIES_MINIOR_METEOR_BLUE,
        SPECIES_MINIOR_METEOR_INDIGO,
        SPECIES_MINIOR_METEOR_VIOLET,
        NEEDS_REVERSION | SPECIES_MINIOR_CORE_RED,
        NEEDS_REVERSION | SPECIES_MINIOR_CORE_ORANGE,
        NEEDS_REVERSION | SPECIES_MINIOR_CORE_YELLOW,
        NEEDS_REVERSION | SPECIES_MINIOR_CORE_GREEN,
        NEEDS_REVERSION | SPECIES_MINIOR_CORE_BLUE,
        NEEDS_REVERSION | SPECIES_MINIOR_CORE_INDIGO,
        NEEDS_REVERSION | SPECIES_MINIOR_CORE_VIOLET,
    },
    [SPECIES_MIMIKYU] = {
        NEEDS_REVERSION | SPECIES_MIMIKYU_BUSTED,
        SPECIES_MIMIKYU_LARGE,
        NEEDS_REVERSION | SPECIES_MIMIKYU_BUSTED_LARGE,
    },
    [SPECIES_NECROZMA] = {
        SPECIES_NECROZMA_DUSK_MANE,
        SPECIES_NECROZMA_DAWN_WINGS,
        NEEDS_REVERSION | SPECIES_NECROZMA_ULTRA_DUSK_MANE,
        NEEDS_REVERSION | SPECIES_NECROZMA_ULTRA_DAWN_WINGS,
    },
    [SPECIES_CRAMORANT] = {
        NEEDS_REVERSION | SPECIES_CRAMORANT_GULPING,
        NEEDS_REVERSION | SPECIES_CRAMORANT_GORGING,
    },
    [SPECIES_EISCUE] = {
        NEEDS_REVERSION | SPECIES_EISCUE_NOICE_FACE,
    },
    [SPECIES_MORPEKO] = {
        NEEDS_REVERSION | SPECIES_MORPEKO_HANGRY,
    },
    [SPECIES_ZACIAN] = {
        NEEDS_REVERSION | SPECIES_ZACIAN_CROWNED,
    },
    [SPECIES_ZAMAZENTA] = {
        NEEDS_REVERSION | SPECIES_ZAMAZENTA_CROWNED,
    },
    [SPECIES_ETERNATUS] = {
        NEEDS_REVERSION | SPECIES_ETERNATUS_ETERNAMAX,
    },
    [SPECIES_ENAMORUS] = {
        SPECIES_ENAMORUS_THERIAN,
    },

    /**hisuian forms**/
    [SPECIES_GROWLITHE] = {
        SPECIES_GROWLITHE_HISUIAN,
    },
    [SPECIES_ARCANINE] = {
        SPECIES_ARCANINE_HISUIAN,
        NEEDS_REVERSION | SPECIES_ARCANINE_LORD,
    },
    [SPECIES_VOLTORB] = {
        SPECIES_VOLTORB_HISUIAN,
    },
    [SPECIES_ELECTRODE] = {
        SPECIES_ELECTRODE_HISUIAN,
        NEEDS_REVERSION | SPECIES_ELECTRODE_LORD,
    },
    [SPECIES_TYPHLOSION] = {
        SPECIES_TYPHLOSION_HISUIAN,
    },
    [SPECIES_QWILFISH] = {
        SPECIES_QWILFISH_HISUIAN,
    },
    [SPECIES_SNEASEL] = {
        SPECIES_SNEASEL_HISUIAN,
    },
    [SPECIES_SAMUROTT] = {
        SPECIES_SAMUROTT_HISUIAN,
    },
    [SPECIES_LILLIGANT] = {
        SPECIES_LILLIGANT_HISUIAN,
        NEEDS_REVERSION | SPECIES_LILLIGANT_LADY,
    },
    [SPECIES_ZORUA] = {
        SPECIES_ZORUA_HISUIAN,
    },
    [SPECIES_ZOROARK] = {
        SPECIES_ZOROARK_HISUIAN,
    },
    [SPECIES_BRAVIARY] = {
        SPECIES_BRAVIARY_HISUIAN,
    },
    [SPECIES_SLIGGOO] = {
        SPECIES_SLIGGOO_HISUIAN,
    },
    [SPECIES_GOODRA] = {
        SPECIES_GOODRA_HISUIAN,
    },
    [SPECIES_AVALUGG] = {
        SPECIES_AVALUGG_HISUIAN,
        NEEDS_REVERSION | SPECIES_AVALUGG_LORD,
    },
    [SPECIES_DECIDUEYE] = {
        SPECIES_DECIDUEYE_HISUIAN,
    },

    /**noble pokemon**/
    [SPECIES_KLEAVOR] = {
        NEEDS_REVERSION | SPECIES_KLEAVOR_LORD,
    },

    /**significant gender differences**/
    [SPECIES_UNFEZANT] = {
        SPECIES_UNFEZANT_FEMALE,
    },
    [SPECIES_FRILLISH] = {
        SPECIES_FRILLISH_FEMALE,
    },
    [SPECIES_JELLICENT] = {
        SPECIES_JELLICENT_FEMALE
    },
    [SPECIES_PYROAR] = {
        SPECIES_PYROAR_FEMALE
    },
    [SPECIES_MEOWSTIC] = {
        SPECIES_MEOWSTIC_FEMALE,
    },
    [SPECIES_INDEEDEE] = {
        SPECIES_INDEEDEE_FEMALE,
    },
    [SPECIES_BASCULEGION] = {
        SPECIES_BASCULEGION_FEMALE,
    },
    [SPECIES_MAUSHOLD] = {
        SPECIES_MAUSHOLD_FAMILY_OF_THREE,
    },

	/** paldean forms **/
    [SPECIES_SQUAWKABILLY] = {
        SPECIES_SQUAWKABILLY_BLUE_PLUMAGE,
        SPECIES_SQUAWKABILLY_YELLOW_PLUMAGE,
        SPECIES_SQUAWKABILLY_WHITE_PLUMAGE,
    },
    [SPECIES_PALAFIN] = {
        NEEDS_REVERSION | SPECIES_PALAFIN_HERO,
    },
    [SPECIES_TATSUGIRI] = {
        SPECIES_TATSUGIRI_DROOPY,
        SPECIES_TATSUGIRI_STRETCHY,
    },
    [SPECIES_DUDUNSPARCE] = {
        SPECIES_DUDUNSPARCE_THREE_SEGMENT,
    },
    [SPECIES_GIMMIGHOUL] = {
        SPECIES_GIMMIGHOUL_ROAMING,
    },
    [SPECIES_WOOPER] = {
        SPECIES_WOOPER_PALDEAN,
    },
    [SPECIES_TAUROS] = {
        SPECIES_TAUROS_COMBAT,
        SPECIES_TAUROS_BLAZE,
        SPECIES_TAUROS_AQUA,
    },
    [SPECIES_OINKOLOGNE] = {
        SPECIES_OINKOLOGNE_FEMALE,
    },
    [SPECIES_REVAVROOM] = { // not technically forms, vanilla mechanics users beware
        SPECIES_REVAVROOM_SEGIN,
        SPECIES_REVAVROOM_SCHEDAR,
        SPECIES_REVAVROOM_NAVI,
        SPECIES_REVAVROOM_RUCHBAH,
        SPECIES_REVAVROOM_CAPH,
    },
    [SPECIES_KORAIDON] = {
        SPECIES_KORAIDON_LIMITED_BUILD,
        SPECIES_KORAIDON_SPRINTING_BUILD,
        SPECIES_KORAIDON_SWIMMING_BUILD,
        SPECIES_KORAIDON_GLIDING_BUILD,
    },
    [SPECIES_MIRAIDON] = {
        SPECIES_MIRAIDON_LOW_POWER_MODE,
        SPECIES_MIRAIDON_DRIVE_MODE,
        SPECIES_MIRAIDON_AQUATIC_MODE,
        SPECIES_MIRAIDON_GLIDE_MODE,
    },
    [SPECIES_POLTCHAGEIST] = {
        SPECIES_POLTCHAGEIST_MASTERPIECE,
    },
    [SPECIES_SINISTCHA] = {
        SPECIES_SINISTCHA_MASTERPIECE,
    },
    [SPECIES_OGERPON] = {
        SPECIES_OGERPON_WELLSPRING_MASK,
        SPECIES_OGERPON_HEARTHFLAME_MASK,
        SPECIES_OGERPON_CORNERSTONE_MASK,
        NEEDS_REVERSION | SPECIES_OGERPON_TEAL_MASK_TERASTAL,
        NEEDS_REVERSION | SPECIES_OGERPON_WELLSPRING_MASK_TERASTAL,
        NEEDS_REVERSION | SPECIES_OGERPON_HEARTHFLAME_MASK_TERASTAL,
        NEEDS_REVERSION | SPECIES_OGERPON_CORNERSTONE_MASK_TERASTAL,
    },
    [SPECIES_URSALUNA] = {
        SPECIES_URSALUNA_BLOODMOON,
    },
    [SPECIES_TERAPAGOS] = {
        NEEDS_REVERSION | SPECIES_TERAPAGOS_TERASTAL,
        NEEDS_REVERSION | SPECIES_TERAPAGOS_STELLAR,
    },
};
