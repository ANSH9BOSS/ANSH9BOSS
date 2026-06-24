package com.ansh9boss.analyzer

object Config {
    const val VERSION = "1.0.0"
    const val DEFAULT_API_URL = "https://ansh9boss.vercel.app"

    val knownCheats = listOf(
        "wurst", "meteor", "sigma", "impact", "aristois", "future", "liquidbounce",
        "wolfram", "inertia", "ares", "sentry", "entropy", "reflex", "bleach",
        "ancientaura", "killaura", "huzuni", "nodus", "vape", "badlion", "mathax",
        "kamiblue", "kami", "salhack", "rusherhack"
    )

    val knownPackages = listOf(
        "meteorclient", "wurst", "sigma", "future", "liquidbounce", "mathax",
        "ares", "wolfram", "kamiblue", "salhack", "rusherhack", "aristois", "huzuni", "vape"
    )

    val cheatStrings = listOf(
        "aimbot", "killaura", "esp", "wallhack", "xray", "freecam", "fly", "speed",
        "nofall", "scaffold", "tower", "triggerbot", "autoclick", "baritone", "pathfind",
        "autototem", "fastplace", "reach", "criticals", "antiknockback", "timer", "nuker",
        "jesus", "spider", "bhop", "strafe", "automine", "autofish", "autoeat", "steal",
        "grief", "exploit", "inject", "hook", "bypass", "anticheat", "spoof", "packet", "cheatengine"
    )
}
