package com.ansh9boss.analyzer

data class ModDetection(
    val file_name: String,
    val risk_level: String,
    val detection_layer: String,
    val matched_details: List<String>
)

data class ScanReport(
    val platform: String,
    val total_files: Int,
    val flagged_files: Int,
    val highest_risk: String,
    val detections: List<ModDetection>
)
