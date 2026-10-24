package securityapp.eval

import securityapp.engine.Level
import java.io.File
import java.util.Locale

/**
 * 결과 파일 쓰기 (모두 UTF-8). 대화 원문은 어떤 파일에도 쓰지 않는다 — 사례 ID·메시지 번호·숫자만
 * (AI-Hub 약관, 설계 6장).
 */
object Report {
    private fun pct(n: Int, d: Int) = if (d == 0) "-" else "$n/$d (${(100.0 * n / d).let { String.format(Locale.ROOT, "%.0f", it) }}%)"
    private fun f2(x: Double?) = x?.let { String.format(Locale.ROOT, "%.3f", it) } ?: "-"
    private fun f1(x: Double?) = x?.let { String.format(Locale.ROOT, "%.1f", it) } ?: "-"
    private fun opt(x: Any?) = x?.toString() ?: "-"
    /** CSV 칸: 쉼표·따옴표·줄바꿈이 있으면 따옴표로 감쌈 */
    private fun cell(x: Any?): String {
        val t = x?.toString() ?: ""
        return if (t.any { it == ',' || it == '"' || it == '\n' }) "\"" + t.replace("\"", "\"\"") + "\"" else t
    }
    private fun row(vararg xs: Any?) = xs.joinToString(",") { cell(it) }
    private fun mode(includeUser: Boolean) = if (includeUser) "나 포함" else "상대만"

    fun write(
        out: File,
        title: String,
        inputs: List<String>,
        summaries: List<Summary>,
        signalScores: List<SignalScore>?,
    ) {
        out.mkdirs()
        File(out, "report.md").writeText(markdown(title, inputs, summaries, signalScores), Charsets.UTF_8)
        File(out, "cases.csv").writeText(casesCsv(summaries), Charsets.UTF_8)
        File(out, "normals.csv").writeText(normalsCsv(summaries), Charsets.UTF_8)
        if (signalScores != null) File(out, "signals.csv").writeText(signalsCsv(signalScores), Charsets.UTF_8)
    }

    fun markdown(title: String, inputs: List<String>, summaries: List<Summary>, signalScores: List<SignalScore>?): String =
        buildString {
            appendLine("# $title")
            appendLine()
            appendLine("- 입력: ${inputs.joinToString(", ")}")
            val first = summaries.first()
            appendLine("- 사기 ${first.scams.size}건 (금전 지점 라벨 ${first.labeledScams.size}건), 일반 ${first.normals.size}건")
            appendLine("- \"상대만\": 앱과 같이 받은 메시지만 엔진에 넣음 (기본). \"나 포함\": 내 메시지도 넣음")
            appendLine("- 일반 대화 중 \"나\"가 정해지지 않은 것(AI-Hub)은 화자마다 한 번씩 \"나\"로 놓고 돌려, 한 번이라도 경고하면 오탐으로 셈")
            appendLine()
            appendLine("## 1. 세 방식 비교")
            appendLine()
            val labeled = first.labeledScams.isNotEmpty()
            if (labeled) {
                appendLine("| 방식 | 보는 메시지 | 송금 전 경고율 | 조기 경고율 | 결심 전 경고율 | 일반 대화 경고 (오탐) | 일반 대화 주의 | 경고가 앞선 상대 메시지 수 (중앙값) | ERDE5 | ERDE10 |")
                appendLine("|---|---|---|---|---|---|---|---|---|---|")
                for (s in summaries) {
                    val n = s.labeledScams.size
                    appendLine("| ${s.method} | ${mode(s.includeUser)} | ${pct(s.beforeTransfer, n)} | ${pct(s.beforeSuggest, n)} | ${pct(s.beforeIntent, n)} | " +
                        "${pct(s.normalWarned, s.normals.size)} | ${pct(s.normalCautionOnly, s.normals.size)} | ${f1(s.medianLead)} | ${f2(s.erde(5))} | ${f2(s.erde(10))} |")
                }
            } else {
                appendLine("금전 지점 라벨이 없는 입력이라 경고까지 갔는지만 셉니다.")
                appendLine()
                appendLine("| 방식 | 보는 메시지 | 사기 경고 | 일반 대화 경고 (오탐) | 일반 대화 주의 |")
                appendLine("|---|---|---|---|---|")
                for (s in summaries) appendLine("| ${s.method} | ${mode(s.includeUser)} | ${pct(s.warnedScams, s.scams.size)} | " +
                    "${pct(s.normalWarned, s.normals.size)} | ${pct(s.normalCautionOnly, s.normals.size)} |")
            }
            appendLine()
            appendLine("## 2. 사례별 결과")
            for (s in summaries) {
                if (s.scams.isEmpty()) continue
                appendLine()
                appendLine("### ${s.method} · ${mode(s.includeUser)}")
                appendLine()
                appendLine("| 사례 | 유형 | 첫 금전 권유 | 결심 전 마감 | 첫 송금 직전 | 첫 주의 | 첫 경고 | 경고 난 방 | 송금 전 | 앞선 상대 메시지 |")
                appendLine("|---|---|---|---|---|---|---|---|---|---|")
                for (c in s.scams) appendLine("| ${c.caseId} | ${c.note} | ${opt(c.points?.firstSuggest)} | ${opt(c.points?.intentDeadline)} | ${opt(c.points?.firstTransferBefore)} | " +
                    "${opt(c.firstCaution)} | ${opt(c.firstWarning)} | ${opt(c.warningRoom)} | ${if (c.points == null) "-" else if (c.beforeTransfer) "O" else "X"} | ${opt(c.leadTransfer)} |")
            }
            appendLine()
            appendLine("## 3. 일반 대화에서 경고·주의가 난 대화 (ID만)")
            for (s in summaries) {
                val hit = s.normals.filter { it.maxLevel > Level.OBSERVE }
                appendLine()
                appendLine("- ${s.method} · ${mode(s.includeUser)}: " + if (hit.isEmpty()) "없음" else
                    hit.joinToString(", ") { "${it.id}(${if (it.maxLevel == Level.WARNING) "경고" else "주의"}, ${it.note})" })
            }
            if (signalScores != null) {
                appendLine()
                appendLine("## 4. 신호 감지 정확도 (행위 감지 층, \"나 포함\" 판, 최종 라벨과 비교)")
                appendLine()
                appendLine("| 신호 | 맞음 | 잘못 붙음 | 놓침 | 정밀도 | 재현율 |")
                appendLine("|---|---|---|---|---|---|")
                for (x in signalScores) appendLine("| ${x.signal.code} ${x.signal.label} | ${x.tp} | ${x.fp} | ${x.fn} | ${f2(x.precision)} | ${f2(x.recall)} |")
                appendLine()
                appendLine("사진만 있는 메시지는 라벨에서는 앞 설명을 따르지만(기준표 v2.1), 행위 감지 층에는 신호가 없으므로 그만큼 놓침으로 셉니다.")
            }
        }

    private fun casesCsv(summaries: List<Summary>) = buildString {
        appendLine("method,mode,case_id,first_suggest,intent_deadline,first_transfer_before,first_caution,first_warning,warning_room,warning_k,before_suggest,before_intent,before_transfer,lead_transfer,counterpart_messages")
        for (s in summaries) for (c in s.scams) appendLine(row(
            s.method, mode(s.includeUser), c.caseId, opt(c.points?.firstSuggest), opt(c.points?.intentDeadline), opt(c.points?.firstTransferBefore),
            opt(c.firstCaution), opt(c.firstWarning), opt(c.warningRoom), opt(c.warningK),
            yn(c.points, c.beforeSuggest), yn(c.points, c.beforeIntent), yn(c.points, c.beforeTransfer), opt(c.leadTransfer), c.counterpartCount,
        ))
    }

    private fun yn(p: MoneyPoints?, v: Boolean) = if (p == null) "-" else if (v) "Y" else "N"

    private fun normalsCsv(summaries: List<Summary>) = buildString {
        appendLine("method,mode,id,note,max_level,perspectives,warned_perspectives")
        for (s in summaries) for (n in s.normals) appendLine(row(s.method, mode(s.includeUser), n.id, n.note, n.maxLevel, n.perspectives, n.warnedPerspectives))
    }

    private fun signalsCsv(xs: List<SignalScore>) = buildString {
        appendLine("signal,tp,fp,fn,precision,recall")
        for (x in xs) appendLine("${x.signal.code},${x.tp},${x.fp},${x.fn},${f2(x.precision)},${f2(x.recall)}")
    }
}
