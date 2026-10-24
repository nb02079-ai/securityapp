package securityapp.eval

import java.io.File

/** 재생할 메시지 하나. isUser가 null이면 "나"가 정해지지 않은 대화(AI-Hub 일반 대화) */
data class ReplayMessage(
    val seq: Int,
    val room: String,
    val sender: String,
    val isUser: Boolean?,
    val text: String,
)

/** 재생할 대화 하나 (사기 재구성, 개발용 합성, AI-Hub 일반 대화 모두 같은 모양으로 읽음) */
data class Conversation(
    val id: String,
    /** "scam" 또는 "normal" */
    val label: String,
    /** 사기 유형·묶음 등 보고용 설명 (원문 아님) */
    val note: String,
    /** 다자간 대화인지 (AI-Hub의 speaker_type). 방 이름으로 알 수 없을 때 씀 */
    val multiParty: Boolean?,
    val messages: List<ReplayMessage>,
) {
    val isScam: Boolean get() = label == "scam"
    /** "나"가 정해지지 않은 대화 → 화자마다 한 번씩 "나"로 놓고 돌림 */
    val userUnknown: Boolean get() = messages.any { it.isUser == null }
    val senders: List<String> get() = messages.map { it.sender }.distinct()
}

/** 사례마다 정답 금전 지점 (data/eval/scam/labels/final_points.csv) */
data class MoneyPoints(
    val caseId: String,
    val firstSuggest: Int,
    val firstIntentBefore: Int,
    val firstTransferBefore: Int,
    val transferSeen: Boolean,
) {
    /** 결심 전 경고율의 마감점 = min(첫 송금 의사 직전, 첫 송금 직전) */
    val intentDeadline: Int get() = minOf(firstIntentBefore, firstTransferBefore)
}

object Loader {
    /** 폴더(하위 폴더 포함)의 .jsonl을 모두 읽음. 파일 이름 순서 */
    fun loadDir(dir: File, defaultLabel: String? = null): List<Conversation> {
        require(dir.isDirectory) { "폴더가 없습니다: $dir" }
        return dir.walkTopDown().filter { it.isFile && it.name.endsWith(".jsonl") }
            .sortedBy { it.path }
            .map { loadFile(it, defaultLabel) }
            .toList()
    }

    fun loadFile(file: File, defaultLabel: String? = null): Conversation =
        parse(file.readLines(Charsets.UTF_8), file.nameWithoutExtension, defaultLabel)

    fun parse(lines: List<String>, fallbackId: String, defaultLabel: String? = null): Conversation {
        val rows = lines.filter { it.isNotBlank() }.map { Json.obj(it) }
        require(rows.isNotEmpty()) { "빈 파일: $fallbackId" }
        val meta = rows.first().takeIf { it["type"] == "meta" || it["seq"] == null } ?: emptyMap()
        val msgRows = rows.filter { it !== meta }
        val id = (meta["case_id"] ?: meta["candidate_id"] ?: fallbackId).toString()
        val label = (meta["label"] ?: meta["kind"] ?: defaultLabel)?.toString()
            ?: throw IllegalArgumentException("$id: label(scam/normal)을 알 수 없습니다")
        require(label == "scam" || label == "normal") { "$id: label은 scam 또는 normal이어야 합니다 ($label)" }
        val note = (meta["scam_type"] ?: meta["bucket"] ?: meta["topic"] ?: "").toString()
        val multi = (meta["speaker_type"] as? String)?.let { it.contains("다자") }
        val messages = msgRows.mapIndexed { idx, m ->
            ReplayMessage(
                seq = (m["seq"] as? Long)?.toInt() ?: (idx + 1),
                room = (m["room"] as? String) ?: id,
                sender = m["sender"]?.toString() ?: throw IllegalArgumentException("$id: sender 없음"),
                isUser = m["is_user"] as? Boolean,
                text = m["text"]?.toString() ?: "",
            )
        }
        require(messages.map { it.seq }.zipWithNext().all { (a, b) -> a < b }) { "$id: seq가 커지는 순서가 아닙니다" }
        return Conversation(id, label, note, multi, messages)
    }

    fun loadPoints(file: File): Map<String, MoneyPoints> {
        val lines = file.readLines(Charsets.UTF_8).filter { it.isNotBlank() }
        val head = lines.first().removePrefix("﻿").split(",")
        fun col(name: String) = head.indexOf(name).also { require(it >= 0) { "${file.name}: '$name' 칸이 없습니다" } }
        val cId = col("case_id"); val cS = col("first_suggest"); val cI = col("first_intent_before")
        val cT = col("first_transfer_before"); val cSeen = col("transfer_seen")
        return lines.drop(1).map { it.split(",") }.associate { r ->
            r[cId] to MoneyPoints(r[cId], r[cS].toInt(), r[cI].toInt(), r[cT].toInt(), r[cSeen].trim() == "Y")
        }
    }

    /** 최종 라벨의 메시지별 신호 (case_id, seq) → 신호 코드 집합 */
    fun loadSignalLabels(file: File): Map<Pair<String, Int>, Set<String>> {
        val lines = file.readLines(Charsets.UTF_8).filter { it.isNotBlank() }
        val head = lines.first().removePrefix("﻿").split(",")
        val cId = head.indexOf("case_id"); val cSeq = head.indexOf("seq"); val cSig = head.indexOf("signals")
        require(cId >= 0 && cSeq >= 0 && cSig >= 0) { "${file.name}: case_id·seq·signals 칸이 필요합니다" }
        return lines.drop(1).map { it.split(",") }.associate { r ->
            (r[cId] to r[cSeq].toInt()) to r[cSig].split(";").map { it.trim() }.filter { it.isNotEmpty() }.toSet()
        }
    }

    /**
     * 방 이름으로 단체방 여부를 정함 (알림이 알려 주는 값을 흉내 냄). 모르면 null → 엔진이 보낸 사람 수로 추정.
     * 평가 세트: group / group_telegram / dm / dm_* / sms, 개발 세트: 단체방(…) / 1:1(…) / 문자 / …채팅 / …채널
     */
    fun groupFlag(room: String, multiParty: Boolean?): Boolean? {
        val r = room.lowercase()
        return when {
            r.startsWith("group") || "단체" in r || "오픈채팅" in r -> true
            r.startsWith("dm") || r.startsWith("sms") || r.startsWith("1:1") || r.startsWith("문자") ||
                "채팅" in r || "채널" in r -> false
            else -> multiParty
        }
    }
}
