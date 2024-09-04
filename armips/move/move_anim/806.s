.nds
.thumb

.include "armips/include/animscriptcmd.s"

.include "asm/include/abilities.inc"
.include "asm/include/items.inc"
.include "asm/include/species.inc"
.include "asm/include/moves.inc"

.create "build/move/move_anim/0_806", 0

//grassy glide (combination of needle arm and vine whip)
a010_806:
    loadparticlefromspa 0, 320
    waitparticle
    loadparticlefromspa 1, 53
    waitparticle

    callfunction 52, 3, 3, 24, 258, "NaN", "NaN", "NaN", "NaN", "NaN", "NaN", "NaN"
    waitstate
    callfunction 52, 3, 3, -24, 258, "NaN", "NaN", "NaN", "NaN", "NaN", "NaN", "NaN"
    addparticle 0, 0, 4
    addparticle 0, 2, 4
    addparticle 0, 3, 4
    wait 2
    repeatse 1926, 117, 2, 8
    wait 40
    addparticle 1, 1, 4
    waitparticle

    unloadparticle 0
    waitstate
    end
    

.close
